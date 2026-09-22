import hashlib
import json
from typing import Any, Dict, Optional, Union


class StructuralFingerprinter:
    """
    Genera l'impronta digitale dello schema analizzando esclusivamente
    la topologia e la gerarchia delle chiavi, ignorando i valori.
    """

    @classmethod
    def compute(cls, data: Union[Dict, list]) -> str:
        structure = cls._extract_topology(data)
        serialized = json.dumps(structure, sort_keys=True)
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()

    @classmethod
    def _extract_topology(cls, obj: Any) -> Any:
        if isinstance(obj, dict):
            return sorted((k, cls._extract_topology(v)) for k, v in obj.items())
        elif isinstance(obj, list):
            return [cls._extract_topology(obj[0])] if obj else []
        return type(obj).__name__


class SchemaRegistry:
    """
    Registro in-memory/Redis che associa gli Hash delle strutture
    alle relative regole di trasformazione JSONata.
    """

    def __init__(self):
        self._registry: Dict[str, str] = {}

    def register_mapping(self, fingerprint: str, jsonata_rule: str) -> None:
        self._registry[fingerprint] = jsonata_rule

    def get_mapping(self, fingerprint: str) -> Optional[str]:
        return self._registry.get(fingerprint)

    def is_registered(self, fingerprint: str) -> bool:
        return fingerprint in self._registry