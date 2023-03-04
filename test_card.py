from unittest import TestCase
from card import Card, Suit, CardSet


class CardTest(TestCase):
    def test_1(self):
        card = Card.parse("JD")
        self.assertEqual(card.suit, Suit.D)
        self.assertEqual(card.value, 11)

    def test_2(self):
        card = Card.parse("2H")
        self.assertEqual(card.suit, Suit.H)
        self.assertEqual(card.value, 2)

    def test_3(self):
        card = Card.parse("AS")
        self.assertEqual(card.suit, Suit.S)
        self.assertEqual(card.value, 14)

    def test_rus_1(self):
        card = Card.parse_rus("ЕБ")
        self.assertEqual(card.suit, Suit.D)
        self.assertEqual(card.value, 10)

    def test_rus_2(self):
        card = Card.parse_rus("ТП")
        self.assertEqual(card.suit, Suit.S)
        self.assertEqual(card.value, 14)

    def test_comparsion_1(self):
        card1 = Card.parse("JD")
        card2 = Card.parse("2H")
        self.assertTrue(card1 > card2)

    def test_comparsion_2(self):
        card1 = Card.parse("QD")
        card2 = Card.parse("QS")
        self.assertTrue(card1 > card2)

    def test_equal(self):
        self.assertTrue(Card.parse("QS") == Card.parse("QS"))


class CardSetTest(TestCase):
    def test_1(self):
        hand = CardSet.parse("KS 2H 5C JD TD")
        self.assertCountEqual(hand.suits, (Suit.S, Suit.H, Suit.C, Suit.D, Suit.D))
        self.assertCountEqual(hand.values, (2, 5, 10, 11, 13))

    def test_iterates(self):
        for card in CardSet.parse("KS 2H 5C JD TD"):
            pass

    def test_sorting_1(self):
        set = CardSet.parse("KS 2H 5C JD TD")
        cards = tuple(map(lambda s: Card.parse(s), "KS JD TD 5C 2H".split(" ")))

        self.assertSequenceEqual(set.cards, cards)

    def test_sorting_2(self):
        set = CardSet.parse("KS 2H 5C JS JD")
        cards = tuple(map(lambda s: Card.parse(s), "KS JD JS 5C 2H".split(" ")))

        self.assertSequenceEqual(set.cards, cards)
