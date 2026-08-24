"""Registration and lookup for optional domain adapters."""

from __future__ import annotations

from collections.abc import Iterable, Iterator

from .protocol import DomainAdapter


class DomainRegistry:
    def __init__(self, adapters: Iterable[DomainAdapter] = ()) -> None:
        self._adapters: dict[str, DomainAdapter] = {}
        for adapter in adapters:
            self.register(adapter)

    def register(self, adapter: DomainAdapter, *, replace: bool = False) -> None:
        name = adapter.name.strip().lower()
        if not name:
            raise ValueError("Domain adapter names cannot be empty.")
        if name in self._adapters and not replace:
            raise ValueError(f"Domain adapter already registered: {name}")
        self._adapters[name] = adapter

    def get(self, name: str) -> DomainAdapter:
        key = name.strip().lower()
        try:
            return self._adapters[key]
        except KeyError as exc:
            choices = ", ".join(self.names()) or "none"
            raise KeyError(f"Unknown domain {name!r}; available domains: {choices}") from exc

    def names(self) -> tuple[str, ...]:
        return tuple(sorted(self._adapters))

    def __iter__(self) -> Iterator[DomainAdapter]:
        for name in self.names():
            yield self._adapters[name]


domains = DomainRegistry()
