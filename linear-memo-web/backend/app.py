from datetime import datetime, timedelta
from math import log
from random import randint
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from typing import List


app = Flask(__name__)
CORS(app, origins=["http://localhost:5173"])
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///linear_memo.db"
db = SQLAlchemy(app)
DTFormat = r"%Y/%m/%d %H:%M"


class Deck(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
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

    def __str__(self):
        return f"Deck(id={self.id}, name={self.name})"

    def __repr__(self):
        return f"Deck(id={self.id}, name={self.name})"

    def count_cards(self) -> int:
        cards = Card.query.filter_by(deck_id=self.id).all()
        return len(cards)

    def count_overtime_cards(self) -> int:
        cards = Card.query.filter_by(deck_id=self.id).all()
        return len([card for card in cards if card.is_overtime()])

    def count_new_cards(self) -> int:
        arrangement = Arrangement.query.filter_by(deck_id=self.id).first()
        if arrangement is None:
            raise ValueError("Arrangement not found")
        return arrangement.count

    def count_review_cards(self) -> int:
        cards = Card.query.filter_by(deck_id=self.id).all()
        return len([card for card in cards if not card.status])

    def count_remembered_cards(self) -> int:
        cards = Card.query.filter_by(deck_id=self.id).all()
        return len([card for card in cards if card.status])


class Card(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
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

    def __init__(self, deck_id: int, front: str, back: str):
        self.deck_id = deck_id
        self.front = front
        self.back = back
        self.last_review = None
        self.stability = 0.4
        self.review_interval = 1
        self.status = False

    def __str__(self):
        return f"Card(id={self.id}, front={self.front}, back={self.back})"

    def __repr__(self):
        return f"Card(id={self.id}, front={self.front}, back={self.back})"

    def is_overtime(self) -> bool:
        # 1. 处理last_review为None的情况（新卡片）
        if self.last_review is None:
            arrangement = Arrangement.query.filter_by(
                deck_id=self.deck_id
            ).first()
            if arrangement is None:
                raise ValueError("Arrangement not found")
            if arrangement.count == 0:
                return False
            return True

        # 2. 检查是否未到复习时间
        period = datetime.now() - self.last_review
        if (
            period.total_seconds() / 86400 < self.review_interval
            and self.review_interval > 1  # 1天以下的卡片不算记得
        ):
            return False

        # 3. 其他情况都需要复习
        return True

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
        deck = Deck.query.filter_by(id=self.deck_id).first()
        if deck is None:
            raise ValueError("Deck not found")

        # 获取遗忘线、Ω和最大间隔参数
        forget_line = deck.forget_line
        omega = deck.omega
        max_delta = deck.max_delta

        # 处理边界情况
        if abs(feedback - 100) < 1e-10:
            self.status = True  # 永久记忆状态

        if abs(feedback - 0) < 1e-10:
            # 重置卡片状态
            self = Card(self.deck_id, self.front, self.back)

        # 记录历史反馈
        history = History(
            card_id=self.id,
            review_date=datetime.now(),
            stability=feedback / 100,
        )
        db.session.add(history)

        # TODO: 处理偏差（简化版，原代码中的线性回归部分）
        bias = 0  # 简化处理，原代码有复杂计算

        # 核心计算
        stability = omega * feedback + (1 - omega) * self.stability * 100
        delta = (
            self.review_interval
            * log(forget_line + bias)
            / log(stability / 100)
        )

        # 处理间隔限制
        if delta > max_delta:
            retention = 1  # 高保留状态
        else:
            retention = self.status

        # 处理永久记忆退化情况
        if retention == 1 and delta < max_delta * 0.8:
            retention = 0
            stability = 40
            delta = 1

        if self.status and feedback <= 40:
            retention = 0
            stability = 40
            delta = 1

        # 确保间隔为正
        if delta <= 0:
            delta = -delta + 0.01

        # 判断是否为新卡片
        if self.last_review is None:
            arrangement = Arrangement.query.filter_by(
                deck_id=self.deck_id
            ).first()
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
    card_id = db.Column(db.Integer, db.ForeignKey("card.id"), nullable=False)
    review_date = db.Column(db.DateTime, nullable=False)
    stability = db.Column(db.Float, nullable=False)

    def __str__(self):
        return f"History(id={self.id}, card_id={self.card_id}, review_date={self.review_date}, stability={self.stability})"

    def __repr__(self):
        return f"History(id={self.id}, card_id={self.card_id}, review_date={self.review_date}, stability={self.stability})"


class Arrangement(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    deck_id = db.Column(db.Integer, db.ForeignKey("deck.id"), nullable=False)
    count = db.Column(db.Integer, nullable=False)

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


# 卡组管理
# 1. 创建卡组
@app.route("/decks", methods=["POST"])
def create_deck():
    if not request.json:
        return jsonify({"error": "Invalid request"}), 400
    name = request.json.get("name")
    max_deck_id = Deck.query.order_by(Deck.id.desc()).first().id
    new_deck_id = max_deck_id + 1
    new_deck = Deck(id=new_deck_id, name=name)
    new_arrangement = Arrangement(deck_id=new_deck_id, count=10)
    db.session.add(new_deck)
    db.session.add(new_arrangement)
    db.session.commit()
    return jsonify({"message": "Deck created"})


# 2. 编辑卡组
@app.route("/decks/<int:deck_id>", methods=["PUT"])
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
        current_arrangement = Arrangement.query.filter_by(
            deck_id=deck_id
        ).first()
        if current_arrangement is None:
            return jsonify({"error": "Arrangement not found"}), 404
        current_arrangement.count = arrangement
    db.session.commit()
    return jsonify({"message": "Deck updated"})


# 3. 删除卡组
@app.route("/decks/<int:deck_id>", methods=["DELETE"])
def delete_deck(deck_id: int):
    deck = Deck.query.filter_by(id=deck_id).first()
    if deck is None:
        return jsonify({"error": "Deck not found"}), 404
    db.session.delete(deck)
    db.session.commit()
    return jsonify({"message": "Deck deleted"})


# 4. 列出卡组
@app.route("/decks", methods=["GET"])
def list_decks():
    decks = Deck.query.all()
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
@app.route("/decks/<int:deck_id>", methods=["GET"])
def get_deck(deck_id: int):
    deck = Deck.query.filter_by(id=deck_id).first()
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
            "new_count": min(
                deck.count_new_cards(), deck.count_overtime_cards()
            ),
            "overtime_count": deck.count_overtime_cards(),
            "review_count": deck.count_review_cards(),
            "remembered_count": deck.count_remembered_cards(),
        }
    )


# 卡片管理
# 1. 创建卡片
@app.route("/cards", methods=["POST"])
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
    new_card = Card(deck_id=deck_id, front=front, back=back)
    db.session.add(new_card)
    db.session.commit()
    return jsonify({"message": "Card created"})


# 2. 编辑卡片
@app.route("/cards/<int:card_id>", methods=["PUT"])
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
@app.route("/cards/<int:card_id>", methods=["DELETE"])
def delete_card(card_id: int):
    card = Card.query.filter_by(id=card_id).first()
    if card is None:
        return jsonify({"error": "Card not found"}), 404
    db.session.delete(card)
    db.session.commit()
    return jsonify({"message": "Card deleted"})


# 4. 列出卡组的卡片
@app.route("/cards", methods=["GET"])
def list_cards():
    deck_id = request.args.get("deck_id")
    if deck_id is not None:
        cards = Card.query.filter_by(deck_id=deck_id).all()
    else:
        return jsonify({"error": "deck_id is required"}), 400
    return jsonify(
        [
            {"id": card.id, "front": card.front, "back": card.back}
            for card in cards
        ]
    )


# 5. 复习卡片
@app.route("/cards/<int:card_id>/review", methods=["POST"])
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
    card: Card = Card.query.filter_by(id=card_id).first()
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
@app.route("/cards/review", methods=["GET"])
def list_review_cards():
    """
    列出待复习卡片，指定卡组id
    """
    deck_id = request.args.get("deck_id")
    if deck_id is not None:
        cards = (
            Card.query.filter_by(deck_id=deck_id).filter_by(status=False).all()
        )
    else:
        return jsonify({"error": "deck_id is required"}), 400
    return jsonify(
        [
            {"id": card.id, "front": card.front, "back": card.back}
            for card in cards
            if card.is_overtime()
        ]
    )


# 7. 搜索卡组的卡片
@app.route("/cards/search", methods=["GET"])
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
        [
            {"id": card.id, "front": card.front, "back": card.back}
            for card in cards
        ]
    )


