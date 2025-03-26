from mongoengine import Document, StringField, ListField, ReferenceField
from .user import User
from .task import Task

class Team(Document):
    name = StringField(required=True)
    members = ListField(ReferenceField(User))
    tasks = ListField(ReferenceField(Task))

    meta = {'collection': 'teams'}