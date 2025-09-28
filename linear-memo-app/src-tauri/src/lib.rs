// Learn more about Tauri commands at https://tauri.app/develop/calling-rust/
use std::sync::Mutex;
use std::fs;
use serde::{Deserialize, Serialize};
use rusqlite::{Connection, Result as SqlResult, params};

// 设置结构体
#[derive(Serialize, Deserialize, Debug)]
struct Settings {
    dark_mode: bool,
}

// 数据库连接池
struct Database {
    conn: Mutex<Connection>,
}

impl Database {
    fn new() -> SqlResult<Self> {
        let conn = Connection::open("linear_memo.db")?;
        // 初始化数据库表
        Self::init_tables(&conn)?;
        Ok(Database {
            conn: Mutex::new(conn),
        })
    }

    fn init_tables(conn: &Connection) -> SqlResult<()> {
        // 创建卡组表
        conn.execute(
            "CREATE TABLE IF NOT EXISTS deck (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                forget_line REAL NOT NULL DEFAULT 0.4,
                omega REAL NOT NULL DEFAULT 0.9,
                max_delta INTEGER NOT NULL DEFAULT 365
            )",
            [],
        )?;

        // 创建卡片表
        conn.execute(
            "CREATE TABLE IF NOT EXISTS card (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                deck_id INTEGER NOT NULL,
                front TEXT NOT NULL,
                back TEXT NOT NULL,
                last_review DATETIME,
                stability REAL NOT NULL DEFAULT 0.4,
                review_interval REAL NOT NULL DEFAULT 1.0,
                status BOOLEAN NOT NULL DEFAULT FALSE,
                FOREIGN KEY (deck_id) REFERENCES deck (id) ON DELETE CASCADE
            )",
            [],
        )?;

        // 创建复习历史表
        conn.execute(
            "CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                card_id INTEGER NOT NULL,
                review_date DATETIME NOT NULL,
                stability REAL NOT NULL,
                FOREIGN KEY (card_id) REFERENCES card (id) ON DELETE CASCADE
            )",
            [],
        )?;

        // 创建安排表
        conn.execute(
            "CREATE TABLE IF NOT EXISTS arrangement (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                deck_id INTEGER NOT NULL UNIQUE,
                count INTEGER NOT NULL,
                FOREIGN KEY (deck_id) REFERENCES deck (id) ON DELETE CASCADE
            )",
            [],
        )?;

        Ok(())
    }
}

// 全局数据库实例
static DATABASE: once_cell::sync::OnceCell<Database> = once_cell::sync::OnceCell::new();

fn init_database() -> SqlResult<()> {
    let db = Database::new()?;
    DATABASE.set(db).map_err(|_| rusqlite::Error::ExecuteReturnedResults)?;
    Ok(())
}

// 读取设置
fn read_settings() -> Settings {
    let settings_content = fs::read_to_string("settings.json").unwrap_or_else(|_| "{}".to_string());
    serde_json::from_str(&settings_content).unwrap_or(Settings { dark_mode: false })
}

// 保存设置
fn save_settings(settings: &Settings) -> Result<(), String> {
    let settings_content = serde_json::to_string_pretty(settings).map_err(|e| e.to_string())?;
    fs::write("settings.json", settings_content).map_err(|e| e.to_string())?;
    Ok(())
}

// 获取数据库连接
fn get_database() -> &'static Database {
    DATABASE.get().expect("Database not initialized")
}

// 数据模型定义
#[derive(Debug, serde::Serialize)]
struct Deck {
    id: i32,
    name: String,
    forget_line: f64,
    omega: f64,
    max_delta: i32,
}

#[derive(Debug, serde::Serialize)]
struct DeckDetail {
    id: i32,
    name: String,
    forget_line: f64,
    omega: f64,
    max_delta: i32,
    cards_count: i32,
    new_count: i32,
    overtime_count: i32,
    review_count: i32,
    remembered_count: i32,
}

#[derive(Debug, serde::Serialize, serde::Deserialize)]
struct Card {
    id: Option<i32>,
    deck_id: i32,
    front: String,
    back: String,
    last_review: Option<String>,
    stability: f64,
    review_interval: f64,
    status: bool,
}

#[derive(Debug, serde::Serialize)]
struct History {
    id: i32,
    card_id: i32,
    review_date: String,
    stability: f64,
}

#[derive(Debug, serde::Serialize, serde::Deserialize)]
struct Arrangement {
    id: Option<i32>,
    deck_id: i32,
    count: i32,
}

// Tauri 命令实现
#[tauri::command]
fn greet(name: &str) -> String {
    format!("Hello, {}! You've been greeted from Rust!", name)
}

