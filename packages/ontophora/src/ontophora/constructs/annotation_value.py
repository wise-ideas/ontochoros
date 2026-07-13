from ontophora.constructs.individual import AnonymousIndividual
from ontophora.constructs.iri import IRI
from ontophora.constructs.literal import LiteralUnion
from ontophora.reference import Reference

AnnotationValue = Reference[LiteralUnion | AnonymousIndividual] | IRI
