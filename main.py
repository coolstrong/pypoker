from typing import Literal
from card import CardSet
from combinations import Combination


def compare_hands(set1str: str, set2str: str) -> Literal[-1, 0, 1]:
    def get_combination(setstr: str):
        return Combination.find_highest(CardSet.parse(setstr))

    return get_combination(set1str).compare(get_combination(set2str)).value


if __name__ == "__main__":
    set1 = input("Input first card set:")
    set2 = input("Input second card set:")

    print(
        {
            -1: "First set is weaker than second",
            0: "Sets are equal",
            1: "First set is stronger than second",
        }[compare_hands(set1, set2)]
    )
