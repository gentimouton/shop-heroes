import os
import urllib2
import time
from lxml import html
import random
from db_categories import categories_db
from db_items import item_db


user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
headers = { 'User-Agent' : user_agent }

# HTML structure 
# from http://shop-heroes.wikia.com/wiki/File:Spears_Iron_Spear.png
# =============
# <img alt="File:Spears Iron Spear.png" 
# src="http://vignette1.wikia.nocookie.net/shop-heroes/images/b/b6/Spears_Iron_Spear.png/revision/latest?cb=20151204183104" 
# data-image-name="Spears Iron Spear.png" 
# data-image-key="Spears_Iron_Spear.png" height="256" width="256">

category = 'daggers' # CHANGE THIS
directory = '../' + category
if not os.path.exists(directory):
    os.makedirs(directory)
    
for item_slug in categories_db[category]['items']:
    time.sleep(.5 + random.random() * 1.5) # throttle 

    # build wiki page url
    item_name = item_db[item_slug]['name'].replace(' ', '_')
    #filename = categories_db[category]['name'] + '_' + item_name + '.png'
    filename = item_name + '.png' # when wiki file name has no category prefix
    url = "http://shop-heroes.wikia.com/wiki/File:" + filename
    
    # get page html
    print 'fetching ' + url
    request = urllib2.Request(url, headers=headers)
    try:
        page = urllib2.urlopen(request).read()
    except urllib2.HTTPError:
        print '======= 404 ==========' 
        print url
        continue
    tree = html.fromstring(page)
    
    # fetch img and save to file
    img_urls = tree.xpath('//img[@width="256"]/@src') # find img url
    if len(img_urls) == 1:
        img_req = urllib2.Request(img_urls[0], headers=headers)
        img_data = urllib2.urlopen(img_req).read()
        filename = item_slug + '.png'
        output = open(os.path.join(directory, filename), 'wb')
        output.write(img_data)
        output.close()
        print 'saved file ' + filename
    else:
        print 'error: too many or not enough img urls'
        print img_urls
    