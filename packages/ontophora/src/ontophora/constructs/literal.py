from typing import Literal

from ontophora.constructs.base import BaseConstruct
from ontophora.constructs.datatype import Datatype
from ontophora.constructs.types import LanguageTag, QuotedString
from ontophora.reference import Reference


class StringLiteralNoLanguage(BaseConstruct):
    """A string literal without a language tag.

    See: [OWL 2 reference](https://www.w3.org/TR/owl2-syntax/#Literals)
    """

    quoted_string: QuotedString
    kind: Literal["StringLiteralNoLanguage"] = "StringLiteralNoLanguage"


class StringLiteralWithLanguage(BaseConstruct):
    """A string literal annotated with a language tag.

    See: [OWL 2 reference](https://www.w3.org/TR/owl2-syntax/#Literals)
    """

    quoted_string: QuotedString
    language_tag: LanguageTag
    kind: Literal["StringLiteralWithLanguage"] = "StringLiteralWithLanguage"


class TypedLiteral(BaseConstruct):
    """A literal value tagged with an explicit datatype IRI.

    See: [OWL 2 reference](https://www.w3.org/TR/owl2-syntax/#Literals)
    """

    lexical_form: QuotedString
    datatype: Reference[Datatype]
    kind: Literal["TypedLiteral"] = "TypedLiteral"


LiteralUnion = StringLiteralNoLanguage | StringLiteralWithLanguage | TypedLiteral
