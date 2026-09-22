import hashlib
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


def generate_urn(entity_type: str, *natural_keys: str) -> str:
    """
    Genera un URN deterministico per Entity Resolution automatica.
    Evita la creazione di duplicati all'interno del grafo.
    """
    raw_key = ":".join(
        [entity_type.lower()] + [str(k).strip().lower() for k in natural_keys if k]
    )
    key_hash = hashlib.sha256(raw_key.encode("utf-8")).hexdigest()[:12]
    return f"urn:{entity_type.lower()}:{key_hash}"


class GraphNode(BaseModel):
    """Rappresenta un singolo nodo/entità nel grafo."""

    id: str  # URN deterministico (es: "urn:sensore:a1b2c3d4e5f6")
    label: str  # Categoria (es: "Sensore", "Azienda", "Contratto")
    attributes: Dict[str, Any] = Field(default_factory=dict)

    # Context Hints per la strutturazione in Oloni
    holon_parent_hint: Optional[str] = (
        None  # URN dell'olone genitore (es: "urn:contratto:xyz")
    )
    domain_boundary: Optional[str] = None  # Categoria di isolamento del sotto-albero


class GraphEdge(BaseModel):
    """Rappresenta un arco diretto tra nodi o tra nodi e oloni."""

    source_id: str
    target_id: str
    relationship_type: str  # es: "MONITORA", "INTESTATO_A", "PARTE_DI"
    attributes: Dict[str, Any] = Field(default_factory=dict)


class HolonicGraphPayload(BaseModel):
    """
    Contratto di output canonico e unificato emesso dall'ingestione.
    Pronto per l'elaborazione immediata da parte del Graph Agent.
    """

    ingestion_source_fp: str
    nodes: List[GraphNode]
    edges: List[GraphEdge]