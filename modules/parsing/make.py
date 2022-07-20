from .expressions.primary_expression import PrimaryExpression
from .expressions.postfix_expression import PostfixExpression
from .expressions.prefix_deviation_expression import PrefixDeviationExpression
from .expressions.exponential_expression import ExponentialExpression
from .expressions.unary_expression import UnaryExpression
from .expressions.cast_expression import CastExpression
from .expressions.multiplicative_expression import MultiplicativeExpression
from .expressions.additive_expression import AdditiveExpression
from .expressions.shift_expression import ShiftExpression
from .expressions.bitwise_and_expression import BitwiseAndExpression
from .expressions.bitwise_xor_expression import BitwiseXorExpression
from .expressions.bitwise_or_expression import BitwiseOrExpression
from .expressions.comparative_expression import ComparativeExpression
from .expressions.logical_not_expression import LogicalNotExpression
from .expressions.logical_and_expression import LogicalAndExpression
from .expressions.logical_or_expression import LogicalOrExpression
from .expressions.conditional_expression import ConditionalExpression
from .expressions.assignment_expression import AssignmentExpression
from .expressions.expression import Expression
from .declarations.type_name import TypeName
from .declarations.non_reference_type_name import NonReferenceTypeName
from .declarations.specifiers_and_qualifiers import SpecifiersAndQualifiers
from .declarations.type_qualifier import TypeQualifier
from .declarations.type_specifier import TypeSpecifier
from .declarations.ranged_generator import RangedGenerator
from .declarations.iterative_generator import IterativeGenerator
from .declarations.designated_initializer import DesignatedInitializer
from .declarations.initializer_compound_literal import InitializerCompoundLiteral
from .declarations.initializer import Initializer
from .declarations.safe_initializer import SafeInitializer
from .declarations.element_declaration import ElementDeclaration
from .declarations.variable_declaration import VariableDeclaration
from .declarations.declaration import Declaration
from .statements.alias_statement import AliasStatement
from .statements.static_assert_statement import StaticAssertStatement
from .statements.statement import Statement
from .statements.file_statement import FileStatement

CLASSES = (
    PrimaryExpression,
    PostfixExpression,
    PrefixDeviationExpression,
    ExponentialExpression,
    UnaryExpression,
    CastExpression,
    MultiplicativeExpression,
    AdditiveExpression,
    ShiftExpression,
    BitwiseAndExpression,
    BitwiseXorExpression,
    BitwiseOrExpression,
    ComparativeExpression,
    LogicalNotExpression,
    LogicalAndExpression,
    LogicalOrExpression,
    ConditionalExpression,
    AssignmentExpression,
    Expression,
    TypeName,
    NonReferenceTypeName,
    SpecifiersAndQualifiers,
    TypeQualifier,
    TypeSpecifier,
    InitializerCompoundLiteral,
    Initializer,
    SafeInitializer,
    ElementDeclaration,
    RangedGenerator,
    IterativeGenerator,
    DesignatedInitializer,
    VariableDeclaration,
    Declaration,
    AliasStatement,
    StaticAssertStatement,
    Statement,
    FileStatement
)

CONSTRUCT_MAP = {cls.__name__: cls.construct for cls in CLASSES}
CONSTRUCT_MAP["ConstantExpression"] = CONSTRUCT_MAP["ConditionalExpression"]

# from ..node import Node

# class Statement(Node):
#     @classmethod
#     def construct(cls, children):
#         pass
#
