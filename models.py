from google.appengine.ext import ndb

class Message(ndb.Model):
    message_text = ndb.StringProperty(indexed=True)
    created = ndb.DateTimeProperty(auto_now_add=True, indexed=True)
    modified = ndb.DateTimeProperty(auto_now_add=True, indexed=True)
    deleted = ndb.BooleanProperty(default=False, indexed=True)
    user = ndb.StringProperty(indexed=True)
