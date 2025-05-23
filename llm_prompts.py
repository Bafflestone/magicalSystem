
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

MAGIC_PROMPT_TEMPLATE = """
You are the governing force of magic in a fantasy universe. Given a description of a set of circumstances that a group of mortals in your universe have constructed, determine what type of magical effect will occur.
If there is no effect respond with: there is no magical effect.
Description:
"{description}"


"""