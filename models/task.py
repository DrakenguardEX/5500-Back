from mongoengine import Document, StringField, ReferenceField

class Task(Document):
    title = StringField(required=True)
    simple_description = StringField(default="")
    description = StringField(default="")
    team = ReferenceField('Team', null=True)
    owner = ReferenceField('User', null=True)
    

    type = StringField(default="")
    status = StringField(default="")
    priority = StringField(default="")

meta = {'collection': 'tasks'}
