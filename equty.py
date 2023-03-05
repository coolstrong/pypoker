from typing import Collection, Iterable
from card import Card, CardSet
import numpy as np
from combinations import Combination, CompareResult


def compute_equity(
    hand: Collection[Card], table: Collection[Card], num_of_players: int, n=5000
) -> float:
    def cards_to_ndarray(cards: Iterable[Card]):
        return np.fromiter(map(Card.to_int, cards), int)

    existingCards = np.concatenate(
        tuple(map(cards_to_ndarray, (hand, table)))
    )

    cardpool = np.delete(np.arange(52), existingCards)

    n_wins = 0
    for i in range(n):
        cursor = 0
        deck = np.random.permutation(cardpool)

        def next_cards(n: int) -> tuple[Card, ...]:
            nonlocal cursor
            r = tuple(map(Card.from_int, deck[cursor : cursor + n]))
            cursor += n
            return r

        rnd_table = (*table, *next_cards(5 - len(table)))
        other_hands = tuple(map(lambda _: next_cards(2), range(num_of_players - 1)))
        my_comb = Combination.find_highest(CardSet((*rnd_table, *hand)))
        other_combs = map(
            lambda player_hand: Combination.find_highest(
                CardSet((*player_hand, *rnd_table))
            ),
            other_hands,
        )

        if all(
            map(
                lambda otherComb: my_comb.compare(otherComb) == CompareResult.GREATER,
                other_combs,
            )
        ):
            n_wins += 1

    return n_wins / n
