from datetime import datetime, timedelta
from math import log
import os
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import (
    JWTManager,
    create_refresh_token,
    jwt_required,
    create_access_token,
    get_jwt_identity,
)
from sqlalchemy.sql import func, or_
from typing import List
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = "your-super-secret-key-change-in-production"
CORS(app, origins="*")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///linear_memo.db"
db = SQLAlchemy(app)
jwt = JWTManager(app)
DTFormat = r"%Y/%m/%d %H:%M"
app.config["STATIC_FOLDER"] = os.path.join(os.path.dirname(__file__), "dist")


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    password = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    decks = db.relationship(
        "Deck", backref="user", lazy=True, cascade="all, delete-orphan"
    )

    def __init__(self, username: str, password: str, email: str | None = None):
        self.username = username
        self.email = email
        self.password = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password, password)

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Deck(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        default=1,
        nullable=False,
    )
    cards = db.relationship(
        "Card",
        backref="deck",
        lazy=True,
        cascade="all, delete-orphan",
    )
    forget_line = db.Column(db.Float, nullable=False, default=0.4)
    omega = db.Column(db.Float, nullable=False, default=0.9)
    max_delta = db.Column(db.Integer, nullable=False, default=365)
    arrangement = db.relationship(
        "Arrangement",
        backref="deck",
        lazy=True,
        cascade="all, delete-orphan",
    )

    def __init__(self, id: int, name: str, user_id: int):
        self.id = id
        self.name = name
        self.user_id = user_id

    def __str__(self):
        return f"Deck(id={self.id}, name={self.name})"

    def __repr__(self):
        return f"Deck(id={self.id}, name={self.name})"

    def count_cards(self) -> int:
        cards = Card.query.filter_by(deck_id=self.id).all()
        return len(cards)

    def count_overtime_cards(self) -> int:
        current_time_stamp = datetime.now().timestamp()

        # 查询需要复习的卡片数量
        needed_review_cards_length = (
            Card.query.filter_by(deck_id=self.id)
            .filter(Card.last_review.isnot(None))  # type: ignore
            .filter(Card.status.is_(False))  # type: ignore
            .filter(
                or_(
                    current_time_stamp
                    > func.strftime("%s", Card.last_review)
                    + Card.review_interval * 86400,
                    Card.review_interval < 1,  # type: ignore
                )
            )
            .count()
        )

        return min(
            needed_review_cards_length + self.count_new_cards(),
            self.count_cards(),
        )

    def count_new_cards(self) -> int:
        arrangement = Arrangement.query.filter_by(deck_id=self.id).first()
        not_reviewed_cards_count = (
            Card.query.filter_by(deck_id=self.id)
            .filter(Card.last_review.is_(None))  # type: ignore
            .filter(Card.status.is_(False))  # type: ignore
            .count()
        )
        if arrangement is None:
            raise ValueError("Arrangement not found")
        return min(not_reviewed_cards_count, arrangement.count)

    def count_review_cards(self) -> int:
        # cards = Card.query.filter_by(deck_id=self.id).all()
        # return len([card for card in cards if not card.status])
        return (
            Card.query.filter_by(deck_id=self.id)
            .filter(Card.last_review.isnot(None))  # type: ignore
            .filter(Card.status.is_(False))  # type: ignore
            .count()
        )

    def count_remembered_cards(self) -> int:
        # cards = Card.query.filter_by(deck_id=self.id).all()
        # return len([card for card in cards if card.status])
        return (
            Card.query.filter_by(deck_id=self.id)
            .filter(Card.status.is_(True))  # type: ignore
            .count()
        )


