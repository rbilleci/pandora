from abc import ABC


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


class Field(ABC):
    def __init__(self, imputations: [Imputation], mark_missing: bool):
        self._mark_missing = mark_missing
        self._imputations = imputations

    @property
    def imputations(self) -> [Imputation]:
        return self._imputations

    @property
    def mark_missing(self) -> bool:
        return self._mark_missing


class Date(Field):
    def __init__(self, imputations: [Imputation] = None, mark_missing=False):
        super().__init__(imputations, mark_missing)


class Ordinal(Field):
    def __init__(self, minimum, maximum, imputations: [Imputation] = None, mark_missing=False):
        super().__init__(imputations, mark_missing)
        self._minimum = minimum
        self._maximum = maximum

    @property
    def minimum(self):
        return self._minimum

    @property
    def maximum(self):
        return self._maximum


class Numeric(Field):
    def __init__(self, minimum, maximum, imputations: [Imputation] = None, mark_missing=False):
        super().__init__(imputations, mark_missing)
        self._minimum = minimum
        self._maximum = maximum

    @property
    def minimum(self):
        return self._minimum

    @property
    def maximum(self):
        return self._maximum


class Nominal(Field):
    def __init__(self, imputations: [Imputation] = None, mark_missing=False):
        super().__init__(imputations, mark_missing)


class Boolean(Field):
    def __init__(self, imputations: [Imputation] = None, mark_missing=False):
        super().__init__(imputations, mark_missing)
