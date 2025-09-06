class ParseContext:
    def __init__(self, in_loop: bool = False, in_function: bool = False):
        self.in_loop = in_loop
        self.in_function = in_function

    def child(self, *, in_loop=None, in_function=None):
        return ParseContext(
            in_loop=self.in_loop if in_loop is None else in_loop,
            in_function=self.in_function if in_function is None else in_function,
        )

__all__ = ["ParseContext"]

