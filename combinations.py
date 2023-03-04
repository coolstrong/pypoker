from abc import abstractmethod
from enum import Enum
from typing import (
    Any,
    Callable,
    ClassVar,
    Iterable,
    Literal,
    Optional,
    Type,
    TypeAlias,
    cast,
)
from collections import OrderedDict, Counter
from itertools import islice
from functools import partial

from utils.assert_utils import assert_expr
from utils.math import sgn
from card import Card, CardSet, Suit


# Перечисление, содержащее результат сравнения - удобно в использовании,
# и напрямую конвертируется в числа
class CompareResult(Enum):
    LESS = -1
    EQUAL = 0
    GREATER = 1

    @staticmethod
    def from_int(n: int) -> "CompareResult":
        return CompareResult(sgn(n))


# Словарь всех комбинаций
_combinations = OrderedDict[str, Type["Combination"]]()


class CombinationException(Exception):
    """Исключение, вызываемое при попытке
    создания комбинации из неподходящих карт."""

    pass


class CombinationMetaclass(type):
    """Метакласс (класс, порождающие другие классы) для комбинаций - автоматически записывает
    все создаваемые субклассы Combination в словарь."""

    def __new__(cls, clsname: str, bases: tuple[type, ...], attrs: dict[str, Any]):
        newType = type.__new__(cls, clsname, bases, attrs)
        if clsname != "Combination" and Combination in bases:
            _combinations[attrs["name"]] = newType  # type: ignore
        return newType


class Combination(metaclass=CombinationMetaclass):
    """Базовый абстрактный класс для всех комбинаций."""

    Comparator: TypeAlias = Callable[[CardSet, CardSet], CompareResult]
    """Тип функции, сравнивающей два набора карт"""

    list: ClassVar = _combinations

    value: ClassVar[int]
    name: ClassVar[str]

    _set: CardSet

    @abstractmethod
    def compare(self, other: "Combination") -> CompareResult:
        """Абстрактный метод для реализации потомками"""
        ...

    def __init__(self, set: CardSet):
        self._set = set

    def _compare_pipeline(
        self, other: "Combination", *comparators: Comparator
    ) -> CompareResult:
        """'Конвеер' для сравнения комбинаций - сначала идет сравнение
        по стоимости самой комбинации (value), затем - по правилам, специфичной
        для каждой комбинации и указанным в ее реализации."""

        # Клонируем наборы карт для безопасного изменения в дальнейшем
        firstSet, secondSet = self._set.clone(), other._set.clone()

        # перебираем компараторы
        for comparator in (
            cast(
                Combination.Comparator,
                lambda _1, _2: compare_ints(self.value, other.value),
            ),
            *comparators,
        ):
            result = comparator(firstSet, secondSet)

            # если компаратор решает, что комбинации не равны, то вовращаем результат;
            # иначе - переходим к следующему
            if result != CompareResult.EQUAL:
                return result

        # если все компараторы отработали и вернули, что комбинации равны, то они
        # действительно равны
        return CompareResult.EQUAL

    @staticmethod
    def find_highest(set: CardSet) -> "Combination":
        """Метод для нахождения лучшей комбинации для данного набора карт"""
        return next(
            filter(
                lambda c: c != None,
                map(
                    lambda Comb: Comb.try_make(set), reversed(Combination.list.values())
                ),
            )
        )

    @classmethod
    def try_make(Class, set: CardSet):
        try:
            return Class(set)
        except CombinationException:
            return None
        except Exception as e:
            raise e


def apply_to_both(mutator: Callable[[CardSet], CompareResult]):
    """Декоратор для функций-мутаторов (преобразующих набор карт каким-то образом), возвращающий
    функцию, применяющую данный мутатор к обоим наборам."""

    def new_mutator(set1: CardSet, set2: CardSet):
        mutator(set1)
        mutator(set2)
        return CompareResult.EQUAL

    return new_mutator


def compare_ints(int1: int, int2: int) -> CompareResult:
    return CompareResult.from_int(int1 - int2)


def compare_by_value_n(
    cards1: Iterable[Card],
    cards2: Iterable[Card],
    start: int = 0,
    n: Optional[int] = None,
) -> CompareResult:
    """Компаратор, сравнивающий наборы по первым n картам."""

    for card1, card2 in zip(islice(cards1, start, n), cards2):
        r = compare_ints(card1.value, card2.value)
        if r != CompareResult.EQUAL:
            return r

    return CompareResult.EQUAL


def remove_value_from_set(value: int):
    """Функция, создающая мутатор для удаления карт определенного значения из набора."""

    @apply_to_both
    def mutator(set: CardSet):
        set.cards = tuple(filter(lambda c: c.value != value, set.cards))

    return mutator


def produce_combination(combinationValue: int, n: int, combinationName: str):
    """Функция, производящая класс комбинации, состоящей из n одинаковых карт (пара, тройка, каре)"""

    class MatchingValueCombination(Combination):
        value: ClassVar = combinationValue
        name: ClassVar = combinationName

        combValue: int

        def __init__(self, set: CardSet):
            super().__init__(set)
            try:
                self.combValue = next(
                    (k for k, v in Counter(set.values).items() if v >= n)
                )
            except StopIteration:
                raise CombinationException
            except Exception as e:
                raise e

        def compare(self, other: "Combination"):
            return self._compare_pipeline(
                other,
                lambda _1, _2: compare_ints(
                    self.combValue,
                    cast(MatchingValueCombination, other).combValue,
                ),
                remove_value_from_set(self.combValue),
                partial(compare_by_value_n, n=5 - n),
            )

    MatchingValueCombination.__name__ = combinationName

    return MatchingValueCombination


