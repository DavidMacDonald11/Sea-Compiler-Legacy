from .initializer import Initializer

class SafeInitializer(Initializer):
    @classmethod
    def construct(cls, children):
        return cls.full_construct(children, "LogicalOrExpression")
