class Attr:
    """ Attribute with computed value and validation """

    def __init__(self, var_type, func=None, modify_type=False):
        self.var_type = var_type
        self.func = func
        self.modify_type = modify_type

    def __set_name__(self, _, name):
        self.name = name

    def __get__(self, instance, _):
        if not instance:
            return self
        return instance.__dict__[self.name]

    def _validate_value(self, value):
        try:
            if self.modify_type:
                return self.var_type(value)
            else:
                if value and not isinstance(value, self.var_type):
                    raise TypeError
                return value
        except Exception:
            raise TypeError(f"Value of field {self.name} is of wrong type: "
                            f"expected {self.var_type.__name__}, but received {type(value).__name__}")

    def __set__(self, instance, value):
        value = self._validate_value(value)
        instance.__dict__[self.name] = self.func(value) if self.func else value


def validate_int(some_int: int):
    if some_int < -1:
        raise ValueError()

    return some_int
