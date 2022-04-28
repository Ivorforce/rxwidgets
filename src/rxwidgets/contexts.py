from dataclasses import dataclass


@dataclass
class AnyContext:
    count: int = 0

    def __enter__(self):
        self.count += 1

    def __exit__(self, *args, **kwargs):
        self.count -= 1

    def __bool__(self):
        return bool(self.count)
