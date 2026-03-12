from __future__ import annotations

import argparse

from app.ontology.translator import OntologyTranslator


def main() -> None:
    parser = argparse.ArgumentParser(description="Translate OWL/RDF ontology into LPG mapping")
    parser.add_argument("--input", required=True, help="Ontology folder path")
    parser.add_argument("--output", required=True, help="Output JSON/YAML file")
    parser.add_argument("--overrides", required=False, help="YAML override file")
    args = parser.parse_args()

    translator = OntologyTranslator(args.overrides)
    mapping = translator.translate_folder(args.input)
    translator.write_output(mapping, args.output)


if __name__ == "__main__":
    main()
