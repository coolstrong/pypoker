from unittest import TestCase

from card import CardSet, Suit
from combinations import (
    Flush,
    FullHouse,
    Straight,
    StraightFlush,
    TwoPairs,
    compare_by_value_n,
    CompareResult,
    Pair,
    compare_ints,
    HighCard,
    CombinationException,
)


class CompareTest(TestCase):
    def test_ints(self):
        self.assertEqual(compare_ints(5, 1), CompareResult.GREATER)
        self.assertEqual(compare_ints(5, 23), CompareResult.LESS)
        self.assertEqual(compare_ints(5, 5), CompareResult.EQUAL)

    def test_value_n(self):
        self.assertEqual(
            compare_by_value_n(CardSet.parse("2C 6H AD"), CardSet.parse("KD QD 9C")),
            CompareResult.GREATER,
        )
        self.assertEqual(
            compare_by_value_n(CardSet.parse("AD JS 2D"), CardSet.parse("AS JH 5D")),
            CompareResult.LESS,
        )
        self.assertEqual(
            compare_by_value_n(CardSet.parse("AD JS 2D"), CardSet.parse("AS JH 2H")),
            CompareResult.EQUAL,
        )


class HighCardTest(TestCase):
    def test_compare(self):
        self.assertEqual(
            HighCard(CardSet.parse("2C 6H AD")).compare(
                HighCard(CardSet.parse("KD QD 9C"))
            ),
            CompareResult.GREATER,
            "Ace is higher than king",
        )
        # self.assertEqual(
        #     HighCard(CardSet.parse("2C 6H AD")).compare(
        #         HighCard(CardSet.parse("KD QD AC"))
        #     ),
        #     CompareResult.EQUAL,
        #     "Cards other than aces are ignored",
        # )


class PairTest(TestCase):
    def test_wrong(self):
        self.assertRaises(CombinationException, Pair, CardSet.parse("AD 5D KS 2H 4C"))

    def test_recognize(self):
        set = CardSet.parse("AD 5D AS 2H 4C")
        self.assertEqual(Pair(set).combValue, 14)

    def test_compare(self):
        set = CardSet.parse("QD TD QS 2H 4C")
        c = Pair(set)

        self.assertEqual(
            c.compare(HighCard(CardSet.parse("2C 6H AD KD 5D"))),
            CompareResult.GREATER,
            "Pair should be greater than high card",
        )

        self.assertEqual(
            c.compare(Pair(CardSet.parse("AD 5D AS 2H 4C"))),
            CompareResult.LESS,
            "Pair of queens should be weaker than a pair of aces",
        )

        self.assertEqual(
            c.compare(Pair(CardSet.parse("QS 9D QD 2H 4C"))),
            CompareResult.GREATER,
            "Kicker",
        )

        self.assertEqual(
            c.compare(Pair(CardSet.parse("QS TD QD 2H 3C"))),
            CompareResult.GREATER,
            "second kicker",
        )


class TwoPairsTest(TestCase):
    def test_wrong(self):
        self.assertRaises(
            CombinationException, TwoPairs, CardSet.parse("AS JS KC 6D 9D 9C 5D")
        )

    def test_recognize(self):
        tp = TwoPairs(CardSet.parse("KS 6S 7D 2D 2C QH 7C"))
        self.assertTupleEqual(tp.pairValues, (7, 2))

        tp = TwoPairs(CardSet.parse("5D 3D 3H 8D 8S 5C 9C"))
        self.assertTupleEqual(tp.pairValues, (8, 5), "If three pairs picks highest")

        tp = TwoPairs(CardSet.parse("6C 7H 8H KH KS KD 8C"))
        self.assertTupleEqual(
            tp.pairValues, (13, 8), "Full house also counts as two pairs"
        )

    def test_compare(self):
        c = TwoPairs(CardSet.parse("TH 9H 9C 5C TC KD 6D"))

        self.assertEqual(
            c.compare(Pair(CardSet.parse("AC QC 3D 6D AD 7D 2H"))),
            CompareResult.GREATER,
            "Two Pairs is stronger than a pair",
        )

        self.assertEqual(
            c.compare(TwoPairs(CardSet.parse("JH 9H 9C 5C JC KD 6D"))),
            CompareResult.LESS,
            "J is stronger than T",
        )

        self.assertEqual(
            c.compare(TwoPairs(CardSet.parse("TH 4H 4C 5C TC KD 6D"))),
            CompareResult.GREATER,
            "Second pairs of 9 is better than 4",
        )

        self.assertEqual(
            c.compare(TwoPairs(CardSet.parse("TH 9H 9C 5C TC AD 6D"))),
            CompareResult.LESS,
            "Kicker",
        )


