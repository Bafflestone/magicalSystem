import json
from pydantic import BaseModel
from typing import Literal, Optional, List
from llm_tools import call_llm

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

class DnDType(BaseModel):
    type: Literal['Magic Item', 'Spell', 'Regular Item', 'Creature', 'Other']

class DnDAny(BaseModel):
    name: str
    description: str

class DnDItem(BaseModel):
    name: str
    damage: Optional[str]
    range: Optional[int] #In feet
    saving_throw: Optional[int]
    saving_throw_type: Optional[Literal['Strength', 'Dexterity', 'Constitution', 'Intelligence', 'Wisdom', 'Charisma']]
    charges: Optional[int]
    rarity: str
    effect_description: Optional[str]
    flavour_text: str

class DnDSpell(BaseModel):
    name: str
    damage: Optional[str]
    range: Optional[int] #In feet
    saving_throw_dc: Optional[int]
    saving_throw_type: Optional[Literal['Strength', 'Dexterity', 'Constitution', 'Intelligence', 'Wisdom', 'Charisma']]
    components: List[Literal['Verbal', 'Somatic', 'Material']]
    materials: Optional[List[str]]
    magic_school: Literal['Evocation', 'Necromancy', 'Abjuration', 'Enchantment', 'Divination']
    spell_level: int
    effect_description: str
    flavour_text: str

class DnDEffect(BaseModel):
    name: Optional[str]
    damage: Optional[str]
    range: Optional[int] #In feet
    saving_throw_dc: Optional[int]
    saving_throw_type: Optional[Literal['Strength', 'Dexterity', 'Constitution', 'Intelligence', 'Wisdom', 'Charisma']]
    effect_description: str
    flavour_text: str

DND_MAP = {
    "Magic Item": DnDItem,
    "Spell": DnDSpell,
    "Regular Item": DnDItem,
    "Creature": DnDAny,
    "Other": DnDAny
}

def systematise_magic(description, system="D&D 5e"):

    prompt = TYPE_PROMPT_TEMPLATE.format(description=description, system=system)
    print("Sending to LLM...")

    try:
        response = call_llm(prompt, DnDType)
        entity_type = response.type
        print(f"Entity type: {entity_type}")
    except Exception as e:
        print(f"Error: {e}")


    prompt = OBJECT_TEMPLATE.format(description=description, system=system)
    entity_model = DND_MAP[entity_type]

    print("Sending to LLM...")

    try:
        response = call_llm(prompt, entity_model)
        item_data = response.model_dump()
        print(json.dumps(item_data, indent=2))
    except Exception as e:
        print(f"Error: {e}")

def main():
    systematise_magic("A metal scimitar that is engulfed by flame.")

if __name__ == "__main__":
    main()
