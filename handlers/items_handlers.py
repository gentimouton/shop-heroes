import logging
from handlers.base import BaseHandler
from db.items_db import item_db  # @UnresolvedImport

# ordered list of mats_list
mats_list = ['iron', 'wood', 'leather', 'herbs',
             'steel', 'hwood', 'fabric', 'oil', 'mana', 'jewels']

class ItemCategoryHandler(BaseHandler):
    def get(self, **kwargs):
        category = kwargs['category']
        items = []
        for item_name, item_data in item_db[category.capitalize()].items():
            # materials listing
            mats_display = []
            mats_required = item_data['resources'].keys()
            for m in mats_list:
                if m in mats_required:
                    qty = item_data['resources'][m]
                    mat_display = {
                        'qty': qty,
                        'img': '/static/resources/%s.png' % m
                        }
                    mats_display.append(mat_display)
            # item level, img, and price
            img = '/static/%s/%s.png' % (category, item_name.replace(' ', '_'))
            item = {
                'name': item_name,
                'level': item_data['level'], 
                'price': item_data['price'],
                'img': img,
                'mats': mats_display
            }
            items.append(item)
        items.sort(key=lambda item: item['level'])
        context = {'category': category,
            'items': items
            }
        self.render_response('category.html', **context)

class ItemListHandler(BaseHandler):
    def get(self):
        context = {'category': 'item list'}
        self.render_response('category.html', **context)
