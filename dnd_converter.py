import json
from llm_tools import call_llm
from llm_prompts import TYPE_PROMPT_TEMPLATE, OBJECT_TEMPLATE
from dnd_classes import DnDType, DND_MAP

def systematise_magic(description, system="D&D 5e"):

    prompt = TYPE_PROMPT_TEMPLATE.format(description=description, system=system)
    print("Sending to LLM...")

    try:
        response = call_llm(prompt, DnDType)
        entity_type = response.type
        print(f"Entity type: {entity_type}")
    except Exception as e:
        print(f"Error: {e}")


    prompt = OBJECT_TEMPLATE.format(dnd_type=entity_type, description=description, system=system)
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
