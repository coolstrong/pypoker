from functools import total_ordering
from typing import *
from dataclasses import dataclass, replace
from enum import Enum
from random import randint, sample
from collections.abc import Container
import numpy as np
from numpy import ravel_multi_index, unravel_index


class Suit(Enum):
    S = 0
    C = 1
    D = 2
    H = 3


@total_ordering
@dataclass
class Card:
    suit: Suit
    value: int

    _val_to_hex: ClassVar[dict[int, Optional[int]]] = str.maketrans("TJQKA", "ABCDE")

    @staticmethod
    def parse(cardstr: str):
        return Card(
            suit=Suit[cardstr[1]],
            value=int(cardstr[0].translate(Card._val_to_hex), base=16),
        )

    @staticmethod
    def parse_rus(cardstr: str) -> "Card":
        suits = {"П": "S", "Т": "C", "Б": "D", "Ч": "H"}
        vals = str.maketrans("ЕВДКТ", "ABCDE")
        return Card(
            suit=Suit[suits[cardstr[1]]], value=int(cardstr[0].translate(vals), base=16)
        )

    @staticmethod
    def random(excluding: Container["Card"] = ()) -> "Card":
        while True:
            card = Card(Suit(randint(0, 3)), randint(2, 14))
            if card not in excluding:
                return card

    @staticmethod
    def from_int(raveled: int):
        t = cast(tuple[int, int], unravel_index(raveled, (13, 4)))
        return Card(Suit(t[1]), t[0] + 2)

    def __lt__(self, other: Any) -> bool:
        return (self.value < other.value) or (
            (self.value == other.value) and (self.suit.value < other.suit.value)
        )

    def __str__(self) -> str:
        val = next(
            (
                k
                for k, v in {"T": 10, "J": 11, "Q": 12, "K": 13, "A": 14}.items()
                if v == self.value
            ),
            None,
        ) or str(self.value)

        return f"{val}{self.suit.name}"

    def to_int(self) -> int:
        return int(ravel_multi_index((self.value - 2, self.suit.value), (13, 4)))


class CardSet(Iterable[Card]):
    cards: tuple[Card, ...]

    def __init__(self, cards: Iterable[Card]) -> None:
        self.cards = tuple[Card, ...](sorted(cards, reverse=True))

    def clone(self) -> "CardSet":
        return CardSet(map(lambda card: replace(card), self.cards))

    @property
    def suits(self):
        return tuple[Suit](map(lambda c: c.suit, self.cards))

    @property
    def values(self):
        return tuple[int](map(lambda c: c.value, self.cards))

    @staticmethod
    def parse(handstr: str, cardFactory=Card.parse):
        return CardSet(map(lambda s: cardFactory(s), handstr.split(" ")))

    @staticmethod
    def random(n: int = 5, excluding: Iterable[Card] = ()) -> "CardSet":
        return CardSet(
            map(
                Card.from_int,
                np.random.choice(
                    np.delete(
                        np.arange(52), tuple(map(Card.to_int, excluding))
                    ),
                    n,
                ),
            )
        )

    def __iter__(self):
        return self.cards.__iter__()

    def __str__(self) -> str:
        return " ".join(map(str, self.cards))

    def __len__(self):
        return self.cards.__len__()

    def __contains__(self, __x):
        return self.cards.__contains__(__x)


__all__ = ["Card", "Suit", "CardSet"]
