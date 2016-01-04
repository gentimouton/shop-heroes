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
        
        for item_slug, item_data in item_db[category.capitalize()].items():
            mats_display = []
            
            # resources from bins
            required_resources = item_data['resources']
            for rsrc_slug in resource_slugs:
                if rsrc_slug in required_resources.keys():
                    mat = {'kind': 'resource',
                        'slug': rsrc_slug,
                        'name': resource_db[rsrc_slug]['name'],
                        'qty': required_resources[rsrc_slug]}
                    mats_display.append(mat)
                    
            # components: artifacts and precrafts
            required_components = item_data['components']
            # sort components: artifacts before precrafts, then alphabetically 
            sorted_comps = sorted(required_components.keys(),
                key=lambda c_slug: (c_slug not in artifact_slugs, c_slug))
            logging.info('----- ' + str(sorted_comps))  
            for comp_slug in sorted_comps:
                comp_data = required_components[comp_slug]
                if comp_slug in artifact_slugs:  # artifact
                    mat = {'kind': 'artifact',
                        'slug': comp_slug,
                        'name': artifact_db[comp_slug]['name'],
                        'qty': comp_data}
                    mats_display.append(mat)
                else:  # precraft
                    mat = {'kind': 'precraft',
                        'slug': comp_slug,
                        'name': comp_slug,  # TODO: name instead
                        'qty': comp_data[0],
                        'quality': comp_data[1]}
                    mats_display.append(mat)
            
            # item name, level, img, and price
            item_name = item_data['name']
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