class Card(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        default=1,
        nullable=False,
    )
    deck_id = db.Column(db.Integer, db.ForeignKey("deck.id"), nullable=False)
    front = db.Column(db.Text, nullable=False)
    back = db.Column(db.Text, nullable=False)
    last_review = db.Column(db.DateTime, nullable=True)
    history = db.relationship(
        "History", backref="card", lazy=True, cascade="all, delete-orphan"
    )
    stability = db.Column(db.Float, nullable=False, default=0.4)
    review_interval = db.Column(db.Float, nullable=False, default=1)
    status = db.Column(db.Boolean, nullable=False, default=False)

    def __init__(self, deck_id: int, front: str, back: str, user_id: int):
        self.deck_id = deck_id
        self.front = front
        self.back = back
        self.last_review = None
        self.stability = 0.4
        self.review_interval = 1
        self.status = False
        self.user_id = user_id

    def __str__(self):
        return f"Card(id={self.id}, front={self.front}, back={self.back})"

    def __repr__(self):
        return f"Card(id={self.id}, front={self.front}, back={self.back})"

    def overtime_days(self) -> float:
        if self.last_review is None:
            deck = Deck.query.filter_by(id=self.deck_id).first()
            if deck is None:
                raise ValueError("Deck not found")
            return deck.max_delta
        period = datetime.now() - self.last_review
        return period.days - self.review_interval

    def review(self, feedback: float) -> None:
        """
        处理卡片复习反馈，更新记忆状态
        Args:
            feedback: 用户反馈分数，范围[0,100]
        Returns:
            None
        """
        deck: Deck | None = Deck.query.filter_by(id=self.deck_id).first()
        if deck is None:
            raise ValueError("Deck not found")

        # 获取遗忘线、Ω和最大间隔参数
        forget_line = deck.forget_line
        omega = deck.omega
        max_delta = deck.max_delta

        # 处理边界情况
        if abs(feedback - 100) < 1e-10:
            self.status = True  # 永久记忆状态
            self.last_review = datetime.now()
            db.session.commit()
            return

        if abs(feedback - 0) < 1e-10:
            # 重置卡片状态
            self.stability = deck.forget_line
            self.review_interval = 1
            self.last_review = None
            self.status = False

        # 记录历史反馈
        history = History(
            card_id=self.id,
            review_date=datetime.now(),
            stability=feedback / 100,
            user_id=self.user_id
        )
        db.session.add(history)

        # TODO: 处理偏差（简化版，原代码中的线性回归部分）
        bias = 0  # 简化处理，原代码有复杂计算

        # 核心计算
        stability = omega * feedback + (1 - omega) * self.stability * 100
        delta = self.review_interval * log(forget_line + bias) / log(stability / 100)

        # 处理间隔限制
        if delta > max_delta:
            retention = 1  # 高保留状态
        else:
            retention = self.status

        # 处理永久记忆退化情况
        if retention == 1 and delta < max_delta * 0.8:
            retention = 0
            stability = forget_line * 100
            delta = 1

        if self.status and feedback <= forget_line * 100:
            retention = 0
            stability = forget_line * 100
            delta = 1

        # 确保间隔为正
        if delta <= 0:
            delta = -delta + 0.01

        # 判断是否为新卡片
        if self.last_review is None:
            arrangement = Arrangement.query.filter_by(deck_id=self.deck_id).first()
            if arrangement is None:
                raise ValueError("Arrangement not found")
            arrangement.count -= 1  # 已经学习了1个新卡片

        # 更新卡片状态
        self.stability = stability / 100
        self.review_interval = delta
        self.status = bool(retention)
        self.last_review = datetime.now()

        db.session.commit()


class History(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        default=1,
        nullable=False,
    )
    card_id = db.Column(db.Integer, db.ForeignKey("card.id"), nullable=False)
    review_date = db.Column(db.DateTime, nullable=False)
    stability = db.Column(db.Float, nullable=False)

    def __init__(self, card_id: int, review_date: datetime, stability: float, user_id: int):
        self.card_id = card_id
        self.review_date = review_date
        self.stability = stability
        self.user_id = user_id

    def __str__(self):
        return f"History(id={self.id}, card_id={self.card_id}, review_date={self.review_date}, stability={self.stability})"

    def __repr__(self):
        return f"History(id={self.id}, card_id={self.card_id}, review_date={self.review_date}, stability={self.stability})"


