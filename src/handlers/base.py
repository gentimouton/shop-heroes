import webapp2
from webapp2_extras import jinja2


class BaseHandler(webapp2.RequestHandler):
    """
    Cache a jinja2 template renderer in the app context
    http://webapp-improved.appspot.com/api/webapp2_extras/jinja2.html#webapp2_extras.jinja2.Jinja2
    """

    @webapp2.cached_property
    def jinja2(self):
        # Returns a Jinja2 renderer cached in the app registry.
        return jinja2.get_jinja2(app=self.app)

    def render_response(self, _template, **context):
        # Renders a template and writes the result to the response.
        # templates are at /templates by default, cf http://stackoverflow.com/a/32435965
        rv = self.jinja2.render_template(_template, **context)
        self.response.write(rv)