// 设置管理命令
#[tauri::command]
fn get_settings() -> Result<Settings, String> {
    Ok(read_settings())
}

#[tauri::command]
fn update_settings(settings: Settings) -> Result<(), String> {
    save_settings(&settings)
}

// 卡组管理命令
#[tauri::command]
fn create_deck(name: &str) -> Result<(), String> {
    let db = get_database();
    let conn = db.conn.lock().unwrap();
    
    conn.execute(
        "INSERT INTO deck (name) VALUES (?1)",
        [name],
    ).map_err(|e| e.to_string())?;
    
    // 创建默认安排
    let deck_id: i32 = conn.last_insert_rowid() as i32;
    conn.execute(
        "INSERT INTO arrangement (deck_id, count) VALUES (?1, 10)",
        [deck_id],
    ).map_err(|e| e.to_string())?;
    
    Ok(())
}

#[tauri::command]
fn update_deck(id: i32, name: Option<String>, forget_line: Option<f64>, omega: Option<f64>, max_delta: Option<i32>, arrangement: Option<i32>) -> Result<(), String> {
    let db = get_database();
    let conn = db.conn.lock().unwrap();
    
    // 更新卡组信息
    if let (Some(name), Some(forget_line), Some(omega), Some(max_delta)) = (name, forget_line, omega, max_delta) {
        conn.execute(
            "UPDATE deck SET name = ?1, forget_line = ?2, omega = ?3, max_delta = ?4 WHERE id = ?5",
            [name, forget_line.to_string(), omega.to_string(), max_delta.to_string(), id.to_string()],
        ).map_err(|e| e.to_string())?;
    }
    
    // 更新安排
    if let Some(count) = arrangement {
        conn.execute(
            "UPDATE arrangement SET count = ?1 WHERE deck_id = ?2",
            [count.to_string(), id.to_string()],
        ).map_err(|e| e.to_string())?;
    }
    
    Ok(())
}

#[tauri::command]
fn delete_deck(id: i32) -> Result<(), String> {
    let db = get_database();
    let conn = db.conn.lock().unwrap();
    
    conn.execute(
        "DELETE FROM deck WHERE id = ?1",
        [id],
    ).map_err(|e| e.to_string())?;
    
    Ok(())
}

#[tauri::command]
fn list_decks() -> Result<Vec<Deck>, String> {
    let db = get_database();
    let conn = db.conn.lock().unwrap();
    
    let mut stmt = conn.prepare(
        "SELECT id, name, forget_line, omega, max_delta FROM deck"
    ).map_err(|e| e.to_string())?;
    
    let decks = stmt.query_map([], |row| {
        Ok(Deck {
            id: row.get(0)?,
            name: row.get(1)?,
            forget_line: row.get(2)?,
            omega: row.get(3)?,
            max_delta: row.get(4)?,
        })
    }).map_err(|e| e.to_string())?;
    
    let mut result = Vec::new();
    for deck in decks {
        result.push(deck.map_err(|e| e.to_string())?);
    }
    
    Ok(result)
}

#[tauri::command]
fn get_deck_detail(id: i32) -> Result<DeckDetail, String> {
    let db = get_database();
    let conn = db.conn.lock().unwrap();
    
    // 获取卡组基本信息
    let mut stmt = conn.prepare(
        "SELECT id, name, forget_line, omega, max_delta FROM deck WHERE id = ?1"
    ).map_err(|e| e.to_string())?;
    
    let mut rows = stmt.query(params![id]).map_err(|e| e.to_string())?;
    let deck = if let Some(row) = rows.next().map_err(|e| e.to_string())? {
        Deck {
            id: row.get(0).map_err(|e| e.to_string())?,
            name: row.get(1).map_err(|e| e.to_string())?,
            forget_line: row.get(2).map_err(|e| e.to_string())?,
            omega: row.get(3).map_err(|e| e.to_string())?,
            max_delta: row.get(4).map_err(|e| e.to_string())?,
        }
    } else {
        return Err("Deck not found".to_string());
    };
    
    // 获取卡片统计信息
    let cards_count: i32 = conn.query_row(
        "SELECT COUNT(*) FROM card WHERE deck_id = ?1",
        params![id],
        |row| row.get(0)
    ).map_err(|e| e.to_string())?;
    
    let review_count: i32 = conn.query_row(
        "SELECT COUNT(*) FROM card WHERE deck_id = ?1 AND status = 0",
        params![id],
        |row| row.get(0)
    ).map_err(|e| e.to_string())?;
    
    let remembered_count: i32 = conn.query_row(
        "SELECT COUNT(*) FROM card WHERE deck_id = ?1 AND status = 1",
        params![id],
        |row| row.get(0)
    ).map_err(|e| e.to_string())?;
    
    // 获取安排信息（新卡片数量）
    let new_count: i32 = conn.query_row(
        "SELECT count FROM arrangement WHERE deck_id = ?1",
        params![id],
        |row| row.get(0)
    ).unwrap_or(0);
    
    // 计算超时卡片数量
    // 这里简化处理，假设所有未记住的卡片都是超时的
    let overtime_count = review_count;
    
    Ok(DeckDetail {
        id: deck.id,
        name: deck.name,
        forget_line: deck.forget_line,
        omega: deck.omega,
        max_delta: deck.max_delta,
        cards_count,
        new_count,
        overtime_count,
        review_count,
        remembered_count,
    })
}

