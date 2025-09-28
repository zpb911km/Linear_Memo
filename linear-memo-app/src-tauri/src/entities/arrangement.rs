use sea_orm::entity::prelude::*;
use serde::{Deserialize, Serialize};

#[derive(Clone, Debug, PartialEq, DeriveEntityModel, Serialize, Deserialize)]
#[sea_orm(table_name = "arrangement")]
pub struct Model {
    #[sea_orm(primary_key)]
    pub id: i32,
    #[sea_orm(unique)]
    pub deck_id: i32,
    pub count: i32,
}

#[derive(Copy, Clone, Debug, EnumIter, DeriveRelation)]
pub enum Relation {
    #[sea_orm(
        belongs_to = "super::deck::Entity",
        from = "Column::DeckId",
        to = "super::deck::Column::Id"
    )]
    Deck,
}

impl Related<super::deck::Entity> for Entity {
    fn to() -> RelationDef {
        Relation::Deck.def()
    }
}

impl ActiveModelBehavior for ActiveModel {}