# Тестировать тройку не будем, так как она создана таким же образом, как и пара


class StraightTest(TestCase):
    def test_wrong(self):
        self.assertRaises(
            CombinationException, Straight, CardSet.parse("TH 9H 9C 5C TC KD 6D")
        )

    def test_recognize(self):
        st = Straight(CardSet.parse("8C 5H 9S 3H 5S 7H 6D"))
        self.assertEqual(st.highValue, 9)

        st = Straight(CardSet.parse("7S 4S 2H 5H AS QC 3C"))
        self.assertEqual(st.highValue, 5, "Recognizes special case (A2345) correctly")

    def test_compare(self):
        st1 = Straight(CardSet.parse("8C 5H 9S 3H 5S 7H 6D"))
        st2 = Straight(CardSet.parse("7S 4S 2H 5H AS QC 3C"))
        self.assertEqual(st1.compare(st2), CompareResult.GREATER)


class FlushTest(TestCase):
    def test_wrong(self):
        self.assertRaises(
            CombinationException, Flush, CardSet.parse("7S 4S 2H 5H AS QC 3C")
        )

    def test_recognize(self):
        fl = Flush(CardSet.parse("QH 7S TH 7H KC 4H 3H"))
        self.assertEqual(fl.highValue, 12)
        self.assertEqual(fl.suit, Suit.H)

    def test_compare(self):
        fl1 = Flush(CardSet.parse("QH 7S TH 7H KC 4H 3H"))
        fl2 = Flush(CardSet.parse("AH 7S TH 7H KC 4H 3H"))
        self.assertEqual(fl1.compare(fl2), CompareResult.LESS)

        fl2 = Flush(CardSet.parse("QH 7S 9H 7H KC 4H 3H"))
        self.assertEqual(
            fl1.compare(fl2), CompareResult.EQUAL, "Only highest card matters"
        )

        fl2 = Flush(CardSet.parse("QH AS TH 7H KC 4H 3H"))
        self.assertEqual(
            fl1.compare(fl2), CompareResult.EQUAL, "Other cards don't matter"
        )


class FullHouseTest(TestCase):
    def test_wrong(self):
        self.assertRaises(
            CombinationException, FullHouse, CardSet.parse("3S JH AC 3D QH 4H QC")
        )

    def test_recognize(self):
        fh = FullHouse(CardSet.parse("TC 8S 8D 7H 8H TS TH"))
        self.assertEqual(fh.trioValue, 10, "For trio picks better value")
        self.assertEqual(fh.pairValue, 8)

    def test_compare(self):
        fh = FullHouse(CardSet.parse("5D 2S 9D 9S 7C 7S 9H"))
        fh2 = FullHouse(CardSet.parse("5D 2S 8D 8S 7C 7S 8H"))
        self.assertEqual(fh.compare(fh2), CompareResult.GREATER, "Trio first")

        fh2 = FullHouse(CardSet.parse("5D 2S 9D 9S 8C 8S 9H"))
        self.assertEqual(fh.compare(fh2), CompareResult.LESS, "Pair second")


class StraightFlushTest(TestCase):
    def test_wrong(self):
        self.assertRaises(
            CombinationException, StraightFlush, CardSet.parse("4S JC QS KS 4C 7S 2S")
        )

        self.assertRaises(
            CombinationException, StraightFlush, CardSet.parse("AH 5D 6C 2S 3C 4D 7D")
        )

    def test_recognize(self):
        sf = StraightFlush(CardSet.parse("KD 4C 6C 2C 3C 4H 5C"))
        self.assertEqual(sf.highValue, 6)

    def test_compare(self):
        sf1 = StraightFlush(CardSet.parse("KD 4C 6C 2C 3C 4H 5C"))
        sf2 = StraightFlush(CardSet.parse("9H AS QS TS 3H KS JS"))
        self.assertEqual(sf1.compare(sf2), CompareResult.LESS)
