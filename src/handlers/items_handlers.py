from handlers.base import BaseHandler


class ItemCategoryHandler(BaseHandler):
    def get(self, **kwargs):
        context = {'category': kwargs['category']}
        self.render_response('category.html', **context)

class ItemListHandler(BaseHandler):
    def get(self):
        context = {'category': 'item list'}
        self.render_response('category.html', **context)
