from peewee import Model, PostgresqlDatabase
from ..services.config import Config


class Connection(Model):
    class Meta:
        config = Config()

        database = PostgresqlDatabase(
            host=config.read_setting("dbconnection", "host"),
            user=config.read_setting("dbconnection", "user"),
            password=config.read_setting("dbconnection", "password"),
            database=config.read_setting("dbconnection", "database"),
            port=config.read_setting("dbconnection", "port"),
        )
