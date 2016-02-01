import csv
import pprint
import re


############ helpers
def get_int(row, key, ignore_start=0, ignore_end=None):
    """ row is the csv row to get an integer from, 
    key is that row's column that we want to cast as int,
    start/end is the number of leading/trailing characters to ignore.
    return 0 if could not convert 
    """
    try:
        s = row[key][ignore_start:(-ignore_end if ignore_end else None)]
        val = int(s.replace(',', ''))  # replace 1,000 by 1000
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

def print_to_file(db_name, db_data, filename):
    """
    Write a database to a database file.
    filename is a python file name,
    data should be a simple python object (dict, list, etc.)    
    """
    print 'writing ' + filename
    output_file = open(filename, 'wb')
    output_file.write(db_name + ' = \\\n')
    output_file.write(pprint.pformat(db_data, indent=4))
    output_file.close()


############### process worker and crafting skill data
workers = {}  # {'blacksmith': {'name': 'Blacksmith', 'tier': 1}, }
skills = {}  # {'metal-working': 'Metal Working', }
filename = 'workers.csv'
print 'reading ' + filename
input_file = open(filename)
reader = csv.DictReader(input_file)  
# name,tier,level-cap,points-per-level,skill1,skill2,skill3,skill4,unlock
# Blacksmith,Tier 1,50,5 Skill Points,
#Metal Working,Weapon Crafting,---,---,Forge - Level 1
for row in reader:
    worker_slug = slugify(row['name'])
    workers[worker_slug] = {
        'name': row['name'],
        'tier': get_int(row, 'tier', ignore_start=len('Tier ')),  # 1 to 4
        'per-level': get_int(row, 'per-level', ignore_end=len(' Skill Points'))
        }
    for i in range(1, 5):
        skill_name = row['skill%d' % i]
        skill_slug = slugify(skill_name)
        if skill_name != '---':
            skills[skill_slug] = skill_name
            workers[worker_slug]['skill%d' % i] = skill_slug
input_file.close()
print_to_file('worker_db', workers, 'db_workers.py')
print_to_file('skill_db', skills, 'db_skills.py')


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
        'tier': get_int(row, 'Tier', ignore_start=len('Tier ')),  # 0 for city raids
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


############## process item categories and item data
item_categories = {}  # {'axes': {'name': 'Axes', 'items': ['hawk']}  
items = {}  # { 'hawk': {'price': 1, 'name': 'Hawk'}, 'fire-gun': {} }

# read item categories
filename = 'item_categories.csv'
print 'reading ' + filename
input_file = open(filename)
reader = csv.DictReader(input_file)  # name, metacategory, rank, slot, slotname
for row in reader:
    item_categories[row['slug']] = {  # swords
        'name': row['name'],  # Swords
        'meta_category': row['metacategory'],  # Weapons 
        'rank': int(row['rank']),  # 1
        'slot': int(row['slot']),  # 1
        'slot_name': row['slotname'],  # Right Hand
        'items': []  # ['Shortsword', 'Longsword']
    }
input_file.close()

# read items
filename = 'items.csv'
print 'reading ' + filename
input_file = open(filename)
reader = csv.DictReader(input_file)  # name, level, power, class, price

basics_int = ['price', 'level', 'power']
# sort resources by rank 
resources = sorted(resources.keys(), key=lambda slug: resources[slug]['rank'])
qualities = ['good', 'great', 'flawless', 'epic', 'legendary', 'mythical']

for row in reader:
    # fill item_data
    item_data = {}
    item_data['name'] = row['name']
    category_slug = slugify(row['class'])
    if category_slug == 'armor':
        category_slug = 'armors'
    item_data['category'] = category_slug
    item_slug = slugify(item_data['name'])
    item_data['slug'] = item_slug
    for b in basics_int:
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
            comp_qty = int(tokens[0])  # int('---') will raise ValueError
            comp_slug = slugify(' '.join(tokens[1:]))
            if comp_slug in artifacts.keys():  # component is an artifact
                item_comp[comp_slug] = comp_qty
            else:  # component is a precraft
                quality = 'normal'
                if slugify(tokens[1]) in qualities:  # quality specified
                    quality = slugify(tokens[1])
                    comp_slug = slugify(' '.join(tokens[2:]))
                    # TODO: make sure that component slug exists
                item_comp[comp_slug] = (comp_qty, quality)
        except ValueError:  # first token was not an integer, eg int('---')
            continue
    item_data['components'] = item_comp
    
    # skills required
    item_skills = {}
    for skill in skills.keys():
        value = get_int(row, skill) # column headers are skill slugs
        if value:
            item_skills[skill] = value
    item_data['skills'] = item_skills
    
    # fill-up databases
    item_categories[category_slug]['items'].append(item_slug)
    items[item_slug] = item_data
input_file.close()

# write
print_to_file('item_db', items, 'db_items.py')
print_to_file('categories_db', item_categories, 'db_categories.py')


################ write json
# output_file = open('items_db.js', 'wb')
# text = 'var items = ' + json.dumps(items, output_file, indent=3)
# output_file.write(text)
# output_file.close()

print 'done'
