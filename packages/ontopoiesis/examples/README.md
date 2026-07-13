# Example ontologies

Source ontologies used by the docs walkthroughs and case studies. Build a
projection from any of them with `ontopoiesis build <file> -o <name>.lbug`.

## Tracked in the repository

These small sources ship with the repository and are ready to build:

| File | Vocabulary |
| --- | --- |
| `dublincore.owl` | Dublin Core metadata terms |
| `foaf.owl` | Friend of a Friend |
| `goslim_generic.owl` | GO generic subset (slim) |
| `SCTO.owl` | Swiss Clinical Trial Organisation ontology |
| `schemaorg.rdf` | schema.org (RDF/XML; convert first, e.g. `robot convert`) |
| `sweetAll.owl` | SWEET Earth and environmental science |

## Fetch as needed

The full ontologies below are too large to track. Download them from their
upstreams before running the walkthroughs that use them:

| File | Download |
| --- | --- |
| `chebi.owl` | <http://purl.obolibrary.org/obo/chebi.owl> |
| `fma.owl` | <http://purl.obolibrary.org/obo/fma.owl> |
| `go.owl` | <http://purl.obolibrary.org/obo/go.owl> |
| `hp.owl` | <http://purl.obolibrary.org/obo/hp.owl> |
| `uberon.owl` | <http://purl.obolibrary.org/obo/uberon.owl> |

For example:

```bash
curl -L http://purl.obolibrary.org/obo/go.owl -o go.owl
```

Most sources come from the
[Open Biological and Biomedical Ontology Foundry](https://obofoundry.org/).
