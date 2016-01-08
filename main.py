import webapp2

from handlers.base import handle_error
from routes import routes


app = webapp2.WSGIApplication(routes)

app.error_handlers[404] = handle_error
app.error_handlers[500] = handle_error
