use sea_orm_migration::prelude::*;

#[derive(DeriveMigrationName)]
pub struct Migration;

#[async_trait::async_trait]
impl MigrationTrait for Migration {
    async fn up(&self, manager: &SchemaManager) -> Result<(), DbErr> {
        // Create deck table
        manager
            .create_table(
                Table::create()
                    .table(Deck::Table)
                    .if_not_exists()
                    .col(
                        ColumnDef::new(Deck::Id)
                            .integer()
                            .not_null()
                            .auto_increment()
                            .primary_key(),
                    )
                    .col(ColumnDef::new(Deck::Name).string().not_null().unique_key())
                    .col(ColumnDef::new(Deck::ForgetLine).double().not_null().default(0.4))
                    .col(ColumnDef::new(Deck::Omega).double().not_null().default(0.9))
                    .col(ColumnDef::new(Deck::MaxDelta).integer().not_null().default(365))
                    .to_owned(),
            )
            .await?;

        // Create card table
        manager
            .create_table(
                Table::create()
                    .table(Card::Table)
                    .if_not_exists()
                    .col(
                        ColumnDef::new(Card::Id)
                            .integer()
                            .not_null()
                            .auto_increment()
                            .primary_key(),
                    )
                    .col(ColumnDef::new(Card::DeckId).integer().not_null())
                    .col(ColumnDef::new(Card::Front).text().not_null())
                    .col(ColumnDef::new(Card::Back).text().not_null())
                    .col(ColumnDef::new(Card::LastReview).date_time().null())
                    .col(ColumnDef::new(Card::Stability).double().not_null().default(0.4))
                    .col(ColumnDef::new(Card::ReviewInterval).double().not_null().default(1.0))
                    .col(ColumnDef::new(Card::Status).boolean().not_null().default(false))
                    .foreign_key(
                        ForeignKey::create()
                            .name("fk-card-deck_id")
                            .from(Card::Table, Card::DeckId)
                            .to(Deck::Table, Deck::Id)
                            .on_delete(ForeignKeyAction::Cascade)
                            .on_update(ForeignKeyAction::Cascade),
                    )
                    .to_owned(),
            )
            .await?;

        // Create history table
        manager
            .create_table(
                Table::create()
                    .table(History::Table)
                    .if_not_exists()
                    .col(
                        ColumnDef::new(History::Id)
                            .integer()
                            .not_null()
                            .auto_increment()
                            .primary_key(),
                    )
                    .col(ColumnDef::new(History::CardId).integer().not_null())
                    .col(ColumnDef::new(History::ReviewDate).date_time().not_null())
                    .col(ColumnDef::new(History::Stability).double().not_null())
                    .foreign_key(
                        ForeignKey::create()
                            .name("fk-history-card_id")
                            .from(History::Table, History::CardId)
                            .to(Card::Table, Card::Id)
                            .on_delete(ForeignKeyAction::Cascade)
                            .on_update(ForeignKeyAction::Cascade),
                    )
                    .to_owned(),
            )
            .await?;

        // Create arrangement table
        manager
            .create_table(
                Table::create()
                    .table(Arrangement::Table)
                    .if_not_exists()
                    .col(
                        ColumnDef::new(Arrangement::Id)
                            .integer()
                            .not_null()
                            .auto_increment()
                            .primary_key(),
                    )
                    .col(ColumnDef::new(Arrangement::DeckId).integer().not_null().unique_key())
                    .col(ColumnDef::new(Arrangement::Count).integer().not_null())
                    .foreign_key(
                        ForeignKey::create()
                            .name("fk-arrangement-deck_id")
                            .from(Arrangement::Table, Arrangement::DeckId)
                            .to(Deck::Table, Deck::Id)
                            .on_delete(ForeignKeyAction::Cascade)
                            .on_update(ForeignKeyAction::Cascade),
                    )
                    .to_owned(),
            )
            .await?;

        Ok(())
    }

    async fn down(&self, manager: &SchemaManager) -> Result<(), DbErr> {
        // Drop tables in reverse order
        manager
            .drop_table(Table::drop().table(Arrangement::Table).to_owned())
            .await?;
        manager
            .drop_table(Table::drop().table(History::Table).to_owned())
            .await?;
        manager
            .drop_table(Table::drop().table(Card::Table).to_owned())
            .await?;
        manager
            .drop_table(Table::drop().table(Deck::Table).to_owned())
            .await?;

        Ok(())
    }
}

#[derive(Iden)]
enum Deck {
    Table,
    Id,
    Name,
    ForgetLine,
    Omega,
    MaxDelta,
}

#[derive(Iden)]
enum Card {
    Table,
    Id,
    DeckId,
    Front,
    Back,
    LastReview,
    Stability,
    ReviewInterval,
    Status,
}

#[derive(Iden)]
enum History {
    Table,
    Id,
    CardId,
    ReviewDate,
    Stability,
}

#[derive(Iden)]
enum Arrangement {
    Table,
    Id,
    DeckId,
    Count,
}