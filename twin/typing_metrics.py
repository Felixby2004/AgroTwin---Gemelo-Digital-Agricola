from dataclasses import dataclass


@dataclass
class TypingMetrics:
    expected_typed_items: int

    correctly_typed_items: int

    incorrectly_typed_items: int

    typing_correctness: float | None