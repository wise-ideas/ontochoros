from typing import Literal

from pydantic import Field

from ontophora.constructs.annotation import Annotation
from ontophora.constructs.base import BaseConstruct
from ontophora.constructs.iri import IRI
from ontophora.reference import Reference


class DirectlyImportsDocument(BaseConstruct):
    """Declares an ontology document import by IRI.

    See: [OWL 2 reference](https://www.w3.org/TR/owl2-syntax/#Imports)
    """

    iri: IRI
    kind: Literal["Import"] = "Import"


class Ontology(BaseConstruct):
    """Represents an OWL ontology: identifiers, imports, annotations, and axioms.

    See: [OWL 2 reference](https://www.w3.org/TR/owl2-syntax/#Ontologies)
    """

    ontology_iri: IRI | None = None
    version_iri: IRI | None = None
    directly_imports_documents: set[Reference[DirectlyImportsDocument]] = Field(default_factory=set)
    ontology_annotations: set[Reference[Annotation]] = Field(default_factory=set)
    axioms: set[Reference[Literal["Axiom"]]] = Field(default_factory=set)
    kind: Literal["Ontology"] = "Ontology"
