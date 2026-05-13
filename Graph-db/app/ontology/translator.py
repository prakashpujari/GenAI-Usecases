from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml
from rdflib import Graph, RDF, RDFS, OWL


@dataclass
class OntologyMapping:
    labels: dict[str, str] = field(default_factory=dict)
    relationships: dict[str, str] = field(default_factory=dict)
    properties: dict[str, list[str]] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "labels": self.labels,
            "relationships": self.relationships,
            "properties": self.properties,
        }


class OntologyTranslator:
    def __init__(self, override_path: str | None = None) -> None:
        self.overrides = {}
        if override_path and Path(override_path).exists():
            with open(override_path, "r", encoding="utf-8") as fh:
                self.overrides = yaml.safe_load(fh) or {}

    def translate_folder(self, ontology_folder: str) -> OntologyMapping:
        mapping = OntologyMapping()
        folder = Path(ontology_folder)
        for file in folder.glob("*.*"):
            if file.suffix.lower() not in {".ttl", ".rdf", ".owl", ".xml"}:
                continue
            self._translate_file(file, mapping)
        return mapping

    def _apply_override(self, key: str, namespace: str) -> str:
        return self.overrides.get(namespace, {}).get(key, key)

    def _translate_file(self, path: Path, mapping: OntologyMapping) -> None:
        graph = Graph()
        graph.parse(path)

        for cls in graph.subjects(RDF.type, OWL.Class):
            local = cls.split("#")[-1].split("/")[-1]
            mapping.labels[local] = self._apply_override(local, "classes")

        for prop in graph.subjects(RDF.type, OWL.ObjectProperty):
            local = prop.split("#")[-1].split("/")[-1]
            mapping.relationships[local] = self._apply_override(local, "object_properties")

        for prop in graph.subjects(RDF.type, OWL.DatatypeProperty):
            local = prop.split("#")[-1].split("/")[-1]
            mapped = self._apply_override(local, "data_properties")
            for domain in graph.objects(prop, RDFS.domain):
                domain_local = domain.split("#")[-1].split("/")[-1]
                lbl = mapping.labels.get(domain_local, domain_local)
                mapping.properties.setdefault(lbl, [])
                if mapped not in mapping.properties[lbl]:
                    mapping.properties[lbl].append(mapped)

    @staticmethod
    def write_output(mapping: OntologyMapping, output_path: str) -> None:
        target = Path(output_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        payload = mapping.to_dict()
        if target.suffix.lower() in {".yaml", ".yml"}:
            with open(target, "w", encoding="utf-8") as fh:
                yaml.safe_dump(payload, fh, sort_keys=True)
        else:
            with open(target, "w", encoding="utf-8") as fh:
                json.dump(payload, fh, indent=2)
