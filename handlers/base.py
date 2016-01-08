import logging
import sys
import traceback

import webapp2
from webapp2_extras import jinja2


# prevent template lines to leave blank lines
jinja2.default_config['environment_args']['trim_blocks'] = True


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

    def handle_exception(self, exception, debug):
        handle_error(None, self.response, exception)
    

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
    renderer = jinja2.get_jinja2(app=webapp2.get_app())
    
    if status == 404:
        render_error(response, renderer, status, {}, '404.html')
    elif status == 500:
        exc_type, exc_value, exc_tb = sys.exc_info()  # get trace
        trace = traceback.format_exception(exc_type, exc_value, exc_tb)
        context = {'error_code': status, 'exception': exception, 'trace': trace}
        render_error(response, renderer, status, context)
    else:  # other http error code
        context = {'error_code': status, 'exception': exception}
        render_error(response, renderer, status, context)


def render_error(response, renderer, status, context, template='error.html'):
    response.write(renderer.render_template(template, **context))
    response.set_status(status)
