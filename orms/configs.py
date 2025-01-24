from peewee import (
    Model,
    SqliteDatabase,
    IntegerField,
)

from os import path

database = SqliteDatabase(
    path.join("database", "configs.db")
)  # Połączenie z bazą danych


class BaseModel(Model):
    class Meta:
        database = database


class GuildConfigs(BaseModel):
    guild_id = IntegerField(primary_key=True, null=False, unique=True)
    events_channel_id = IntegerField(null=True)
    logging_channel_id = IntegerField(null=True)

    class Meta:
        table_name = "GuildConfigs"
        without_rowid = True
