import logging
import sys
import traceback
from collections import defaultdict
import webapp2
from webapp2_extras import jinja2

from db.db_categories import categories_db
from db.db_items import item_db


# prevent template lines to leave blank lines
jinja2.default_config['environment_args']['trim_blocks'] = True

# search terms for the search box
search_terms = [{'slug': s, 'name': d['name']} for s, d in item_db.items()] 

# item categories for the navbar links
def get_cat_links():
    # return {'Weapons': [{'slug':'swords', 'name':'Swords'}], 'Garments': []}
    cat_links = defaultdict(list)  
    for cat_slug, cat_data in categories_db.items():
        cat = {k: cat_data[k] for k in ['name', 'slot']}
        cat['slug'] = cat_slug
        cat_links[cat_data['meta_category']].append(cat)
    # sort each meta-category by slot, then alphabetically
    [l.sort(key=lambda x: (x['slot'], x['name'])) for l in cat_links.values()]
    return dict(cat_links)
item_cat_links = get_cat_links()


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
        # add list of names to context for search box autocompletion
        context['search_terms'] = search_terms
        context['item_cat_links'] = item_cat_links
        rv = self.jinja2.render_template(_template, **context)
        self.response.write(rv)

    def handle_exception(self, exception, debug):
        handle_error(None, self.response, exception)
        
    def serve_404(self):
        render_error(self.response, 404, {}, '404.html')
        
            

def handle_error(request, response, exception):
    """
    Use standard error code for HTTPException, generic 500 code otherwise.
    404 have their own template page.
    500 template page displays traceback.
    Other errors display error code only.
    https://webapp-improved.appspot.com/guide/exceptions.html
    http://www.hipatic.com/2012/12/appengine-custom-error-handlers-using.html 
    """
    if isinstance(exception, webapp2.HTTPException):
        status = exception.code
    else: 
        status = 500
    logging.error("Error {}: {}".format(status, exception))
    
    if status == 404:
        render_error(response, status, {}, '404.html')
    elif status == 500:
        exc_type, exc_value, exc_tb = sys.exc_info()  # get trace
        trace = traceback.format_exception(exc_type, exc_value, exc_tb)
        context = {'error_code': status, 'exception': exception, 'trace': trace}
        render_error(response, status, context)
    else:  # other http error code
        context = {'error_code': status, 'exception': exception}
        render_error(response, status, context)


def render_error(response, status, context, template='error.html'):
    context['search_terms'] = search_terms
    renderer = jinja2.get_jinja2(app=webapp2.get_app())
    response.write(renderer.render_template(template, **context))
    response.set_status(status)
