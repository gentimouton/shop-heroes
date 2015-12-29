import logging
from handlers.base import BaseHandler
from db.items_db import item_db  # @UnresolvedImport


class ItemCategoryHandler(BaseHandler):
    def get(self, **kwargs):
        category = kwargs['category']
        items = item_db[category.capitalize()]
        ordered_items = [{
            'name': name, 
            'level': data['level'], 
            'price': data['price'],
            'img': '/static/%s/%s.png' % (category, name.replace(' ', '_'))
            } for name, data in items.items()]
        ordered_items.sort(key=lambda item: item['level'])
        logging.info(str(ordered_items))
        context = {'category': category,
            'items': ordered_items
            }
        self.render_response('category.html', **context)

class ItemListHandler(BaseHandler):
    def get(self):
        context = {'category': 'item list'}
        self.render_response('category.html', **context)
