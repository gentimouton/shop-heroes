from handlers.base import BaseHandler


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
        self.render_response('home.html', **context)

class SearchHandler(BaseHandler):
    def get(self):
        query = self.request.get('q')
        context = {'query': query}
        self.render_response('search.html', **context)