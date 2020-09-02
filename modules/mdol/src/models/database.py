from peewee import Model, PostgresqlDatabase


class Database(Model):
    class Meta:
        database = PostgresqlDatabase(
            host="192.168.12.28",
            user="postgres",
            password="loo98Yt5",
            database="ais_lesoseka",
            port=5432,
        )
