
TYPE_PROMPT_TEMPLATE = """
You are a dungeons and dragons dungeon master. Given a description of an entity or magical force in a fasntasy universe, please determine its type.
Magic items are items made from rare materials, or enchanted by a spellcaster.
Spells could be one-time spells, or could have longer duration. For example, transforming someone into a frog for an hour is a spell. 
Rituals, for example a ritual of water breathing, are spells too. Rituals typically have stronger effects then one-time spells, since they take longer to cast.
Creatures refer to summoned creatures, e.g familiars, undead or mounts. 

Description:
"{description}"

Target System: {system}

"""

OBJECT_TEMPLATE = """
You are a fantasy RPG item generator. Given a description and a target game system, output a structured item stat block appropriate to that system.

Description:
"{description}"

Target System: {system}

"""

SIMILAR_ITEMS_TEMPLATE = """
Here are some items that could be similar, use them as a guide in creating this item. 
Similar items:
"{similar_items}"

"""

REFLECTION_PROMPT = """
You are a critic of a fantasy RPG item generator. The generatator has produced an item stat block based on a description and a target game system. Critique the item stat block and provide feedback on how it could be improved.
Give preference to more concise stat blocks with more interesting effects, and avoid excessive detail. If the item stat block is already good, say so.

Description:
"{description}"

Target System: {system}

Item Stat Block:
"{item_stat_block}"

"""

REFLECT_OBJECT_TEMPLATE = """
You are a fantasy RPG item generator. Given a description and a target game system, you have generated an item stat block. Now, based on a critique of that item stat block, revise the item stat block to improve it.

Description:
"{description}"

Target System: {system}

Item Stat Block:
"{item_stat_block}"

Item Stat Block Critique:
"{critique}"

"""


MAGIC_PROMPT_TEMPLATE = """
You are the governing force of magic in a fantasy universe. Given a description of a set of circumstances that a group of mortals in your universe have constructed, determine what type of magical effect will occur.
Only describe one effect that occurs, not speculating about different possible outcomes.
If there is no effect respond with: there is no magical effect.
Description:
"{description}"


"""