import webapp2

from handlers import HomeHandler, ItemListHandler, ItemCategoryHandler, \
    HeroListHandler, FurnitureListHandler


# See http://webapp-improved.appspot.com/guide/routing.html#simple-routes
routes = [webapp2.Route(r'/', handler=HomeHandler, name='home'),
    webapp2.Route(r'/items', handler=ItemListHandler, name='item-list'),
    webapp2.Route(r'/items/<category:\D+>', handler=ItemCategoryHandler, name='category'),
    webapp2.Route(r'/heroes', handler=HeroListHandler, name='item-list'),
    webapp2.Route(r'/furniture', handler=FurnitureListHandler, name='item-list'),
    ]

app = webapp2.WSGIApplication(routes)

