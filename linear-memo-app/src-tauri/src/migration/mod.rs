use sea_orm_migration::prelude::*;

pub struct Migrator;

#[async_trait::async_trait]
impl sea_orm_migration::MigratorTrait for Migrator {
    fn migrations() -> Vec<Box<dyn sea_orm_migration::MigrationTrait>> {
        vec![Box::new(m000001_create_tables::Migration)]
    }
}

mod m000001_create_tables;