// 卡片管理命令
#[tauri::command]
fn create_card(deck_id: i32, front: &str, back: &str) -> Result<(), String> {
    let db = get_database();
    let conn = db.conn.lock().unwrap();
    
    conn.execute(
        "INSERT INTO card (deck_id, front, back) VALUES (?1, ?2, ?3)",
        [deck_id.to_string(), front.to_string(), back.to_string()],
    ).map_err(|e| e.to_string())?;
    
    Ok(())
}

#[tauri::command]
fn update_card(id: i32, front: Option<String>, back: Option<String>) -> Result<(), String> {
    let db = get_database();
    let conn = db.conn.lock().unwrap();
    
    if let (Some(front), Some(back)) = (front, back) {
        conn.execute(
            "UPDATE card SET front = ?1, back = ?2 WHERE id = ?3",
            [front, back, id.to_string()],
        ).map_err(|e| e.to_string())?;
    }
    
    Ok(())
}

#[tauri::command]
fn delete_card(id: i32) -> Result<(), String> {
    let db = get_database();
    let conn = db.conn.lock().unwrap();
    
    conn.execute(
        "DELETE FROM card WHERE id = ?1",
        [id],
    ).map_err(|e| e.to_string())?;
    
    Ok(())
}

#[tauri::command]
fn list_cards(deck_id: i32) -> Result<Vec<Card>, String> {
    let db = get_database();
    let conn = db.conn.lock().unwrap();
    
    let mut stmt = conn.prepare(
        "SELECT id, deck_id, front, back, last_review, stability, review_interval, status FROM card WHERE deck_id = ?1"
    ).map_err(|e| e.to_string())?;
    
    let cards = stmt.query_map([deck_id], |row| {
        Ok(Card {
            id: row.get(0)?,
            deck_id: row.get(1)?,
            front: row.get(2)?,
            back: row.get(3)?,
            last_review: row.get(4)?,
            stability: row.get(5)?,
            review_interval: row.get(6)?,
            status: row.get(7)?,
        })
    }).map_err(|e| e.to_string())?;
    
    let mut result = Vec::new();
    for card in cards {
        result.push(card.map_err(|e| e.to_string())?);
    }
    
    Ok(result)
}

#[tauri::command]
fn review_card(id: i32, feedback: f64) -> Result<(), String> {
    // TODO: 实现完整的复习逻辑
    // 这里简化处理，只更新卡片状态
    let db = get_database();
    let conn = db.conn.lock().unwrap();
    
    conn.execute(
        "UPDATE card SET last_review = datetime('now'), status = ?1 WHERE id = ?2",
        [if feedback > 80.0 { 1 } else { 0 }.to_string(), id.to_string()],
    ).map_err(|e| e.to_string())?;
    
    // 记录历史
    conn.execute(
        "INSERT INTO history (card_id, review_date, stability) VALUES (?1, datetime('now'), ?2)",
        [id.to_string(), feedback.to_string()],
    ).map_err(|e| e.to_string())?;
    
    Ok(())
}

#[tauri::command]
fn list_review_cards(deck_id: i32) -> Result<Vec<Card>, String> {
    let db = get_database();
    let conn = db.conn.lock().unwrap();
    
    // 简化实现：返回所有未记住的卡片
    let mut stmt = conn.prepare(
        "SELECT id, deck_id, front, back, last_review, stability, review_interval, status 
         FROM card 
         WHERE deck_id = ?1 AND status = 0"
    ).map_err(|e| e.to_string())?;
    
    let cards = stmt.query_map([deck_id], |row| {
        Ok(Card {
            id: row.get(0)?,
            deck_id: row.get(1)?,
            front: row.get(2)?,
            back: row.get(3)?,
            last_review: row.get(4)?,
            stability: row.get(5)?,
            review_interval: row.get(6)?,
            status: row.get(7)?,
        })
    }).map_err(|e| e.to_string())?;
    
    let mut result = Vec::new();
    for card in cards {
        result.push(card.map_err(|e| e.to_string())?);
    }
    
    Ok(result)
}

