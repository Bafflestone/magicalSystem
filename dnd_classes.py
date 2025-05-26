from pydantic import BaseModel
from typing import Literal, Optional, List

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