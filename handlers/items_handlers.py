import logging

from db.db_artifacts import artifact_db
from db.db_resources import resource_db
from db.db_items import item_db
from handlers.base import BaseHandler


# ordered list of resources and special resources
resource_slugs = sorted(resource_db.keys(),
    key=lambda slug: resource_db[slug]['rank'])
artifact_slugs = sorted(artifact_db.keys(),
    key=lambda slug: artifact_db[slug]['level'])

# map resource and artifact slugs to their position in the icons sprite
icons_map = [resource_slugs,
    artifact_slugs[0:10],
    artifact_slugs[10:20],
    artifact_slugs[20:26],
    ['coin', 'gem', 'time', 'barracks', 'power', 'heart']
    ]


class ItemCategoryHandler(BaseHandler):
    
    def get(self, **kwargs):
        category = kwargs['category']
        items = []
        
        for item_name, item_data in item_db[category.capitalize()].items():
            mats_display = []
            
            # resources from bins
            required_resources = item_data['resources']
            for slug in resource_slugs:
                if slug in required_resources.keys():
                    mat = {'slug': slug,
                        'name': resource_db[slug]['name'],
                        'qty': required_resources[slug]}
                    mats_display.append(mat)
                    
            # components # TODO: precrafts 
            required_components = item_data['components']
            for slug in artifact_slugs:
                if slug in required_components.keys():
                    mat = {'slug': slug,
                        'name': artifact_db[slug]['name'],
                        'qty': required_components[slug]}
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
