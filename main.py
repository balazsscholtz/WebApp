import os
import jinja2
import webapp2

template_dir = os.path.join(
    os.path.dirname(__file__),
    "templates"
)
jinja_env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(template_dir),
    autoescape=False
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
        params = {
            "username": "Ninja",
            "input_text": None,
        }
        self.render_template("landing_page.html", params)
    def post(self):
        params = {
            "username": "Ninja",
            "input_text": self.request.get("some_text"),
        }
        self.render_template("landing_page.html", params)

app = webapp2.WSGIApplication([
    webapp2.Route('/', MainHandler),
], debug=True)