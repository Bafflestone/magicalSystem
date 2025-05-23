from effect_creator import create_effect
from dnd_converter import systematise_magic

EXAMPLE_TEXT = "A group of five adventurers gather by a fire holding elemental gems of type fire, water, ice, earth and air chanting 'rage' over and over again."
def main():
    effect = create_effect(EXAMPLE_TEXT)
    systematise_magic(effect)

if __name__ == "__main__":
    main()
