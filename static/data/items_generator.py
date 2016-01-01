import csv
import json
from collections import defaultdict
from string import Template


############ helper

def get_int(row, key):
    try:
        val = int(row[key].replace(',', ''))
    except ValueError:  # raised by int('') or int('---')
        val = 0
    return val

############### fetch special resources data
special_resources = []
input_file = open('special resources.csv')
reader = csv.DictReader(input_file)  # Resource,Level
for row in reader:
    special_resources.append(row['Resource'])
input_file.close()

############## read item data
input_file = open('items.csv')
reader = csv.DictReader(input_file)
# name    level    power    class    price
# iron    wood    leather    herbs    steel    
# hwood    fabric    oil    mana    jewels
# comp1    comp2
items = defaultdict(dict)  # {'Swords': {'Shortsword': {}, ...}, 'Axes': {} }
basics = ['price', 'level', 'power']
resources = ['iron', 'wood', 'leather', 'herbs',
             'steel', 'hwood', 'fabric', 'oil', 'mana', 'jewels']
for row in reader:
    name = row['name']
    kind = row['class']
    # fill item_data
    item_data = {}
    for b in basics:
        value = get_int(row, b)
        item_data[b] = value
    item_res = {}
    for r in resources:
        value = get_int(row, r)
        if value:
            item_res[r] = value
    item_data['resources'] = item_res
    items[kind][name] = item_data
input_file.close()

################ write python
import pprint 
pp = pprint.PrettyPrinter(indent=4)
output_file = open('items_db.py', 'wb')
output_file.write('item_db = \\\n')
output_file.write(pprint.pformat(dict(items), indent=4))
output_file.close()

################ write json
output_file = open('items_db.js', 'wb')
text = 'var items = ' + json.dumps(items, output_file, indent=3)
output_file.write(text)
output_file.close()

################## html templates ###############

doc_template_str = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta http-equiv="X-UA-Compatible" content="IE=edge">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>Shop Heroes</title>
        <link href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.5/css/bootstrap.min.css" rel="stylesheet" media="screen"/>
        <script src="https://ajax.googleapis.com/ajax/libs/jquery/1.11.3/jquery.min.js"></script>
        <script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.5/js/bootstrap.min.js"></script>
        <link href="custom.css" rel="stylesheet" media="screen"/>
    </head>
    <body>
        $body
    </body>
    </html>
"""

section_template_str = """
    <div class='container section'>
        <h1>$kind</h1>
        <div class='row'>
            $items
        </div>
    </div>
"""

item_template_str = """
    <div class="col-sm-6 col-lg-4">
        <div class="col-xs-4">
            <img class="img-responsive" title="$name" src="../item_placeholder.png">
        </div>
        <div class="col-xs-8">
            <div>
                <span class="itemLevel">$lvl</span>
                <span class="itemName">$name</span>
            </div>
            <div class='row'>
                $mats
            </div>
        </div>
    </div>
"""


################# write HTML from string templates
output_file = open('items_db.html', 'wb')
document_template = Template(doc_template_str)
section_template = Template(section_template_str)
item_template = Template(item_template_str)

sections_str = ''
for kind in items.keys():
    # sort by item level
    # http://stackoverflow.com/questions/613183/sort-a-python-dictionary-by-value
    ordered_kind = sorted(items[kind].items(), key=lambda kv_pair: kv_pair[1]['level'])
    items_str = ''
    for name, item_data in ordered_kind:
        mats = '<div class="row">\n'
        lvl = item_data['level']
        price = item_data['price']
        # find resources
        res = item_data['resources'].keys()
        for r in resources:
            if r in res:
                qty = item_data['resources'][r]
                mats += '<div class="col-xs-4 col-sm-3 nopadding">%d<img src="../resources/%s.png"></div>\n' % (qty, r)
        mats += '</div>\n'
        items_str += item_template.substitute(name=name, lvl=lvl, mats=mats)
    sections_str += section_template.substitute(kind=kind, items=items_str)

output_file.write(document_template.substitute(body=sections_str))
output_file.close()
