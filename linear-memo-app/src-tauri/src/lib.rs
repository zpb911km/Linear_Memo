use sea_orm::{EntityTrait, Set, ColumnTrait, QueryFilter, DatabaseConnection};
use serde::{Deserialize, Serialize};
use std::sync::Arc;
use tauri::State;
use chrono::NaiveDateTime;

mod database;
mod entities;
mod card_logic;
mod migration;

use database::{init_database, get_database};
use entities::{deck, card, arrangement};
use card_logic::*;

// 设置结构体
#[derive(Serialize, Deserialize, Debug, Clone)]
struct Settings {
    dark_mode: bool,
}

#[derive(Debug, Serialize, Deserialize)]
struct CardWithReview {
    id: i32,
    deck_id: i32,
    front: String,
    back: String,
    last_review: Option<NaiveDateTime>,
    stability: f64,
    review_interval: f64,
    status: bool,
}

impl From<card::Model> for CardWithReview {
    fn from(model: card::Model) -> Self {
        CardWithReview {
            id: model.id,
            deck_id: model.deck_id,
            front: model.front,
            back: model.back,
            last_review: model.last_review,
            stability: model.stability,
            review_interval: model.review_interval,
            status: model.status,
        }
    }
}

// Tauri 命令实现
#[tauri::command]
fn greet(name: &str) -> String {
    format!("Hello, {}! You've been greeted from Rust!", name)
}

// 设置管理命令
#[tauri::command]
fn get_settings() -> Result<Settings, String> {
    // 简化实现，实际应该从文件或数据库读取
    Ok(Settings { dark_mode: false })
}

#[tauri::command]
fn update_settings(_settings: Settings) -> Result<(), String> {
    // 简化实现，实际应该保存到文件或数据库
    Ok(())
}

// 卡组管理命令
#[tauri::command]
async fn create_deck(name: &str, db: State<'_, Arc<DatabaseConnection>>) -> Result<(), String> {
    let new_deck = deck::ActiveModel {
        id: Default::default(),
        name: Set(name.to_string()),
        forget_line: Set(0.4),
        omega: Set(0.9),
        max_delta: Set(365),
    };
    
    let deck_model = deck::Entity::insert(new_deck)
        .exec(db.as_ref())
        .await
        .map_err(|e| e.to_string())?;
    
    // 创建默认安排
    let new_arrangement = arrangement::ActiveModel {
        id: Default::default(),
        deck_id: Set(deck_model.last_insert_id),
        count: Set(10),
    };
    
    arrangement::Entity::insert(new_arrangement)
        .exec(db.as_ref())
        .await
        .map_err(|e| e.to_string())?;
    
    Ok(())
}

#[tauri::command]
async fn update_deck(
    id: i32, 
    name: Option<String>, 
    forget_line: Option<f64>, 
    omega: Option<f64>, 
    max_delta: Option<i32>, 
    arrangement: Option<i32>,
    db: State<'_, Arc<DatabaseConnection>>
) -> Result<(), String> {
    // 更新卡组信息
    let deck_model = deck::Entity::find_by_id(id)
        .one(db.as_ref())
        .await
        .map_err(|e| e.to_string())?
        .ok_or("Deck not found".to_string())?;
    
    let mut deck_active: deck::ActiveModel = deck_model.into();
    
    if let Some(name) = name {
        deck_active.name = Set(name);
    }
    if let Some(forget_line) = forget_line {
        deck_active.forget_line = Set(forget_line);
    }
    if let Some(omega) = omega {
        deck_active.omega = Set(omega);
    }
    if let Some(max_delta) = max_delta {
        deck_active.max_delta = Set(max_delta);
    }
    
    deck::Entity::update(deck_active)
        .exec(db.as_ref())
        .await
        .map_err(|e| e.to_string())?;
    
    // 更新安排
    if let Some(count) = arrangement {
        let arrangement_model = arrangement::Entity::find()
            .filter(arrangement::Column::DeckId.eq(id))
            .one(db.as_ref())
            .await
            .map_err(|e| e.to_string())?
            .ok_or("Arrangement not found".to_string())?;
            
        let mut arrangement_active: arrangement::ActiveModel = arrangement_model.into();
        arrangement_active.count = Set(count);
        
        arrangement::Entity::update(arrangement_active)
            .exec(db.as_ref())
            .await
            .map_err(|e| e.to_string())?;
    }
    
    Ok(())
}

#[tauri::command]
async fn delete_deck(id: i32, db: State<'_, Arc<DatabaseConnection>>) -> Result<(), String> {
    deck::Entity::delete_by_id(id)
        .exec(db.as_ref())
        .await
        .map_err(|e| e.to_string())?;
    
    Ok(())
}

