use sea_orm::{Database, DatabaseConnection, DbErr, RuntimeErr};
use std::sync::Arc;
use tokio::sync::OnceCell;
use sea_orm_migration::MigratorTrait;

static DATABASE: OnceCell<Arc<DatabaseConnection>> = OnceCell::const_new();

pub async fn init_database() -> Result<(), DbErr> {
    // 检查数据库是否已经初始化
    if DATABASE.get().is_some() {
        return Ok(());
    }
    
    let db_url = "sqlite://linear_memo.db?mode=rwc";
    let db = Database::connect(db_url).await?;
    
    // 运行迁移
    // 注意：这里我们假设迁移模块存在并且可以正常工作
    // 如果迁移失败，我们仍然设置数据库连接，因为应用程序可能仍然可以工作
    if let Err(e) = crate::migration::Migrator::up(&db, None).await {
        eprintln!("Warning: Failed to run migrations: {}", e);
    }
    
    DATABASE.set(Arc::new(db)).map_err(|_| DbErr::Exec(RuntimeErr::Internal("Failed to set database".to_string())))?;
    Ok(())
}

pub fn get_database() -> Arc<DatabaseConnection> {
    DATABASE.get().expect("Database not initialized. Please call init_database() first.").clone()
}