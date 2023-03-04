from functools import total_ordering
from typing import *
from dataclasses import dataclass, replace
from enum import Enum
from random import randint
from collections.abc import Container


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
    def random(n: int = 5, excluding: Container[Card] = ()) -> "CardSet":
        # set: list[Card] = []
        # for i in range(n):
            # set.append(Card.random(excluding=(*excluding, *set)))
        return CardSet(Card.random(excluding) for i in range(n))

    def __iter__(self):
        return iter(self.cards)
    
    def __str__(self) -> str:
        return " ".join(map(str, self.cards))


__all__ = ["Card", "Suit", "CardSet"]
