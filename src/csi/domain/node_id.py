from dataclasses import dataclass

MAX_NODE_ID = 255


# Identitatea nodului, 0-255
@dataclass(frozen=True, order=True)
class NodeId:
    value: int

    # Valideaza tipul si intervalul
    def __post_init__(self):
        if isinstance(self.value, bool) or not isinstance(self.value, int):
            raise TypeError(f"NodeId trebuie sa fie int, nu {type(self.value).__name__}")
        if not 0 <= self.value <= MAX_NODE_ID:
            raise ValueError(f"NodeId trebuie sa fie intre 0 si {MAX_NODE_ID}, nu {self.value}")

    # Afiseaza doar numarul
    def __str__(self):
        return str(self.value)
