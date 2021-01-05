from typing import List, Dict, Set


class Imputation:
    def __init__(self, function: callable, keys: [str]):
        self._keys = keys
        self._function = function

    @property
    def keys(self) -> [str]:
        return self._keys

    @property
    def function(self) -> callable:
        return self._function


class Module:
    def __init__(self,
                 location: str,
                 imputations: dict = None,
                 mark_missing: [str] = None):
        self._location = location
        self._imputations = imputations if imputations else dict()
        self._marking_missing = mark_missing if mark_missing else set()

    @property
    def imputations(self) -> Dict[str, List[Imputation]]:
        return self._imputations

    @property
    def location(self) -> str:
        return self._location

    @property
    def mark_missing(self) -> Set[str]:
        return self._marking_missing
