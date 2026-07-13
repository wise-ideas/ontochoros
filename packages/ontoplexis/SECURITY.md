# Security Policy

## Supported versions

Only the latest release on [PyPI](https://pypi.org/project/ontoplexis/)
receives fixes.

## Reporting a vulnerability

Please do not open a public issue for suspected vulnerabilities. Report them
privately via
[GitHub security advisories](https://github.com/wise-ideas/ontotheke/security/advisories/new)
or by email to ell.wise@gmail.com.

Note that `Ontology.from_owlxml` hands its input straight to the Python
stdlib XML parser, which is not hardened against entity-expansion attacks;
for untrusted documents use `Ontology.from_document`, which routes through
OWLAPI first. This is documented behavior, not a vulnerability.
