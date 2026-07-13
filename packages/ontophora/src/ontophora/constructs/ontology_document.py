from typing import Literal

from pydantic import Field

from ontophora.constructs.base import BaseConstruct
from ontophora.constructs.iri import FullIRI
from ontophora.constructs.ontology import Ontology
from ontophora.constructs.types import PrefixName
from ontophora.reference import Reference


class PrefixDeclaration(BaseConstruct):
    """Declares a prefix mapping used in abbreviated IRIs.

    See: [OWL 2 reference](https://www.w3.org/TR/owl2-syntax/#Functional-Style_Syntax)
    """

    prefix_name: PrefixName
    full_iri: FullIRI
    kind: Literal["Prefix"] = "Prefix"


class OntologyDocument(BaseConstruct):
    """Represents an ontology document with prefix declarations and an ontology payload.

    See: [OWL 2 reference](https://www.w3.org/TR/owl2-syntax/#Ontology_Documents)
    """

    ontology: Reference[Ontology]
    prefix_declarations: list[Reference[PrefixDeclaration]] = Field(default_factory=list)
    kind: Literal["OntologyDocument"] = "OntologyDocument"