class Arrangement(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        default=1,
        nullable=False,
    )
    deck_id = db.Column(db.Integer, db.ForeignKey("deck.id"), nullable=False)
    count = db.Column(db.Integer, nullable=False)

    def __init__(self, deck_id: int, count: int, user_id: int):
        self.deck_id = deck_id
        self.count = count
        self.user_id = user_id

    def __str__(self):
        return f"Arrangement(id={self.id}, deck_id={self.deck_id}, count={self.count})"

    def __repr__(self):
        return f"Arrangement(id={self.id}, deck_id={self.deck_id}, count={self.count})"


def try_init_db():
    with app.app_context():
        try:
            db.create_all()
        except Exception:
            pass


# 用户认证相关API
@app.route("/api/register", methods=["POST"])
def register():
    """用户注册"""
    try:
        data = request.get_json()

        # 验证必需字段
        if not data or not data.get("username") or not data.get("password") or not data.get("code"):
            return jsonify({"error": "用户名和密码都是必需的"}), 400

        username = data["username"].strip()
        password = data["password"]
        email = data.get("email", "").strip() if data.get("email") else None
        code = data["code"].strip()
        now = datetime.now()
        time_parts = [now.hour, now.minute, now.date().day]
        calc_code = lambda x, y, z: f"{int(str(x+y)[:len(str(x+y))])}{z:02}"
        correct_code = calc_code(*time_parts)

        if correct_code != code:
            return jsonify({"error": "请找管理员"}), 400

        # 验证用户名是否已存在
        if User.query.filter_by(username=username).first():
            return jsonify({"error": "用户名已存在"}), 400

        # 验证邮箱是否已存在（如果提供了邮箱）
        if email and User.query.filter_by(email=email).first():
            return jsonify({"error": "邮箱已被注册"}), 400

        # 创建新用户
        user = User(username=username, password=password, email=email)

        db.session.add(user)
        db.session.commit()

        # 创建访问令牌
        access_token = create_access_token(identity=str(user.id))
        refresh_token = create_refresh_token(identity=str(user.id))

        return (
            jsonify(
                {
                    "message": "注册成功",
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "user": user.to_dict(),
                }
            ),
            201,
        )

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"注册失败: {str(e)}"}), 500


@app.route("/api/login", methods=["POST"])
def login():
    """用户登录"""
    data = request.get_json()

    if not data or not data.get("username") or not data.get("password"):
        return jsonify({"error": "用户名和密码都是必需的"}), 400

    username = data["username"].strip()
    password = data["password"]

    # 查找用户（支持用户名或邮箱登录）
    user = User.query.filter(
        (User.username == username) | (User.email == username)
    ).first()

    if not user or not user.check_password(password):
        return jsonify({"error": "用户名或密码错误"}), 401

    # 创建访问令牌
    access_token = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))

    return (
        jsonify(
            {
                "message": "登录成功",
                "access_token": access_token,
                "refresh_token": refresh_token,
                "user": user.to_dict(),
            }
        ),
        200,
    )


