from peewee import Model, PostgresqlDatabase
from ..services.config import Settings


class Database(Model):
    class Meta:
        database = PostgresqlDatabase(
            host=Settings(group="Database", key="host").read_setting(),
            user=Settings(group="Database", key="user").read_setting(),
            password=Settings(group="Database", key="password").read_setting(),
            database=Settings(group="Database", key="database").read_setting(),
            port=Settings(group="Database", key="port").read_setting(),
        )
