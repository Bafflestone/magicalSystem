from llm_tools import call_llm
from llm_prompts import MAGIC_PROMPT_TEMPLATE

def create_effect(description: str):

    prompt = MAGIC_PROMPT_TEMPLATE.format(description=description)
    print("Sending to LLM...")

    try:
        response = call_llm(prompt)
        print(f"Effect: {response}")
        return response
    except Exception as e:
        print(f"Error: {e}")
        return "There is no effect."



def main():
    create_effect("A group of five adventurers gather by a fire holding elemental gems of type fire, water, ice, earth and air chanting 'rage' over and over again.")

if __name__ == "__main__":
    main()
