

def systematise_magic(description, system="D&D 5e"):

    prompt = TYPE_PROMPT_TEMPLATE.format(description=description, system=system)
    print("Sending to Ollama...")

    try:
        response = call_ollama(prompt, DnDType)
        type_dict = extract_json(response)
        print(type_dict)
        entity_type = type_dict['type']
    except Exception as e:
        print(f"Error: {e}")


    prompt = OBJECT_TEMPLATE.format(description=description, system=system)
    entity_model = DND_MAP[entity_type]

    print("Sending to Ollama...")

    try:
        response = call_ollama(prompt, entity_model)
        item_data = extract_json(response)
        print(json.dumps(item_data, indent=2))
    except Exception as e:
        print(f"Error: {e}")