@app.route("/api/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    """
    刷新令牌
    """
    user_id = get_jwt_identity()
    access_token = create_access_token(identity=user_id)
    return jsonify(access_token=access_token)

@app.route("/api/user/profile", methods=["GET"])
@jwt_required()
def get_user_profile():
    """获取当前用户信息"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        if not user:
            return jsonify({"error": "用户不存在"}), 404

        return jsonify({"user": user.to_dict()}), 200

    except Exception as e:
        return jsonify({"error": f"获取用户信息失败: {str(e)}"}), 500


# 卡组管理
# 1. 创建卡组
@app.route("/api/decks", methods=["POST"])
@jwt_required()
def create_deck():
    if not request.json:
        return jsonify({"error": "Invalid request"}), 400
    name = request.json.get("name")
    last_deck = Deck.query.order_by(Deck.id.desc()).first() # type: ignore
    if last_deck is None:
        max_deck_id = -1
    else:
        max_deck_id = last_deck.id
    new_deck_id = max_deck_id + 1
    user_id = get_jwt_identity()
    new_deck = Deck(id=new_deck_id, name=name, user_id=user_id)
    new_arrangement = Arrangement(deck_id=new_deck_id, count=10, user_id=user_id)
    db.session.add(new_deck)
    db.session.add(new_arrangement)
    db.session.commit()
    return jsonify({"message": "Deck created"})


# 2. 编辑卡组
@app.route("/api/decks/<int:deck_id>", methods=["PUT"])
@jwt_required()
def edit_deck(deck_id: int):
    """
    编辑卡组信息，可修改名称、遗忘线、Ω、最大间隔参数
    json: {
        "name": str,
        "forget_line": float,
        "omega": float,
        "max_delta": int
    }
    """
    if not request.json:
        return jsonify({"error": "Invalid request"}), 400
    deck = Deck.query.filter_by(id=deck_id).first()
    if deck is None:
        return jsonify({"error": "Deck not found"}), 404
    name = request.json.get("name")
    if name is not None:
        deck.name = name
    forget_line = request.json.get("forget_line")
    if forget_line is not None:
        if forget_line <= 0 or forget_line >= 1:
            return jsonify({"error": "forget_line should be in (0, 1)"}), 400
        deck.forget_line = forget_line
    omega = request.json.get("omega")
    if omega is not None:
        if omega <= 0 or omega >= 1:
            return jsonify({"error": "omega should be in (0, 1)"}), 400
        deck.omega = omega
    max_delta = request.json.get("max_delta")
    if max_delta is not None:
        deck.max_delta = max_delta
    arrangement = request.json.get("arrangement")
    if arrangement is not None:
        current_arrangement = Arrangement.query.filter_by(deck_id=deck_id).first()
        if current_arrangement is None:
            return jsonify({"error": "Arrangement not found"}), 404
        current_arrangement.count = arrangement
    db.session.commit()
    return jsonify({"message": "Deck updated"})


# 3. 删除卡组
@app.route("/api/decks/<int:deck_id>", methods=["DELETE"])
@jwt_required()
def delete_deck(deck_id: int):
    deck = Deck.query.filter_by(id=deck_id).first()
    if deck is None:
        return jsonify({"error": "Deck not found"}), 404
    db.session.delete(deck)
    db.session.commit()
    return jsonify({"message": "Deck deleted"})


# 4. 列出卡组
@app.route("/api/decks", methods=["GET"])
@jwt_required()
def list_decks():
    user_id = get_jwt_identity()
    decks = Deck.query.filter_by(user_id=user_id).all()
    return jsonify(
        [
            {
                "id": deck.id,
                "name": deck.name,
                "forget_line": deck.forget_line,
                "omega": deck.omega,
                "max_delta": deck.max_delta,
            }
            for deck in decks
        ]
    )


# 5. 卡组详情
@app.route("/api/decks/<int:deck_id>", methods=["GET"])
@jwt_required()
def get_deck(deck_id: int):
    deck: Deck | None = Deck.query.filter_by(id=deck_id).first()
    if deck is None:
        return jsonify({"error": "Deck not found"}), 404
    return jsonify(
        {
            "id": deck.id,
            "name": deck.name,
            "forget_line": deck.forget_line,
            "omega": deck.omega,
            "max_delta": deck.max_delta,
            "cards_count": deck.count_cards(),
            "new_count": min(deck.count_new_cards(), deck.count_overtime_cards()),
            "overtime_count": deck.count_overtime_cards(),
            "review_count": deck.count_review_cards(),
            "remembered_count": deck.count_remembered_cards(),
        }
    )


# 卡片管理
# 1. 创建卡片
@app.route("/api/cards", methods=["POST"])
@jwt_required()
def create_card():
    """
    创建卡片，需要指定卡组id、正反面文字
    json: {
        "deck_id": int,
        "front": str,
        "back": str,
    }
    """
    if not request.json:
        return jsonify({"error": "Invalid request"}), 400
    deck_id = request.json.get("deck_id")
    front = request.json.get("front")
    back = request.json.get("back")
    if deck_id is None or front is None or back is None:
        return jsonify({"error": "deck_id, front and back are required"}), 400
    user_id = get_jwt_identity()
    new_card = Card(deck_id=deck_id, front=front, back=back, user_id=user_id)
    db.session.add(new_card)
    db.session.commit()
    return jsonify({"message": "Card created"})


# 2. 编辑卡片
@app.route("/api/cards/<int:card_id>", methods=["PUT"])
@jwt_required()
def edit_card(card_id: int):
    """
    编辑卡片信息，可修改卡片正反面
    json: {
        "front": str,
        "back": str,
    }
    """
    if not request.json:
        return jsonify({"error": "Invalid request"}), 400
    card = Card.query.filter_by(id=card_id).first()
    if card is None:
        return jsonify({"error": "Card not found"}), 404
    front = request.json.get("front")
    if front is not None:
        card.front = front
    back = request.json.get("back")
    if back is not None:
        card.back = back
    db.session.commit()
    print(card, "updated")
    return jsonify({"message": "Card updated"})


# 3. 删除卡片
@app.route("/api/cards/<int:card_id>", methods=["DELETE"])
@jwt_required()
def delete_card(card_id: int):
    card = Card.query.filter_by(id=card_id).first()
    if card is None:
        return jsonify({"error": "Card not found"}), 404
    db.session.delete(card)
    db.session.commit()
    return jsonify({"message": "Card deleted"})


# 4. 列出卡组的卡片
@app.route("/api/cards", methods=["GET"])
@jwt_required()
def list_cards():
    deck_id = request.args.get("deck_id")
    if deck_id is not None:
        cards = Card.query.filter_by(deck_id=deck_id).all()
    else:
        return jsonify({"error": "deck_id is required"}), 400
    return jsonify(
        [{"id": card.id, "front": card.front, "back": card.back} for card in cards]
    )


# 5. 复习卡片
@app.route("/api/cards/<int:card_id>/review", methods=["POST"])
@jwt_required()
def review_card(card_id: int):
    """
    复习卡片，需要提供用户反馈分数
    json: {
        "feedback": float,
    }
    """
    if not request.json:
        return jsonify({"error": "Invalid request"}), 400
    feedback = request.json.get("feedback")
    if feedback is None:
        return jsonify({"error": "feedback is required"}), 400
    feedback = float(feedback)
    if feedback < 0 or feedback > 100:
        return jsonify({"error": "feedback should be in [0, 100]"}), 400
    card: Card | None = Card.query.filter_by(id=card_id).first()
    if card is None:
        return jsonify({"error": "Card not found"}), 404
    try:
        card.review(feedback)
    except ValueError as e:
        return (
            jsonify({"error": "Error occurred when reviewing card: " + str(e)}),
            400,
        )
    return jsonify({"message": "Card reviewed"})


# 6. 列出卡组的待复习卡片
@app.route("/api/cards/review", methods=["GET"])
@jwt_required()
def list_review_cards():
    """
    列出待复习卡片，指定卡组id
    """
    deck_id = request.args.get("deck_id")
    if deck_id is None:
        return jsonify({"error": "deck_id is required"}), 400
    current_time_stamp = func.strftime("%s", func.now())
    overtime_cards = (
        Card.query.filter_by(deck_id=deck_id)
        .filter(Card.last_review.isnot(None))  # type: ignore
        .filter(
            or_(
                current_time_stamp
                > func.strftime("%s", Card.last_review) + Card.review_interval * 86400,
                Card.review_interval < 1,  # type: ignore
            )
        )
        .all()
    )
    return jsonify(
        [
            {"id": card.id, "front": card.front, "back": card.back}
            for card in overtime_cards
        ]
    )


# 7. 搜索卡组的卡片
@app.route("/api/cards/search", methods=["GET"])
@jwt_required()
def search_cards():
    """
    搜索卡组的卡片，指定卡组id和关键字
    """
    deck_id = request.args.get("deck_id")
    keyword = request.args.get("keyword")
    if deck_id is None or keyword is None:
        return jsonify({"error": "deck_id and keyword are required"}), 400
    cards = []
    cards = (
        Card.query.filter_by(deck_id=deck_id)
        .filter(
            Card.front.ilike(  # pyright: ignore[reportAttributeAccessIssue]
                f"%{keyword}%"
            )
            | Card.back.ilike(  # pyright: ignore[reportAttributeAccessIssue]
                f"%{keyword}%"
            )
        )
        .all()
    )
    return jsonify(
        [{"id": card.id, "front": card.front, "back": card.back} for card in cards]
    )


# 8. 返回当前最需要复习的卡片
@app.route("/api/next_card", methods=["GET"])
@jwt_required()
def next_card():
    """
    返回当前最需要复习的卡片，指定卡组id
    """
    deck_id = request.args.get("deck_id")
    if deck_id is None:
        return jsonify({"error": "deck_id is required"}), 400
    deck: Deck | None = Deck.query.filter_by(id=deck_id).first()
    if deck is None:
        return jsonify({"error": "Deck not found"}), 404
    arrangement: Arrangement | None = Arrangement.query.filter_by(
        deck_id=deck_id
    ).first()
    if arrangement is None:
        return jsonify({"error": "Arrangement not found"}), 404
    current_time_stamp = datetime.now().timestamp()
    arrangement_count = arrangement.count
    cards = (
        Card.query.filter_by(deck_id=deck_id)
        .filter_by(status=False)
        .filter(
            or_(
                current_time_stamp
                > func.strftime("%s", Card.last_review) + Card.review_interval * 86400,
                arrangement_count > 0,
                Card.review_interval < 1,  # type: ignore
            )
        )
        .order_by(
            func.strftime("%s", Card.last_review)
            + Card.review_interval * 86400
            - current_time_stamp
        )
    ).all()
    if len(cards) == 0:
        return jsonify({"message": "No cards to review"}), 204
    index = 1 if len(cards) > 1 else 0
    return jsonify(
        {
            "id": cards[index].id,
            "deck_id": cards[index].deck_id,
            "front": cards[index].front,
            "back": cards[index].back,
        }
    )


# 9. 整合
@app.route("/api/review_and_next_card", methods=["POST"])
@jwt_required()
def review_and_next_card():
    """
    复习卡片并返回当前最需要复习的卡片，指定卡组id
    """
    deck_id = request.args.get("deck_id")
    card_id = request.args.get("card_id")
    feedback = request.args.get("feedback")
    if deck_id is None or card_id is None or feedback is None:
        return jsonify({"error": "deck_id, card_id and feedback are required"}), 400
    deck: Deck | None = Deck.query.filter_by(id=deck_id).first()
    if deck is None:
        return jsonify({"error": "Deck not found"}), 404
    card: Card | None = Card.query.filter_by(id=card_id).first()
    if card is None:
        return jsonify({"error": "Card not found"}), 404
    feedback = float(feedback)
    if feedback < 0 or feedback > 100:
        return jsonify({"error": "feedback should be in [0, 100]"}), 400
    arrangement = Arrangement.query.filter_by(deck_id=deck_id).first()
    if arrangement is None:
        return jsonify({"error": "Arrangement not found"}), 404
    try:
        card.review(feedback)
    except ValueError as e:
        return (
            jsonify({"error": "Error occurred when reviewing card: " + str(e)}),
            400,
        )
    overtime_count = deck.count_overtime_cards()
    current_time_stamp = datetime.now().timestamp()
    arrangement_count = arrangement.count
    cards: List[Card] = (
        Card.query.filter_by(deck_id=deck_id)
        .filter_by(status=False)
        .filter(
            or_(
                current_time_stamp
                > func.strftime("%s", Card.last_review) + Card.review_interval * 86400,
                arrangement_count > 0,
                Card.review_interval < 1,  # type: ignore
            )
        )
        .order_by(
            func.strftime("%s", Card.last_review)
            + Card.review_interval * 86400
            - current_time_stamp
        )
    ).all()
    if len(cards) == 0:
        return jsonify({"message": "No cards to review"}), 204
    for c in cards:
        if c.id != int(card_id):
            card = c
            break
    else:
        return jsonify({"message": "No cards to review"}), 204
    return jsonify(
        {
            "card": {
                "id": card.id,
                "deck_id": card.deck_id,
                "front": card.front,
                "back": card.back,
                # "last_review": card.last_review,
                # "stability": card.stability,
                # "review_interval": card.review_interval,
                # "status": card.status,
            },
            "overtime_count": overtime_count,
        }
    )


# 安排管理
# 1. 创建安排
@app.route("/api/arrangements", methods=["POST"])
@jwt_required()
def create_arrangement():
    """
    创建安排，指定卡组id, 数量
    json: {
        "deck_id": int,
        "count": int,
    }
    """
    if not request.json:
        return jsonify({"error": "Invalid request"}), 400
    deck_id = request.json.get("deck_id")
    count = request.json.get("count")
    if count is None:
        return jsonify({"error": "count is required"}), 400
    user_id = get_jwt_identity()
    arrangement = Arrangement(deck_id=deck_id, count=count, user_id=user_id)
    db.session.add(arrangement)
    db.session.commit()
    return jsonify({"message": "Arrangement created"})


# 2. 编辑安排
@app.route("/api/arrangements/<int:arrangement_id>", methods=["PUT"])
@jwt_required()
def edit_arrangement(arrangement_id: int):
    """
    编辑安排，可修改日期和卡片数量
    json: {
        "count": int,
    }
    """
    if not request.json:
        return jsonify({"error": "Invalid request"}), 400
    arrangement = Arrangement.query.filter_by(id=arrangement_id).first()
    if arrangement is None:
        return jsonify({"error": "Arrangement not found"}), 404
    count = request.json.get("count")
    if count is not None:
        arrangement.count = count
    db.session.commit()
    return jsonify({"message": "Arrangement updated"})


# 3. 删除安排
@app.route("/api/arrangements/<int:arrangement_id>", methods=["DELETE"])
@jwt_required()
def delete_arrangement(arrangement_id: int):
    arrangement = Arrangement.query.filter_by(id=arrangement_id).first()
    if arrangement is None:
        return jsonify({"error": "Arrangement not found"}), 404
    db.session.delete(arrangement)
    db.session.commit()
    return jsonify({"message": "Arrangement deleted"})


# 4. 列出卡组的安排
@app.route("/api/arrangements", methods=["GET"])
@jwt_required()
def list_arrangements():
    deck_id = request.args.get("deck_id")
    if deck_id is not None:
        arrangement: Arrangement | None = Arrangement.query.filter_by(
            deck_id=deck_id
        ).first()
    else:
        return jsonify({"error": "deck_id is required"}), 400
    if arrangement is None:
        return jsonify({"error": "Arrangement not found"}), 404
    return jsonify({"id": arrangement.id, "count": arrangement.count})


# 静态文件
@app.route("/<path:path>")
def static_file(path):
    return send_from_directory(app.config["STATIC_FOLDER"], path)


@app.route("/")
def index():
    return send_from_directory(app.config["STATIC_FOLDER"], "index.html")


@app.errorhandler(404)
def handle_404(e):
    return """
    <h1>404 Not Found</h1>
    <p>The resource could not be found.</p>
    <a href="/">Go back</a>
    """


if __name__ == "__main__":
    try_init_db()
    app.run(host="0.0.0.0", port=65533, debug=True)
