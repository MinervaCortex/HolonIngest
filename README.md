🔷 HolonIngest
> \*\*Zero-Code Dynamic Ingestion Engine for Holonic Knowledge Graphs.\*\*  
> Convert any heterogeneous payload (XML, CSV, JSON, Webhooks) into zero-copy PyArrow graph structures using structural fingerprinting and JSONata.

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688.svg)](https://fastapi.tiangolo.com)
[![PyArrow](https://img.shields.io/badge/PyArrow-Enabled-orange.svg)](https://arrow.apache.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
---
🚨 **The Problem**

Traditional ETL pipelines break when new API sources change their JSON schemas or send raw XML/CSV. Re-deploying parsers for every new IoT sensor, contract format, or HR system creates engineering debt and bloats your graph database with duplicate nodes.

💡 **The Solution**

**HolonIngest** sits between your raw data sources and your Graph AI/Workers:
**Normalizes** raw bytes (JSON, XML, CSV) on the fly.
**Fingerprints** payload topology using Structural Hashing (SHA256).
**Transforms** data using dynamic JSONata rules (no code deploy needed).
**Outputs** PyArrow Node/Edge tables pre-clustered for Holonic Graphs ($O(1)$ sub-tree grouping).

---

🚀 **Quickstart (30 Seconds)**
```bash
pip install holoningest
holoningest-server --port 8000

```
Send any payload:
```bash
curl -X POST "http://localhost:8000/api/v1/ingest" \\
     -H "Content-Type: application/xml" \\
     -d '<sensor><id>S-101</id><val>42.1</val></sensor>'

```
If the payload layout is unknown, HolonIngest sends it to the Dead Letter Queue (DLQ) with its structural hash:
```json
{
  "status": "DLQ\_UNRECOGNIZED\_SCHEMA",
  "fingerprint": "a1b2c3d4e5..."
}

```
Add a JSONata rule to the registry for that hash, and you're live. No restarts required.
---
📊 Architecture & Benchmarks
```mermaid
flowchart TD;
    subgraph Ingestion["1. Ingestion Layer"]
        A["Unpredictable Sources<br/>(REST, SOAP, CSV, XML)"] --> B["Normalizer Gateway"]
    end

    subgraph CoreEngine["2. Processing & Mapping"]
        B --> C["Structural Fingerprinter"]
        C --> D{"Schema Found<br/>in Registry?"}
        D -- Yes --> E["JSONata Transformer"]
        D -- No --> DLQ["⚠️ Dead Letter Queue (DLQ)<br/><i>Store raw payload & hash</i>"]
    end

    subgraph GraphOutput["3. Graph Export"]
        E --> F["Pydantic V2 Validation"]
        F --> G["PyArrow Engine"]
        G --> H1[("Nodes Table")]
        G --> H2[("Edges Table")]
        G --> H3["Holon Clusters<br/><i>(DuckDB Sub-trees)</i>"]
    end

    style DLQ fill:#f8d7da,stroke:#842029,stroke-width:1.5px,color: black
    style H3 fill:#d1e7dd,stroke:#0f5132,stroke-width:2px, color: black
```
Latency: < 8ms per request (FastAPI + Pydantic V2 Rust Core)
Memory: Zero-copy transfer to Polars / DuckDB / Kuzu Graph DB via PyArrow
```
