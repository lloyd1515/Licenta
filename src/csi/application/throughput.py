from dataclasses import dataclass, replace


# Debit pe fereastra glisanta
@dataclass(frozen=True)
class Throughput:
    window_s: float
    total: int = 0
    arrivals: tuple[float, ...] = ()

    # Valideaza fereastra
    def __post_init__(self):
        if self.window_s <= 0:
            raise ValueError(f"window_s trebuie sa fie pozitiv, nu {self.window_s}")

    # Adauga sosiri, intoarce obiect nou
    def add(self, now, count):
        if count < 0:
            raise ValueError(f"count nu poate fi negativ: {count}")
        recent = tuple(t for t in self.arrivals + (now,) * count if now - t <= self.window_s)
        return replace(self, total=self.total + count, arrivals=recent)

    # Pachete pe secunda
    @property
    def per_second(self):
        return len(self.arrivals) / self.window_s
