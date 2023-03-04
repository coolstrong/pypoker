from unittest import TestCase, skip
from random import randint
from card import CardSet

from main import compare_hands


class PokerHand(object):
    """решение с CodeWars - работает херово, поэтому тесты не проходят"""

    CARD = "23456789TJQKA"
    RESULT = [-1, 0, 1]

    def __init__(self, hand):
        values = "".join(sorted(hand[::3], key=self.CARD.index))
        suits = set(hand[1::3])
        is_straight = values in self.CARD
        is_flush = len(suits) == 1
        self.score = (
            2 * sum(values.count(card) for card in values)
            + 13 * is_straight
            + 15 * is_flush,
            [self.CARD.index(card) for card in values[::-1]],
        )

    def compare_with(self, other):
        return self.RESULT[(self.score > other.score) - (self.score < other.score) + 1]


NUMBER_OF_TESTS = 10**6

class RandomTest(TestCase):
    @skip("Bad reference solution")
    def test_random(self):
        for _ in range(NUMBER_OF_TESTS):
            set1 = str(CardSet.random())
            set2 = str(CardSet.random())

            self.assertEqual(
                compare_hands(set1, set2),
                PokerHand(set1).compare_with(PokerHand(set2)),
                f"Failed for sets: ({set1}) and ({set2})"
            )
