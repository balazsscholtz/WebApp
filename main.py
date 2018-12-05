import os
import jinja2
import webapp2
import datetime
import json
from models import Message
from google.appengine.ext import ndb
from google.appengine.api import users


template_dir = os.path.join(
    os.path.dirname(__file__),
    "templates"
)
jinja_env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(template_dir),
    autoescape=True
)

class BaseHandler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

    def render_template(self, view_filename, params=None):
        if not params:
            params = {}
        template = jinja_env.get_template(view_filename)
        self.response.out.write(template.render(params))

class MainHandler(BaseHandler):
    def get(self):
        user = users.get_current_user()
        params = {"user": user,}
        if user:
            logout_url = users.create_logout_url('/')
            params["logout_url"] = logout_url
        else:
            login_url = users.create_login_url('/')
            params["login_url"] = login_url
        self.render_template("landing_page.html", params)
    def post(self):
        user = users.get_current_user()
        params = {"user": user,}
        if user:
            logout_url = users.create_logout_url('/')
            params["logout_url"] = logout_url
            input_text = self.request.get("some_text")
            msg = Message(message_text=input_text, user=user.user_id())
            msg.put()
            params["input_text"] = input_text
        else:
            login_url = users.create_login_url('/')
            params["login_url"] = login_url
        self.render_template("landing_page.html", params)

class ListHandler(BaseHandler):
    def get(self):
        user = users.get_current_user()
        params = {"user": user,}
        if user:
            logout_url = users.create_logout_url('/')
            params["logout_url"] = logout_url
            messages = Message.query(
                ndb.AND(
                    Message.deleted == False,
                    Message.user == user.user_id(),
                )
            ).order(Message.created).fetch()
            params["message_list"] = messages
        else:
            login_url = users.create_login_url('/list')
            params["login_url"] = login_url
        self.render_template("message_list.html", params)

class MessageDetailsHandler(BaseHandler):
    def get(self, message_id):
        message = Message.get_by_id(int(message_id))
        params = {"message": message}
        self.render_template("message_details.html", params)

class MessageEditHandler(BaseHandler):
    def get(self, message_id):
        message = Message.get_by_id(int(message_id))
        params = {"message": message}
        self.render_template("message_edit.html", params)
    def post(self, message_id):
        message = Message.get_by_id(int(message_id))
        message.message_text = self.request.get("message_text")
        message.modified = datetime.datetime.now()
        message.put()
        self.redirect("/message/%s" % message_id)

class MessageDeleteHandler(BaseHandler):
    def get(self, message_id):
        message = Message.get_by_id(int(message_id))
        params = {"message": message}
        self.render_template("message_delete.html", params)
    def post(self, message_id):
        message = Message.get_by_id(int(message_id))
        #message.key.delete()
        message.modified = datetime.datetime.now()
        message.deleted = True
        message.put()
        self.redirect("/list")

class SearchHandler(BaseHandler):
    def post(self):
        user =users.get_current_user()
        if user:
            search_text = self.request.get("search_text")
            messages = Message.query(
                ndb.AND(
                    Message.deleted == False,
                    Message.message_text == search_text,
                    Message.user == user.user_id(),
                )
            ).order(Message.created).fetch()
            params = {"message_list": messages, 'user': user}
            self.render_template("message_list.html", params)
        else:
            self.redirect("/list")

class APIHandler(webapp2.RequestHandler):
    def get(self):
        messages = Message.query()
        message2json = {"api_version": "1,0", "messages": []}
        for message in messages:
            m = {}
            m["text"] = message.message_text
            m["create_date"] = message.created.strftime("%Y. %B %d. %H:%M:%S")
            m["last_midified_date"] = message.modified.strftime("%Y. %B %d. %H:%M:%S")
            m["is_deleted"] = message.deleted
            m["user_id"] = message.user
            message2json["messages"].append(m)
        return self.response.write(json.dumps(message2json, indent=4))

app = webapp2.WSGIApplication([
    webapp2.Route('/', MainHandler),
    webapp2.Route('/list', ListHandler),
    webapp2.Route('/message/<message_id:\d+>', MessageDetailsHandler),
    webapp2.Route('/message/<message_id:\d+>/edit', MessageEditHandler),
    webapp2.Route('/message/<message_id:\d+>/delete', MessageDeleteHandler),
    webapp2.Route('/search', SearchHandler),
    webapp2.Route('/api', APIHandler)
], debug=True)