# поскольку все созданные комбинации записываются метаклассом в список,
# создавать их надо строго в порядке возрастания


class HighCard(Combination):
    value: ClassVar[int] = 1
    name: ClassVar[str] = "High Card"

    def __init__(self, set: CardSet):
        super().__init__(set)

    def compare(self, other: Combination):
        return self._compare_pipeline(other, partial(compare_by_value_n, n=5))


Pair = produce_combination(combinationValue=2, n=2, combinationName="Pair")


class TwoPairs(Combination):
    value: ClassVar[int] = 3
    name: ClassVar[str] = "Two Pairs"

    pairValues: tuple[int, int]

    def __init__(self, set: CardSet):
        super().__init__(set)
        vals = tuple(
            map(
                lambda entry: entry[0],
                filter(lambda entry: entry[1] >= 2, Counter(set.values).items()),
            )
        )
        if len(vals) < 2:
            raise CombinationException

        # берем самые старшие пары
        self.pairValues = cast(tuple[int, int], tuple(sorted(vals, reverse=True))[:2])

    def compare(self, other: Combination):
        def compare_values(n: Literal[0, 1]):
            return lambda _1, _2: compare_ints(
                self.pairValues[n],
                cast(TwoPairs, other).pairValues[n],
            )

        return self._compare_pipeline(
            other,
            compare_values(0),
            compare_values(1),
            remove_value_from_set(self.pairValues[0]),
            remove_value_from_set(self.pairValues[1]),
            partial(compare_by_value_n, n=1),
        )


ThreeOfAKind = produce_combination(
    combinationValue=4, n=3, combinationName="Three of a Kind"
)


class Straight(Combination):
    value: ClassVar[int] = 5
    name: ClassVar[str] = "Straight"

    highValue: int
    """Значение старшей карты"""

    def __init__(self, set: CardSet):
        super().__init__(set)
        for i in range(len(set.cards) - 4):
            currentValue = set.values[i]

            # если 5 карт идут подряд (range())
            if set.values[i : i + 5] == tuple(
                range(currentValue, currentValue - 5, -1)
            ):
                self.highValue = currentValue
                return

        # Особый случай A2345
        if all(map(lambda v: v in set.values, (14, 2, 3, 4, 5))):
            self.highValue = 5
            return

        raise CombinationException

    def compare(self, other: Combination):
        return self._compare_pipeline(
            other,
            lambda _1, _2: compare_ints(
                self.highValue,
                cast(Straight, other).highValue,
            ),
        )


class Flush(Combination):
    value: ClassVar[int] = 6
    name: ClassVar[str] = "Flush"

    suit: Suit
    highValue: int
    """Старшинство флеша определяется по одной старшей карте"""

    def __init__(self, set: CardSet):
        super().__init__(set)

        suit = next((k for k, v in Counter(set.suits).items() if v == 5), None)
        if not suit:
            raise CombinationException

        self.suit = suit
        self.highValue = next(filter(lambda c: c.suit == suit, set.cards)).value

    def compare(self, other: Combination):
        return self._compare_pipeline(
            other,
            lambda _1, _2: compare_ints(self.highValue, cast(Flush, other).highValue),
        )


class FullHouse(Combination):
    value: ClassVar[int] = 7
    name: ClassVar[str] = "Full House"

    trioValue: int
    pairValue: int

    def __init__(self, set: CardSet):
        super().__init__(set)

        counter = Counter(set.values)

        def find_cards_by_count(value: int) -> int:
            return next(k for k, v in counter.items() if v >= value)

        try:
            self.trioValue = find_cards_by_count(3)
            del counter[self.trioValue]
            self.pairValue = find_cards_by_count(2)
        except StopIteration:
            raise CombinationException
        except Exception as e:
            raise e

    def compare(self, other: "Combination") -> CompareResult:
        return self._compare_pipeline(
            other,
            lambda _1, _2: compare_ints(
                self.trioValue, cast(FullHouse, other).trioValue
            ),
            lambda _1, _2: compare_ints(
                self.pairValue, cast(FullHouse, other).pairValue
            ),
        )


FourOfAKind = produce_combination(
    combinationValue=8, n=4, combinationName="Four of a Kind"
)


class StraightFlush(Combination):
    value: ClassVar[int] = 8
    name: ClassVar[str] = "Straight Flush"

    highValue: int

    def __init__(self, set: CardSet):
        super().__init__(set)

        flush = Flush(set)
        straight = Straight(
            CardSet(filter(lambda c: c.suit == flush.suit, set.clone()))
        )
        self.highValue = straight.highValue
        if self.highValue == 14:
            self.name = "Flush Royale" #type: ignore

    def compare(self, other: "Combination") -> CompareResult:
        return self._compare_pipeline(
            other,
            lambda _1, _2: compare_ints(
                self.highValue, cast(StraightFlush, other).highValue
            ),
        )
