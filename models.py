import peewee

database = peewee.SqliteDatabase("db.db")


class Guide(peewee.Model):
    name = peewee.CharField(default="Неизвестный гайд")
    text = peewee.CharField()
    essential = peewee.BooleanField()

    class Meta:
        database = database


class User(peewee.Model):
    uid = peewee.IntegerField()
    is_admin = peewee.BooleanField()
    state = peewee.CharField(default="START")

    class Meta:
        database = database


class Job(peewee.Model):
    guide_id = peewee.IntegerField()
    publication_time = peewee.DateTimeField()

    class Meta:
        database = database


database.create_tables([Guide, User, Job])
