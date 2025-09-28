use sea_orm::{Database, DatabaseConnection, DbErr, RuntimeErr};
use std::sync::Arc;
use tokio::sync::OnceCell;
use crate::migration::Migrator;
use sea_orm_migration::MigratorTrait;

static DATABASE: OnceCell<Arc<DatabaseConnection>> = OnceCell::const_new();

pub async fn init_database() -> Result<(), DbErr> {
    let db_url = "sqlite://linear_memo.db?mode=rwc";
    let db = Database::connect(db_url).await?;
    
    // Run migrations
    Migrator::up(&db, None).await?;
    
    DATABASE.set(Arc::new(db)).map_err(|_| DbErr::Exec(RuntimeErr::Internal("Failed to set database".to_string())))?;
    Ok(())
}

pub fn get_database() -> Arc<DatabaseConnection> {
    DATABASE.get().expect("Database not initialized").clone()
}