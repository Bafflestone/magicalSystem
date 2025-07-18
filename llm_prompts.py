
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
You are a fantasy RPG {dnd_type} generator. Given a description and a target game system, output a structured {dnd_type} stat block appropriate to that system.

Description:
"{description}"

Target System: {system}

"""

SIMILAR_OBJECTS_TEMPLATE = """
Here are some examples of {dnd_type}s that could be similar, use them as a guide in creating this {dnd_type}. 
Examples:
"{similar_objects}"

"""

REFLECTION_PROMPT = """
You are a critic of a fantasy RPG {dnd_type} generator. The generatator has produced a {dnd_type} stat block based on a description and a target game system. Critique the {dnd_type} stat block and provide feedback on how it could be improved.
Give preference to more concise stat blocks with more interesting effects, and check that the generated {dnd_type} is a good thematic match with the description. If the {dnd_type} stat block is already good, say so.
Give at most two recommendations.

Description:
"{description}"

Target System: {system}

{dnd_type} Stat Block:
"{object_stat_block}"

"""

REFLECT_OBJECT_TEMPLATE = """
You are a fantasy RPG {dnd_type} generator. Given a description and a target game system, you have generated an {dnd_type} stat block. Now, based on a critique of that stat block, revise the {dnd_type} stat block to improve it.

Description:
"{description}"

Target System: {system}

{dnd_type} Stat Block:
"{object_stat_block}"

{dnd_type} Stat Block Critique:
"{critique}"

"""


MAGIC_PROMPT_TEMPLATE = """
You are the governing force of magic in a fantasy universe. Given a description of a set of circumstances that a group of mortals in your universe have constructed, determine what type of magical effect will occur.
Only describe one effect that occurs, not speculating about different possible outcomes.
If there is no effect respond with: there is no magical effect.
Description:
"{description}"


"""