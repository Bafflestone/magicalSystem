
TYPE_PROMPT_TEMPLATE = """
You are a dungeons and dragons dungeon master. Given a description of an entity or magical force in a fasntasy universe, please determine its type.

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
If there is no effect respond with: there is no magical effect.
Description:
"{description}"


"""