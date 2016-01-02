import logging

from db.artifacts_db import artifacts_db
from db.items_db import item_db
from handlers.base import BaseHandler


# ordered list of resources and special resources
resources_list = ['iron', 'wood', 'leather', 'herbs',
    'steel', 'hardwood', 'fabric', 'oil', 'mana', 'jewels']
artifacts_list = sorted(artifacts_db.keys(),
    key=lambda name: artifacts_db[name]['level'])
# only keep alphanum characters in artifact names
artifacts_slugs = {
    artifact: ''.join(c for c in artifact if c.isalnum()) 
    for artifact in artifacts_list
    }

# map resource and artifact slugs to their position in the icons sprite
icons_map = [resources_list,
    [artifacts_slugs[a] for a in artifacts_list[0:10]],
    [artifacts_slugs[a] for a in artifacts_list[10:20]],
    [artifacts_slugs[a] for a in artifacts_list[20:26]],
    ['coin', 'gem', 'time', 'barracks', 'power', 'heart']
    ]       


class ItemCategoryHandler(BaseHandler):
    
    def get(self, **kwargs):
        category = kwargs['category']
        items = []
        
        for item_name, item_data in item_db[category.capitalize()].items():
            # materials listing # TODO: db_gen.py should generate slugs for me
            mats_display = []
            # resources from bins
            required_resources = item_data['resources']
            for r in resources_list:
                if r in required_resources.keys():
                    mat = {'name': r, 
                        'slug': r, 
                        'qty': required_resources[r]}
                    mats_display.append(mat)
                    
            # components # TODO: precrafts 
            # TODO: db_gen.py should generate slugs for me
            required_components = item_data['components']
            for artifact in artifacts_list:
                if artifact in required_components.keys():
                    mat = {'name': artifact,
                        'slug': artifacts_slugs[artifact],
                        'qty': required_components[artifact]}
                    mats_display.append(mat)

            # item level, img, and price
            item_filename = item_name.replace(' ', '_').replace('\'', '')
            img = '/static/%s/%s.png' % (category, item_filename)
            item = {
                'name': item_name,
                'level': item_data['level'],
                'price': '{:,}'.format(item_data['price']),
                'power': item_data['power'],
                'img': img,
                'mats': mats_display
            }
            items.append(item)
        items.sort(key=lambda item: (item['level'], item['name']))
        context = {'category': category,
            'items': items,
            'icons_map': icons_map
            }
        self.render_response('category.html', **context)


class ItemListHandler(BaseHandler):
    def get(self):
        context = {'category': 'item list'}
        self.render_response('category.html', **context)
