use sea_orm::entity::prelude::*;
use serde::{Deserialize, Serialize};

#[derive(Clone, Debug, PartialEq, DeriveEntityModel, Serialize, Deserialize)]
#[sea_orm(table_name = "deck")]
pub struct Model {
    #[sea_orm(primary_key)]
    pub id: i32,
    #[sea_orm(unique)]
    pub name: String,
    pub forget_line: f64,
    pub omega: f64,
    pub max_delta: i32,
}

#[derive(Copy, Clone, Debug, EnumIter, DeriveRelation)]
pub enum Relation {
    #[sea_orm(has_many = "super::card::Entity")]
    Card,
    #[sea_orm(has_one = "super::arrangement::Entity")]
    Arrangement,
}

impl Related<super::card::Entity> for Entity {
    fn to() -> RelationDef {
        Relation::Card.def()
    }
}

impl Related<super::arrangement::Entity> for Entity {
    fn to() -> RelationDef {
        Relation::Arrangement.def()
    }
}

impl ActiveModelBehavior for ActiveModel {}