#[tauri::command]
fn search_cards(deck_id: i32, keyword: &str) -> Result<Vec<Card>, String> {
    let db = get_database();
    let conn = db.conn.lock().unwrap();
    
    let mut stmt = conn.prepare(
        "SELECT id, deck_id, front, back, last_review, stability, review_interval, status 
         FROM card 
         WHERE deck_id = ?1 AND (front LIKE ?2 OR back LIKE ?2)"
    ).map_err(|e| e.to_string())?;
    
    let keyword_pattern = format!("%{}%", keyword);
    let cards = stmt.query_map(params![deck_id, keyword_pattern], |row| {
        Ok(Card {
            id: row.get(0)?,
            deck_id: row.get(1)?,
            front: row.get(2)?,
            back: row.get(3)?,
            last_review: row.get(4)?,
            stability: row.get(5)?,
            review_interval: row.get(6)?,
            status: row.get(7)?,
        })
    }).map_err(|e| e.to_string())?;
    
    let mut result = Vec::new();
    for card in cards {
        result.push(card.map_err(|e| e.to_string())?);
    }
    
    Ok(result)
}

#[tauri::command]
fn next_card(deck_id: i32) -> Result<Option<Card>, String> {
    let db = get_database();
    let conn = db.conn.lock().unwrap();
    
    // 简化实现：返回第一个需要复习的卡片
    let mut stmt = conn.prepare(
        "SELECT id, deck_id, front, back, last_review, stability, review_interval, status 
         FROM card 
         WHERE deck_id = ?1 AND status = 0 
         LIMIT 1"
    ).map_err(|e| e.to_string())?;
    
    let mut rows = stmt.query([deck_id]).map_err(|e| e.to_string())?;
    if let Some(row) = rows.next().map_err(|e| e.to_string())? {
        Ok(Some(Card {
            id: row.get(0).map_err(|e| e.to_string())?,
            deck_id: row.get(1).map_err(|e| e.to_string())?,
            front: row.get(2).map_err(|e| e.to_string())?,
            back: row.get(3).map_err(|e| e.to_string())?,
            last_review: row.get(4).map_err(|e| e.to_string())?,
            stability: row.get(5).map_err(|e| e.to_string())?,
            review_interval: row.get(6).map_err(|e| e.to_string())?,
            status: row.get(7).map_err(|e| e.to_string())?,
        }))
    } else {
        Ok(None)
    }
}

// 安排管理命令
#[tauri::command]
fn create_arrangement(deck_id: i32, count: i32) -> Result<(), String> {
    let db = get_database();
    let conn = db.conn.lock().unwrap();
    
    conn.execute(
        "INSERT INTO arrangement (deck_id, count) VALUES (?1, ?2)",
        [deck_id.to_string(), count.to_string()],
    ).map_err(|e| e.to_string())?;
    
    Ok(())
}

#[tauri::command]
fn update_arrangement(id: i32, count: i32) -> Result<(), String> {
    let db = get_database();
    let conn = db.conn.lock().unwrap();
    
    conn.execute(
        "UPDATE arrangement SET count = ?1 WHERE id = ?2",
        [count.to_string(), id.to_string()],
    ).map_err(|e| e.to_string())?;
    
    Ok(())
}

#[tauri::command]
fn delete_arrangement(id: i32) -> Result<(), String> {
    let db = get_database();
    let conn = db.conn.lock().unwrap();
    
    conn.execute(
        "DELETE FROM arrangement WHERE id = ?1",
        [id],
    ).map_err(|e| e.to_string())?;
    
    Ok(())
}

#[tauri::command]
fn list_arrangements(deck_id: i32) -> Result<Arrangement, String> {
    let db = get_database();
    let conn = db.conn.lock().unwrap();
    
    let mut stmt = conn.prepare(
        "SELECT id, deck_id, count FROM arrangement WHERE deck_id = ?1"
    ).map_err(|e| e.to_string())?;
    
    let mut rows = stmt.query([deck_id]).map_err(|e| e.to_string())?;
    if let Some(row) = rows.next().map_err(|e| e.to_string())? {
        Ok(Arrangement {
            id: row.get(0).map_err(|e| e.to_string())?,
            deck_id: row.get(1).map_err(|e| e.to_string())?,
            count: row.get(2).map_err(|e| e.to_string())?,
        })
    } else {
        Err("Arrangement not found".to_string())
    }
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    // 初始化数据库
    init_database().expect("Failed to initialize database");
    
    tauri::Builder::default()
        .plugin(tauri_plugin_opener::init())
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
            review_card,
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