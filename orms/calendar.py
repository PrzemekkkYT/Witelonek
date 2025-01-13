from peewee import (
    Model,
    SqliteDatabase,
    AutoField,
    TextField,
    IntegerField,
    DateField,
    TimeField,
)
from os import path

database = SqliteDatabase(
    path.join("database", "calendar.db")
)  # Połączenie z bazą danych


class BaseModel(Model):
    class Meta:
        database = database


class Event(BaseModel):
    id = AutoField()  # Auto-incrementujące pole ID
    title = TextField()  # Nazwa wydarzenia (wymagane)
    message = TextField(null=True)  # Wiadomość (opcjonalnie)
    event_type = TextField()  # Typ wydarzenia (wymagane)
    role_id = IntegerField(null=True)  # ID roli (opcjonalnie)
    date = DateField()  # Data wydarzenia (wymagane)
    time = TimeField(null=True)  # Czas wydarzenia (opcjonalnie)
    guild_id = IntegerField()  # ID serwera (wymagane)
    location = TextField(null=True)  # Lokalizacja (opcjonalnie)

    class Meta:
        table_name = "events"  # Nazwa tabeli w bazie
