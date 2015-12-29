import webapp2

from routes import routes


app = webapp2.WSGIApplication(routes)

