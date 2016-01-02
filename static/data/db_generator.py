from collections import defaultdict
import csv
import json
import pprint
from string import Template


############ helper
def get_int(row, key, ignore=0):
    """ row is the csv row to get an integer from, 
    key is that row's column that we want to cast as int,
    ignore is the number of chars to ignore.
    return 0 if could not convert 
    """
    try:
        val = int(row[key][ignore:].replace(',', ''))
    except ValueError:  # raised by int('') or int('---')
        val = 0
    return val

############### fetch and write artifact data
artifacts = {}
input_file = open('artifacts.csv')
reader = csv.DictReader(input_file)  # Artifact Name,Level,Tier,Artifact Type
for row in reader:
    artifacts[row['Artifact Name']] = {
        'level': int(row['Level']),
        'tier': get_int(row, 'Tier', ignore=len('Tier ')),  # 0 for city raids
        'origin': row['Artifact Type']
        }
input_file.close()

pp = pprint.PrettyPrinter(indent=4)
output_file = open('artifacts_db.py', 'wb')
output_file.write('artifacts_db = \\\n')
output_file.write(pprint.pformat(artifacts, indent=4))
output_file.close()


############## read item data
print 'reading items.csv'
input_file = open('items.csv')
reader = csv.DictReader(input_file)
# name    level    power    class    price
# iron    wood    leather    herbs    steel    
# hwood    fabric    oil    mana    jewels
# comp1    comp2
items = defaultdict(dict)  # {'Swords': {'Shortsword': {}, ...}, 'Axes': {} }
basics = ['price', 'level', 'power']
resources = ['iron', 'wood', 'leather', 'herbs',
             'steel', 'hardwood', 'fabric', 'oil', 'mana', 'jewels']
for row in reader:
    item_name = row['name']
    item_kind = row['class']
    # fill item_data
    item_data = {}
    for b in basics:
        value = get_int(row, b)
        item_data[b] = value
    # resources
    item_res = {}
    for r in resources:
        value = get_int(row, r)
        if value:
            item_res[r] = value
    item_data['resources'] = item_res
    # components
    item_comp = {}
    for comp in [row['comp1'], row['comp2']]:
        tokens = comp.split(' ')
        try:
            comp_qty = int(tokens[0])
            comp_name = ' '.join(tokens[1:])  # rejoin tokens for component name
            if comp_name in artifacts.keys():  # TODO: precrafts as well
                item_comp[comp_name] = comp_qty
        except ValueError:  # first token was not an integer, eg int('---')
            continue
    item_data['components'] = item_comp
    items[item_kind][item_name] = item_data
input_file.close()

################ write python
print 'writing items_db.py'
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
print 'writing items_db.html'
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
