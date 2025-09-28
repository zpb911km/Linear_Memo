use crate::entities::{card, deck, history, arrangement};
use sea_orm::{EntityTrait, Set, ColumnTrait, QueryFilter, DatabaseConnection, PaginatorTrait};
use chrono::Utc;

#[derive(Debug, serde::Serialize)]
pub struct DeckDetail {
    pub id: i32,
    pub name: String,
    pub forget_line: f64,
    pub omega: f64,
    pub max_delta: i32,
    pub cards_count: i32,
    pub new_count: i32,
    pub overtime_count: i32,
    pub review_count: i32,
    pub remembered_count: i32,
}

impl From<deck::Model> for DeckDetail {
    fn from(model: deck::Model) -> Self {
        DeckDetail {
            id: model.id,
            name: model.name,
            forget_line: model.forget_line,
            omega: model.omega,
            max_delta: model.max_delta,
            cards_count: 0,
            new_count: 0,
            overtime_count: 0,
            review_count: 0,
            remembered_count: 0,
        }
    }
}

pub async fn count_cards(db: &DatabaseConnection, deck_id: i32) -> Result<i32, sea_orm::DbErr> {
    card::Entity::find()
        .filter(card::Column::DeckId.eq(deck_id))
        .count(db)
        .await
        .map(|c| c as i32)
}

pub async fn count_review_cards(db: &DatabaseConnection, deck_id: i32) -> Result<i32, sea_orm::DbErr> {
    card::Entity::find()
        .filter(card::Column::DeckId.eq(deck_id))
        .filter(card::Column::Status.eq(false))
        .count(db)
        .await
        .map(|c| c as i32)
}

pub async fn count_remembered_cards(db: &DatabaseConnection, deck_id: i32) -> Result<i32, sea_orm::DbErr> {
    card::Entity::find()
        .filter(card::Column::DeckId.eq(deck_id))
        .filter(card::Column::Status.eq(true))
        .count(db)
        .await
        .map(|c| c as i32)
}

pub async fn count_new_cards(db: &DatabaseConnection, deck_id: i32) -> Result<i32, sea_orm::DbErr> {
    let arrangement = arrangement::Entity::find()
        .filter(arrangement::Column::DeckId.eq(deck_id))
        .one(db)
        .await?;
    
    Ok(arrangement.map(|a| a.count).unwrap_or(0))
}

pub async fn count_overtime_cards(db: &DatabaseConnection, deck_id: i32) -> Result<i32, sea_orm::DbErr> {
    let cards = card::Entity::find()
        .filter(card::Column::DeckId.eq(deck_id))
        .all(db)
        .await?;
    
    let arrangement = arrangement::Entity::find()
        .filter(arrangement::Column::DeckId.eq(deck_id))
        .one(db)
        .await?
        .ok_or_else(|| sea_orm::DbErr::RecordNotFound("Arrangement not found".to_string()))?;
    
    let overtime_cards_count = cards.iter()
        .filter(|card| is_needed_review(card))
        .count() as i32;
    
    Ok(std::cmp::min(overtime_cards_count + arrangement.count, cards.len() as i32))
}

pub fn is_overtime(card: &card::Model) -> bool {
    // 1. 处理last_review为None的情况（新卡片）
    if card.last_review.is_none() {
        // 这里我们不直接访问arrangement，因为这应该在调用函数中处理
        return true;
    }

    // 2. 检查是否未到复习时间
    let last_review = card.last_review.unwrap();
    let period = Utc::now().naive_utc() - last_review;
    let days = period.num_seconds() as f64 / 86400.0;
    
    if days < card.review_interval && card.review_interval > 1.0 {
        return false;
    }

    // 3. 其他情况都需要复习
    true
}

pub fn is_needed_review(card: &card::Model) -> bool {
    // 1. 处理last_review为None的情况（新卡片）
    if card.last_review.is_none() {
        return false;
    }
    
    // 2. 检查是否未到复习时间
    let last_review = card.last_review.unwrap();
    let period = Utc::now().naive_utc() - last_review;
    let days = period.num_seconds() as f64 / 86400.0;
    
    if days < card.review_interval && card.review_interval > 1.0 {
        return false;
    }
    
    // 3. 其他情况都需要复习
    true
}

pub fn overtime_days(card: &card::Model, max_delta: i32) -> f64 {
    if card.last_review.is_none() {
        return max_delta as f64;
    }
    
    let last_review = card.last_review.unwrap();
    let period = Utc::now().naive_utc() - last_review;
    let days = period.num_seconds() as f64 / 86400.0;
    days - card.review_interval
}

pub async fn review_card(db: &DatabaseConnection, card: &mut card::ActiveModel, feedback: f64, deck: &deck::Model) -> Result<(), sea_orm::DbErr> {
    // 获取遗忘线、Ω和最大间隔参数
    let forget_line = deck.forget_line;
    let omega = deck.omega;
    let max_delta = deck.max_delta;

    // 处理边界情况
    if (feedback - 100.0).abs() < 1e-10 {
        card.status = Set(true); // 永久记忆状态
    }

    if (feedback - 0.0).abs() < 1e-10 {
        // 重置卡片状态
        card.stability = Set(0.4);
        card.review_interval = Set(1.0);
        card.status = Set(false);
        card.last_review = Set(None);
    }

    // 记录历史反馈
    let history = history::ActiveModel {
        id: Default::default(),
        card_id: Set(card.id.clone().unwrap()),
        review_date: Set(Utc::now().naive_utc()),
        stability: Set(feedback / 100.0),
    };
    
    history::Entity::insert(history).exec(db).await?;

    // TODO: 处理偏差（简化版，原代码中的线性回归部分）
    let bias = 0.0; // 简化处理，原代码有复杂计算

    // 核心计算
    let stability = omega * feedback + (1.0 - omega) * card.stability.as_ref() * 100.0;
    let delta = card.review_interval.as_ref() * ((forget_line + bias).ln() / (stability / 100.0).ln());

    // 处理间隔限制
    let retention = if delta > max_delta as f64 {
        1 // 高保留状态
    } else {
        *card.status.as_ref() as i32
    };

    // 处理永久记忆退化情况
    let (retention, stability, delta) = if retention == 1 && delta < (max_delta as f64) * 0.8 {
        (0, forget_line * 100.0, 1.0)
    } else if *card.status.as_ref() && feedback <= forget_line * 100.0 {
        (0, forget_line * 100.0, 1.0)
    } else {
        (retention, stability, delta)
    };

    // 确保间隔为正
    let delta = if delta <= 0.0 {
        -delta + 0.01
    } else {
        delta
    };

    // 判断是否为新卡片
    let is_new_card = card.last_review.as_ref().is_none();
    
    if is_new_card {
        let arrangement_model = arrangement::Entity::find()
            .filter(arrangement::Column::DeckId.eq(*card.deck_id.as_ref()))
            .one(db)
            .await?
            .ok_or_else(|| sea_orm::DbErr::RecordNotFound("Arrangement not found".to_string()))?;
            
        let mut arrangement_active: arrangement::ActiveModel = arrangement_model.into();
        arrangement_active.count = Set(std::cmp::max(0, arrangement_active.count.as_ref() - 1));
        arrangement::Entity::update(arrangement_active).exec(db).await?;
    }

    // 更新卡片状态
    card.stability = Set(stability / 100.0);
    card.review_interval = Set(delta);
    card.status = Set(retention != 0);
    card.last_review = Set(Some(Utc::now().naive_utc()));

    Ok(())
}