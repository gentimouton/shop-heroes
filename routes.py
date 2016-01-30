import webapp2

from handlers.items_handlers import ItemHandler, ItemCategoryHandler
from handlers.misc_handlers import HomeHandler, HeroListHandler, \
    FurnitureListHandler, SearchHandler


# See http://webapp-improved.appspot.com/guide/routing.html#simple-routes
routes = [webapp2.Route(r'/', handler=HomeHandler, name='home'),
    webapp2.Route(r'/search', handler=SearchHandler, name='search'),
    webapp2.Route(r'/items/<category:\D+>', handler=ItemCategoryHandler, name='category'),
    webapp2.Route(r'/item/<slug:\D+>', handler=ItemHandler, name='item'),
    webapp2.Route(r'/heroes', handler=HeroListHandler, name='item-list'),
    webapp2.Route(r'/furniture', handler=FurnitureListHandler, name='item-list'),
    ]
