"""This module contains methods that handle items and their attributes."""
import ujson

from subs.miniscape import users
from subs.gastercoin import account as ac
from subs.miniscape import monsters as mon
from subs.miniscape.files import ITEM_JSON, SHOP_FILE

with open(ITEM_JSON, 'r') as f:
    ITEMS = ujson.load(f)

NAME_KEY = 'name'           # Name of the item
VALUE_KEY = 'value'         # High alch value of the item
DAMAGE_KEY = 'damage'       # Damage stat of the item
ACCURACY_KEY = 'accuracy'   # Accuracy stat of the item
ARMOUR_KEY = 'armour'       # Armuour stat of the item
SLOT_KEY = 'slot'           # Slot item can be equipped
AFFINITY_KEY = 'aff'        # Item affinity, 0:Melee, 1:Range, 2:Magic
LEVEL_KEY = 'level'         # Level item can be equipped/gathered
XP_KEY = 'xp'               # xp gained for gathering/crafting the item.
GATHER_KEY = 'gather'       # Boolean whether item can be gathered.
TREE_KEY = 'tree'           # Boolean whether gatherable is a tree.
ROCK_KEY = 'rock'           # Boolean whether gatherable is a rock.
FISH_KEY = 'fish'           # Boolean whether gatherable is a fish.
DEFAULT_ITEM = {NAME_KEY: 'unknown item',
                VALUE_KEY: 0,
                DAMAGE_KEY: 0,
                ACCURACY_KEY: 0,
                ARMOUR_KEY: 0,
                SLOT_KEY: 0,
                AFFINITY_KEY: 0,
                LEVEL_KEY: 1,
                XP_KEY: 1,
                GATHER_KEY: False}

SLOT_NAMES = {
        "0": "None",
        "1": "Head",
        "2": "Back",
        "3": "Neck",
        "4": "Ammunition",
        "5": "Main-Hand",
        "6": "Torso",
        "7": "Off-Hand",
        "8": "Legs",
        "9": "Hands",
        "10": "Feet",
        "11": "Ring",
        "12": "Pocket",
        "13": "Aura"
    }


def add_plural(itemid):
    return get_attr(itemid) + 's'


def buy(userid, item, number):
    """Buys (a given amount) of an item and places it in the user's inventory."""
    try:
        itemid = find_by_name(item)
        number = int(number)
    except KeyError:
        return f'Error: {item} is not an item.'
    except ValueError:
        return f'Error: {number} is not a number.'

    item_name = get_attr(itemid)
    if item_in_shop(itemid):
        items = open_shop()
        if int(items[itemid]) in users.get_completed_quests(userid) or int(items[itemid]) == 0:
            value = get_attr(itemid, key=VALUE_KEY)
            users.update_inventory(userid, [itemid]*number)
            ac.update_account(userid, -(4 * number * value))
            value_formatted = '{:,}'.format(4 * value * number)
            return f'{number} {item_name} bought for G${value_formatted}!'
        else:
            return 'Error: You do not have the requirements to buy this item.'
    else:
        return f'Error: {item_name} not in inventory or you do not have at least {number} in your inventory.'


def compare(item1, item2):
    """Prints a string comparing the stats of two given items."""
    try:
        item1id = find_by_name(item1)
    except KeyError:
        return f'Error: {item1} does not exist.'
    try:
        item2id = find_by_name(item2)
    except KeyError:
        return f'Error: {item2} does not exist.'

    item1_acc = get_attr(item1id, key=ACCURACY_KEY)
    item1_dam = get_attr(item1id, key=DAMAGE_KEY)
    item1_arm = get_attr(item1id, key=ARMOUR_KEY)

    item2_acc = get_attr(item2id, key=ACCURACY_KEY)
    item2_dam = get_attr(item2id, key=DAMAGE_KEY)
    item2_arm = get_attr(item2id, key=ARMOUR_KEY)

    out = f'__**:moneybag: COMPARE :moneybag:**__\n'\
          f'**{item1} vs {item2}:**\n\n'\
          f'**Accuracy**: {item1_acc} vs {item2_acc} *({item1_acc - item2_acc})*\n' \
          f'**Damage**: {item1_dam} vs {item2_dam} *({item1_dam - item2_dam})*\n' \
          f'**Armour**: {item1_arm} vs {item2_arm} *({item1_arm - item2_arm})*'
    return out


