import json
from pydantic import BaseModel
from typing import Literal, Optional, List
from llm_tools import call_llm

MAGIC_PROMPT_TEMPLATE = """
You are the governing force of magic in a fantasy universe. Given a description of a set of circumstances that a group of mortals in your universe have constructed, determine what type of magical effect will occur.
Only describe one effect that occurs, not speculating about different possible outcomes.
If there is no effect respond with: there is no magical effect.
Description:
"{description}"


"""



def create_effect(description, system="D&D 5e"):

    prompt = MAGIC_PROMPT_TEMPLATE.format(description=description)
    print("Sending to LLM...")

    try:
        response = call_llm(prompt)
        # print(response)
        print(f"Effect: {response}")
        return response
    except Exception as e:
        print(f"Error: {e}")
        return "There is no effect."



def main():
    create_effect("A group of five adventurers gather by a fire holding elemental gems of type fire, water, ice, earth and air chanting 'rage' over and over again.")

if __name__ == "__main__":
    main()
