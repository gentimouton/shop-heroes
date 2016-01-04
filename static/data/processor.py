from collections import defaultdict
import csv
import pprint
import re

############ helpers
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

def slugify(value):
    """
    Converts to lowercase, removes non-word characters (alphanumerics and
    underscores) and converts spaces to hyphens. Also strips leading and
    trailing whitespace.
    (From Django)
    """
    value = value.encode('ascii', 'ignore').decode('ascii')
    value = re.sub('[^\w\s-]', '', value).strip().lower()
    return str(re.sub('[-\s]+', '-', value))

def print_to_file(db_name, data, filename):
    """
    Write a database to a database file.
    filename is a python file name,
    data should be a simple python object (dict, list, etc.)    
    """
    print 'writing ' + filename
    output_file = open(filename, 'wb')
    output_file.write(db_name + ' = \\\n')
    output_file.write(pprint.pformat(data, indent=4))
    output_file.close()


############### process artifact data
artifacts = {}
filename = 'artifacts.csv'
print 'reading ' + filename
input_file = open(filename)
reader = csv.DictReader(input_file)  # Artifact Name,Level,Tier,Artifact Type
for row in reader:
    artifacts[slugify(row['Artifact Name'])] = {
        'name': row['Artifact Name'],
        'level': int(row['Level']),
        'tier': get_int(row, 'Tier', ignore=len('Tier ')),  # 0 for city raids
        'origin': row['Artifact Type']
        }
input_file.close()
print_to_file('artifact_db', artifacts, 'db_artifacts.py')


############### process resource data
resources = {}
filename = 'resources.csv'
print 'reading ' + filename
input_file = open(filename)
reader = csv.DictReader(input_file)  # Resource Name,Tier
for row in reader:
    resources[slugify(row['Resource Name'])] = {
        'name': row['Resource Name'],
        'tier': get_int(row, 'Tier'),
        'rank': get_int(row, 'Rank')  # order they are introduced in the game
        }
input_file.close()
print_to_file('resource_db', resources, 'db_resources.py')


############## process item data
items = defaultdict(dict)  # {'Swords': {'Shortsword': {}, ...}, 'Axes': {} }
filename = 'items.csv'
print 'reading ' + filename
input_file = open('items.csv')
reader = csv.DictReader(input_file)  # name, level, power, class, price

basics = ['price', 'level', 'power']
# sort resources by rank 
resources = sorted(resources.keys(), key=lambda slug: resources[slug]['rank'])
qualities = ['good', 'great', 'flawless', 'epic', 'legendary', 'mythical']

for row in reader:
    item_name = row['name']
    item_kind = row['class']
    
    # fill item_data
    item_data = {}
    item_data['name'] = item_name
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
            comp_qty = int(tokens[0]) # int('---') will raise ValueError
            comp_slug = slugify(' '.join(tokens[1:]))
            if comp_slug in artifacts.keys(): # component is an artifact
                item_comp[comp_slug] = comp_qty
            else: # component is a precraft
                quality = 'normal'
                if slugify(tokens[1]) in qualities:  # quality specified
                    quality = slugify(tokens[1])
                    comp_slug = slugify(' '.join(tokens[2:]))
                    # TODO: make sure that component slug exists
                item_comp[comp_slug] = (comp_qty, quality)
        except ValueError:  # first token was not an integer, eg int('---')
            continue
        
    item_data['components'] = item_comp
    items[item_kind][slugify(item_name)] = item_data
input_file.close()
print_to_file('item_db', dict(items), 'db_items.py')


################ write json
# output_file = open('items_db.js', 'wb')
# text = 'var items = ' + json.dumps(items, output_file, indent=3)
# output_file.write(text)
# output_file.close()