def find_by_name(name):
    """Finds an item's ID from its name."""
    for item in list(ITEMS.keys()):
        if name == ITEMS[item][NAME_KEY]:
            return item
    else:
        raise KeyError


def get_attr(itemid, key=NAME_KEY):
    """Gets an item's attribute from its id."""
    itemid = str(itemid)
    if itemid in set(ITEMS.keys()):
        try:
            return ITEMS[itemid][key]
        except KeyError:
            ITEMS[itemid][key] = DEFAULT_ITEM[key]
            return ITEMS[itemid][key]
    else:
        raise KeyError


def item_in_shop(itemid):
    """Checks if an item is in the shop."""
    return str(itemid) in set(open_shop().keys())


def open_shop():
    """Opens the shop file and places the items and quest reqs in a dictionary."""
    with open(SHOP_FILE, 'r') as f:
        lines = f.read().splitlines()
    items = {}
    for line in lines:
        itemid, quest_req = line.split(';')
        items[itemid] = quest_req
    return items


def sell(userid, item, number):
    """Sells (a given amount) of an item from a user's inventory."""
    try:
        itemid = find_by_name(item)
        number = int(number)
    except KeyError:
        return f'Error: {item} is not an item.'
    except ValueError:
        return f'Error: {number} is not a number.'

    item_name = get_attr(itemid)
    if users.item_in_inventory(userid, itemid, number=number):
        value = get_attr(itemid, key=VALUE_KEY)
        users.update_inventory(userid, [itemid]*number, remove=True)
        ac.update_account(userid, number * value)
        value_formatted = '{:,}'.format(value * number)
        return f'{number} {item_name} sold for G${value_formatted}!'
    else:
        return f'Error: {item_name} not in inventory or you do not have at least {number} in your inventory.'


def print_shop(userid):
    """Prints the shop."""
    items = open_shop()

    header = '__**:moneybag: SHOP :moneybag:**__\n'
    messages = []
    out = f'{header}'
    for itemid in list(items.keys()):
        if int(items[itemid]) in set(users.get_completed_quests(userid)) or items[itemid] == '0':
            name = get_attr(itemid)
            price = '{:,}'.format(4 * get_attr(itemid, key=VALUE_KEY))
            out += f'**{name.title()}**: G${price}\n'
        if len(out) > 1800:
            messages.append(out)
            out = f'{header}'
    messages.append(out)
    return messages


def print_stats(item):
    """Prints the stats of an item."""
    try:
        itemid = find_by_name(item)
    except KeyError:
        return f'Error: {item} is not an item.'

    name = get_attr(itemid).title()
    value = '{:,}'.format(get_attr(itemid, key=VALUE_KEY))
    damage = get_attr(itemid, key=DAMAGE_KEY)
    accuracy = get_attr(itemid, key=ACCURACY_KEY)
    armour = get_attr(itemid, key=ARMOUR_KEY)
    slot = get_attr(itemid, key=SLOT_KEY)
    level = get_attr(itemid, key=LEVEL_KEY)

    out = f'__**:moneybag: ITEMS :moneybag:**__\n'
    out += f'**Name**: {name}\n'
    out += f'**Value**: G${value}\n'
    if slot > 0:
        out += f'**Damage**: {damage}\n'
        out += f'**Accuracy**: {accuracy}\n'
        out += f'**Armour**: {armour}\n'
        out += f'**Slot**: {users.SLOTS[str(slot)].title()}\n'
        out += f'**Level Requirement**: {level}\n'

    out += "\n" + mon.print_item_from_lootable(itemid)
    return out
