use sea_orm::entity::prelude::*;
use serde::{Deserialize, Serialize};

#[derive(Clone, Debug, PartialEq, DeriveEntityModel, Serialize, Deserialize)]
#[sea_orm(table_name = "card")]
pub struct Model {
    #[sea_orm(primary_key)]
    pub id: i32,
    #[sea_orm(indexed)]
    pub deck_id: i32,
    pub front: String,
    pub back: String,
    pub last_review: Option<DateTime>,
    pub stability: f64,
    pub review_interval: f64,
    pub status: bool,
}

#[derive(Copy, Clone, Debug, EnumIter, DeriveRelation)]
pub enum Relation {
    #[sea_orm(
        belongs_to = "super::deck::Entity",
        from = "Column::DeckId",
        to = "super::deck::Column::Id"
    )]
    Deck,
    #[sea_orm(has_many = "super::history::Entity")]
    History,
}

impl Related<super::deck::Entity> for Entity {
    fn to() -> RelationDef {
        Relation::Deck.def()
    }
}

impl Related<super::history::Entity> for Entity {
    fn to() -> RelationDef {
        Relation::History.def()
    }
}

impl ActiveModelBehavior for ActiveModel {}