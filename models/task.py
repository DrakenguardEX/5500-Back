from mongoengine import Document, StringField, ReferenceField, DateField  # ✅ 新增：DateField

class Task(Document):
    title = StringField(required=True)
    simple_description = StringField(default="")
    description = StringField(default="")
    team = ReferenceField('Team', null=True)
    owner = ReferenceField('User', null=True)

    type = StringField(default="")
    status = StringField(default="")
    priority = StringField(default="")

    cycle = StringField(default="")            
    dueDate = DateField(required=False, null=True)  

    meta = {'collection': 'tasks'}