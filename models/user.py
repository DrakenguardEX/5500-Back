from mongoengine import Document, StringField, ListField, ReferenceField


class User(Document):
    username = StringField(required=True, unique=True)
    password = StringField(required=True)
    teams = ListField(ReferenceField('Team'))
    personal_tasks = ListField(ReferenceField('Task'))

    meta = {'collection': 'users'}