#[tauri::command]
async fn list_decks(db: State<'_, Arc<DatabaseConnection>>) -> Result<Vec<deck::Model>, String> {
    let decks = deck::Entity::find()
        .all(db.as_ref())
        .await
        .map_err(|e| e.to_string())?;
    
    Ok(decks)
}

#[tauri::command]
async fn get_deck_detail(id: i32, db: State<'_, Arc<DatabaseConnection>>) -> Result<DeckDetail, String> {
    // 获取卡组基本信息
    let deck_model = deck::Entity::find_by_id(id)
        .one(db.as_ref())
        .await
        .map_err(|e| e.to_string())?
        .ok_or("Deck not found".to_string())?;
    
    let mut deck_detail: DeckDetail = deck_model.clone().into();
    
    // 获取卡片统计信息
    deck_detail.cards_count = count_cards(db.as_ref(), id).await.map_err(|e| e.to_string())?;
    deck_detail.review_count = count_review_cards(db.as_ref(), id).await.map_err(|e| e.to_string())?;
    deck_detail.remembered_count = count_remembered_cards(db.as_ref(), id).await.map_err(|e| e.to_string())?;
    deck_detail.new_count = count_new_cards(db.as_ref(), id).await.map_err(|e| e.to_string())?;
    deck_detail.overtime_count = count_overtime_cards(db.as_ref(), id).await.map_err(|e| e.to_string())?;
    
    Ok(deck_detail)
}

// 卡片管理命令
#[tauri::command]
async fn create_card(deck_id: i32, front: &str, back: &str, db: State<'_, Arc<DatabaseConnection>>) -> Result<(), String> {
    let new_card = card::ActiveModel {
        id: Default::default(),
        deck_id: Set(deck_id),
        front: Set(front.to_string()),
        back: Set(back.to_string()),
        last_review: Set(None),
        stability: Set(0.4),
        review_interval: Set(1.0),
        status: Set(false),
    };
    
    card::Entity::insert(new_card)
        .exec(db.as_ref())
        .await
        .map_err(|e| e.to_string())?;
    
    Ok(())
}

#[tauri::command]
async fn update_card(id: i32, front: Option<String>, back: Option<String>, db: State<'_, Arc<DatabaseConnection>>) -> Result<(), String> {
    let card_model = card::Entity::find_by_id(id)
        .one(db.as_ref())
        .await
        .map_err(|e| e.to_string())?
        .ok_or("Card not found".to_string())?;
    
    let mut card_active: card::ActiveModel = card_model.into();
    
    if let Some(front) = front {
        card_active.front = Set(front);
    }
    if let Some(back) = back {
        card_active.back = Set(back);
    }
    
    card::Entity::update(card_active)
        .exec(db.as_ref())
        .await
        .map_err(|e| e.to_string())?;
    
    Ok(())
}

#[tauri::command]
async fn delete_card(id: i32, db: State<'_, Arc<DatabaseConnection>>) -> Result<(), String> {
    card::Entity::delete_by_id(id)
        .exec(db.as_ref())
        .await
        .map_err(|e| e.to_string())?;
    
    Ok(())
}

#[tauri::command]
async fn list_cards(deck_id: i32, db: State<'_, Arc<DatabaseConnection>>) -> Result<Vec<CardWithReview>, String> {
    let cards = card::Entity::find()
        .filter(card::Column::DeckId.eq(deck_id))
        .all(db.as_ref())
        .await
        .map_err(|e| e.to_string())?;
    
    Ok(cards.into_iter().map(|c| c.into()).collect())
}

#[tauri::command]
async fn review_card_cmd(id: i32, feedback: f64, db: State<'_, Arc<DatabaseConnection>>) -> Result<(), String> {
    // 获取卡片
    let card_model = card::Entity::find_by_id(id)
        .one(db.as_ref())
        .await
        .map_err(|e| e.to_string())?
        .ok_or("Card not found".to_string())?;
        
    // 获取卡组
    let deck_model = deck::Entity::find_by_id(card_model.deck_id)
        .one(db.as_ref())
        .await
        .map_err(|e| e.to_string())?
        .ok_or("Deck not found".to_string())?;

    // 复习卡片
    let mut card_active: card::ActiveModel = card_model.into();
    card_logic::review_card(db.as_ref(), &mut card_active, feedback, &deck_model)
        .await
        .map_err(|e| e.to_string())?;
    
    // 更新卡片
    card::Entity::update(card_active)
        .exec(db.as_ref())
        .await
        .map_err(|e| e.to_string())?;
    
    Ok(())
}

#[tauri::command]
async fn list_review_cards(deck_id: i32, db: State<'_, Arc<DatabaseConnection>>) -> Result<Vec<CardWithReview>, String> {
    let cards = card::Entity::find()
        .filter(card::Column::DeckId.eq(deck_id))
        .filter(card::Column::Status.eq(false))
        .all(db.as_ref())
        .await
        .map_err(|e| e.to_string())?;
    
    // 过滤出超时的卡片
    let overtime_cards: Vec<CardWithReview> = cards
        .into_iter()
        .filter(|card| is_overtime(card))
        .map(|c| c.into())
        .collect();
    
    Ok(overtime_cards)
}

