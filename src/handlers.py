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


#################### item handlers ####################

class ItemCategoryHandler(BaseHandler):
    def get(self, **kwargs):
        context = {'category': kwargs['category']}
        self.render_response('category.html', **context)

class ItemListHandler(BaseHandler):
    def get(self):
        context = {'category': 'item list'}
        self.render_response('category.html', **context)



################## misc handlers ####################

class HeroListHandler(BaseHandler):
    def get(self):
        context = {}
        self.render_response('heroes.html', **context)

class FurnitureListHandler(BaseHandler):
    def get(self):
        context = {}
        self.render_response('furniture.html', **context)
        
     
class HomeHandler(BaseHandler):
    def get(self):
        context = {}
        self.render_response('base.html', **context)
