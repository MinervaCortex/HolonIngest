import json
from typing import Any, Dict, List, Tuple
import duckdb
import pyarrow as pa
import pyjsonata
from pydantic import ValidationError

from decoder_gateway import PayloadDecoder
from fingerprint_engine import SchemaRegistry, StructuralFingerprinter
from graph_models import HolonicGraphPayload


class IngestionPipelineEngine:
    """Orchestratore principale del flusso di ingestione, trasformazione e DLQ."""

    def __init__(self, registry: SchemaRegistry):
        self.registry = registry

    def process_incoming_event(
        self, raw_bytes: bytes, content_type: str
    ) -> Dict[str, Any]:
        # 1. Normalizzazione iniziale del formato
        decoded_data = PayloadDecoder.decode(raw_bytes, content_type)

        # 2. Calcolo fingerprint della struttura
        fp = StructuralFingerprinter.compute(decoded_data)

        # 3. Lookup della regola di trasformazione
        jsonata_rule = self.registry.get_mapping(fp)
        if not jsonata_rule:
            return {
                "status": "DLQ_UNRECOGNIZED_SCHEMA",
                "fingerprint": fp,
                "raw_sample": decoded_data,
            }

        # 4. Esecuzione trasformazione JSONata
        transformed_raw = pyjsonata.jsonata(jsonata_rule, decoded_data)
        transformed_dict = json.loads(transformed_raw)
        transformed_dict["ingestion_source_fp"] = fp

        # 5. Validazione finale su schema grafico canonico
        try:
            canonical_graph_event = HolonicGraphPayload(**transformed_dict)
            return {"status": "SUCCESS", "data": canonical_graph_event}
        except ValidationError as err:
            return {
                "status": "DLQ_VALIDATION_FAILED",
                "errors": err.errors(),
                "transformed_data": transformed_dict,
            }


class PythonDataBridge:
    """
    Converte un batch di HolonicGraphPayload in tabelle PyArrow Zero-Copy
    ed esegue il pre-clustering olonico tramite DuckDB.
    """

    @staticmethod
    def build_graph_tables(
        payloads: List[HolonicGraphPayload],
    ) -> Tuple[pa.Table, pa.Table, Any]:
        raw_nodes: List[Dict[str, Any]] = []
        raw_edges: List[Dict[str, Any]] = []

        for p in payloads:
            for n in p.nodes:
                raw_nodes.append(
                    {
                        "node_id": n.id,
                        "label": n.label,
                        "attributes_json": json.dumps(n.attributes),
                        "holon_parent_hint": n.holon_parent_hint,
                        "domain_boundary": n.domain_boundary,
                    }
                )
            for e in p.edges:
                raw_edges.append(
                    {
                        "source_id": e.source_id,
                        "target_id": e.target_id,
                        "rel_type": e.relationship_type,
                        "attributes_json": json.dumps(e.attributes),
                    }
                )

        # 1. Creazione Tabelle PyArrow Zero-Copy
        nodes_table = pa.Table.from_pylist(raw_nodes)
        edges_table = pa.Table.from_pylist(raw_edges)

        # 2. Pre-clustering in Oloni e Sub-Trees tramite DuckDB (Operazione O(1))
        holon_clusters = duckdb.query(
            """
            SELECT 
                holon_parent_hint, 
                COUNT(*) as child_count, 
                list(node_id) as child_nodes,
                list(label) as child_labels
            FROM nodes_table
            WHERE holon_parent_hint IS NOT NULL
            GROUP BY holon_parent_hint
        """
        ).df()

        return nodes_table, edges_table, holon_clusters