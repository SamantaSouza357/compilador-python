class StatementHandler:
    def can_handle(self, parser, ctx=None) -> bool:
        raise NotImplementedError

    def parse(self, parser, ctx=None):
        raise NotImplementedError

__all__ = ["StatementHandler"]
