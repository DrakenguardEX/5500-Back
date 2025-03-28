from mongoengine import Document, StringField, ReferenceField

class Task(Document):
    title = StringField(required=True)
    simple_description = StringField(default="")
    description = StringField(default="")
    team = ReferenceField('Team', null=True)
    owner = ReferenceField('User', null=True)

    status = StringField()
    type = StringField()
    priority = StringField()

    meta = {'collection': 'tasks'}