#[tauri::command]
async fn search_cards(deck_id: i32, keyword: &str, db: State<'_, Arc<DatabaseConnection>>) -> Result<Vec<CardWithReview>, String> {
    let cards = card::Entity::find()
        .filter(card::Column::DeckId.eq(deck_id))
        .filter(
            card::Column::Front.contains(keyword)
                .or(card::Column::Back.contains(keyword))
        )
        .all(db.as_ref())
        .await
        .map_err(|e| e.to_string())?;
    
    Ok(cards.into_iter().map(|c| c.into()).collect())
}

#[tauri::command]
async fn next_card(deck_id: i32, db: State<'_, Arc<DatabaseConnection>>) -> Result<Option<CardWithReview>, String> {
    let cards = card::Entity::find()
        .filter(card::Column::DeckId.eq(deck_id))
        .filter(card::Column::Status.eq(false))
        .all(db.as_ref())
        .await
        .map_err(|e| e.to_string())?;
    
    // 过滤出需要复习的卡片
    let mut overtime_cards: Vec<card::Model> = cards
        .into_iter()
        .filter(|card| is_overtime(card))
        .collect();
    
    // 按超时天数排序
    let deck_model = deck::Entity::find_by_id(deck_id)
        .one(db.as_ref())
        .await
        .map_err(|e| e.to_string())?
        .ok_or("Deck not found".to_string())?;
        
    overtime_cards.sort_by(|a, b| {
        let a_days = overtime_days(a, deck_model.max_delta);
        let b_days = overtime_days(b, deck_model.max_delta);
        b_days.partial_cmp(&a_days).unwrap()
    });
    
    if overtime_cards.is_empty() {
        Ok(None)
    } else {
        // 返回第二个元素或第一个元素（如果只有一个）
        let index = if overtime_cards.len() > 1 { 1 } else { 0 };
        Ok(Some(overtime_cards[index].clone().into()))
    }
}

// 安排管理命令
#[tauri::command]
async fn create_arrangement(deck_id: i32, count: i32, db: State<'_, Arc<DatabaseConnection>>) -> Result<(), String> {
    let new_arrangement = arrangement::ActiveModel {
        id: Default::default(),
        deck_id: Set(deck_id),
        count: Set(count),
    };
    
    arrangement::Entity::insert(new_arrangement)
        .exec(db.as_ref())
        .await
        .map_err(|e| e.to_string())?;
    
    Ok(())
}

#[tauri::command]
async fn update_arrangement(id: i32, count: i32, db: State<'_, Arc<DatabaseConnection>>) -> Result<(), String> {
    let arrangement_model = arrangement::Entity::find_by_id(id)
        .one(db.as_ref())
        .await
        .map_err(|e| e.to_string())?
        .ok_or("Arrangement not found".to_string())?;
    
    let mut arrangement_active: arrangement::ActiveModel = arrangement_model.into();
    arrangement_active.count = Set(count);
    
    arrangement::Entity::update(arrangement_active)
        .exec(db.as_ref())
        .await
        .map_err(|e| e.to_string())?;
    
    Ok(())
}

#[tauri::command]
async fn delete_arrangement(id: i32, db: State<'_, Arc<DatabaseConnection>>) -> Result<(), String> {
    arrangement::Entity::delete_by_id(id)
        .exec(db.as_ref())
        .await
        .map_err(|e| e.to_string())?;
    
    Ok(())
}

#[tauri::command]
async fn list_arrangements(deck_id: i32, db: State<'_, Arc<DatabaseConnection>>) -> Result<arrangement::Model, String> {
    let arrangement_model = arrangement::Entity::find()
        .filter(arrangement::Column::DeckId.eq(deck_id))
        .one(db.as_ref())
        .await
        .map_err(|e| e.to_string())?
        .ok_or("Arrangement not found".to_string())?;
    
    Ok(arrangement_model)
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_opener::init())
        .setup(|_app| {
            tauri::async_runtime::block_on(async {
                // 初始化数据库
                init_database().await.expect("Failed to initialize database");
            });
            Ok(())
        })
        .manage(get_database())
        .invoke_handler(tauri::generate_handler![
            greet,
            // 设置管理
            get_settings,
            update_settings,
            // 卡组管理
            create_deck,
            update_deck,
            delete_deck,
            list_decks,
            get_deck_detail,
            // 卡片管理
            create_card,
            update_card,
            delete_card,
            list_cards,
            review_card_cmd,
            list_review_cards,
            search_cards,
            next_card,
            // 安排管理
            create_arrangement,
            update_arrangement,
            delete_arrangement,
            list_arrangements,
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}