# 8. 返回当前最需要复习的卡片
@app.route("/next_card", methods=["GET"])
def next_card():
    """
    返回当前最需要复习的卡片，指定卡组id
    """
    deck_id = request.args.get("deck_id")
    if deck_id is None:
        return jsonify({"error": "deck_id is required"}), 400
    deck = Deck.query.filter_by(id=deck_id).first()
    if deck is None:
        return jsonify({"error": "Deck not found"}), 404
    cards: List[Card] = (
        Card.query.filter_by(deck_id=deck_id).filter_by(status=False).all()
    )
    cards = list(
        filter(
            lambda c: c.is_overtime(),
            cards,
        )
    )
    cards.sort(
        key=lambda c: c.overtime_days(),
        reverse=True,
    )
    if len(cards) == 0:
        return jsonify({"message": "No cards to review"}), 204
    # print(cards[0].front)
    return jsonify(
        {
            "id": cards[0].id,
            "deck_id": cards[0].deck_id,
            "front": cards[0].front,
            "back": cards[0].back,
        }
    )


# 安排管理
# 1. 创建安排
@app.route("/arrangements", methods=["POST"])
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
    arrangement = Arrangement(deck_id=deck_id, count=count)
    db.session.add(arrangement)
    db.session.commit()
    return jsonify({"message": "Arrangement created"})


# 2. 编辑安排
@app.route("/arrangements/<int:arrangement_id>", methods=["PUT"])
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
@app.route("/arrangements/<int:arrangement_id>", methods=["DELETE"])
def delete_arrangement(arrangement_id: int):
    arrangement = Arrangement.query.filter_by(id=arrangement_id).first()
    if arrangement is None:
        return jsonify({"error": "Arrangement not found"}), 404
    db.session.delete(arrangement)
    db.session.commit()
    return jsonify({"message": "Arrangement deleted"})


# 4. 列出卡组的安排
@app.route("/arrangements", methods=["GET"])
def list_arrangements():
    deck_id = request.args.get("deck_id")
    if deck_id is not None:
        arrangement = Arrangement.query.filter_by(deck_id=deck_id).first()
    else:
        return jsonify({"error": "deck_id is required"}), 400
    return jsonify({"id": arrangement.id, "count": arrangement.count})


if __name__ == "__main__":
    try_init_db()
    app.run(debug=True)
