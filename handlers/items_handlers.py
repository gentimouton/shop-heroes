import logging
from handlers.base import BaseHandler
from db.items_db import item_db  # @UnresolvedImport

# ordered list of resources_list
resources_list = ['iron', 'wood', 'leather', 'herbs',
    'steel', 'hardwood', 'fabric', 'oil', 'mana', 'jewels']

def format_price(price):
    # 1500 becomes 1,500
    # 15500 becomes 15.5k
    return '{:,}'.format(price)
        
    
class ItemCategoryHandler(BaseHandler):
    def get(self, **kwargs):
        category = kwargs['category']
        items = []
        for item_name, item_data in item_db[category.capitalize()].items():
            # materials listing
            mats_display = []
            mats_required = item_data['resources'].keys()
            for r in resources_list:
                if r in mats_required:
                    qty = item_data['resources'][r]
                    mat_display = {
                        'qty': qty,
                        'name': r
                        }
                    mats_display.append(mat_display)
            # item level, img, and price
            item_filename = item_name.replace(' ', '_').replace('\'', '')
            img = '/static/%s/%s.png' % (category, item_filename)
            item = {
                'name': item_name,
                'level': item_data['level'],
                'price': format_price(item_data['price']),
                'power': item_data['power'],
                'img': img,
                'mats': mats_display
            }
            items.append(item)
        items.sort(key=lambda item: (item['level'], item['name']))
        context = {'category': category,
            'items': items,
            'resources': resources_list  # same order as in the icon sprite
            }
        self.render_response('category.html', **context)

class ItemListHandler(BaseHandler):
    def get(self):
        context = {'category': 'item list'}
        self.render_response('category.html', **context)
