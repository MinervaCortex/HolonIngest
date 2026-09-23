## <p align="center">🔷 HolonIngest </p>

<p align="center"><font color="red"><b>Zero-Code Dynamic Ingestion Engine for Holonic Knowledge Graphs.</b></font> </p> 
<p align="center"><font color="red">Convert any heterogeneous payload (XML, CSV, JSON, Webhooks) into zero-copy PyArrow graph structures using structural fingerprinting and JSONata.</font></p>
</p>

<p align="center">
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/python-3.11+-blue.svg" alt="Python 3.11+"></a>
  <a href="https://fastapi.tiangolo.com"><img src="https://img.shields.io/badge/FastAPI-0.100+-009688.svg" alt="FastAPI"></a>
  <a href="https://arrow.apache.org/"><img src="https://img.shields.io/badge/PyArrow-Enabled-green.svg" alt="PyArrow"></a>
  <a href="https://opensource.org/licenses/Apache2.0"><img src="https://img.shields.io/badge/License-Apache2.0-yellow.svg" alt="License: Apache2.o"></a>
</p> 

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
pip install git+https://github.com/your-username/holoningest.git
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
-  "status": "UNRECOGNIZED SCHEMA",
  "fingerprint": "a1b2c3d4e5..."
}

```
Add a JSONata rule to the registry for that hash, and you're live. No restarts required.
---
📊 Architecture & Benchmarks
```mermaid
flowchart TD;
    subgraph Ingestion[" "]
        direction TB
        T1["<b>1. Ingestion Layer</b>"]
        A["Unpredictable Sources<br/>(REST, SOAP, CSV, XML)"] --> B["Normalizer Gateway"]
        
        %% Force T1 to be above A
        T1 ~~~ A
    end

    subgraph CoreEngine[" "]
        direction TB
        T2["<b>2. Processing & Mapping</b>"]
        B --> C["Structural Fingerprinter"]
        C --> D{"Schema Found<br/>in Registry?"}
        D -- Yes --> E["JSONata Transformer"]
        D -- No --> DLQ["⚠️ Dead Letter Queue (DLQ)<br/><i>Store raw payload & hash</i>"]
        
        %% Force T2 to be above C
        T2 ~~~ C
    end

    subgraph GraphOutput[" "]
        direction TB
        T3["<b>3. Graph Export</b>"]
        E --> F["Pydantic V2 Validation"]
        F --> G["PyArrow Engine"]
        G --> H1[("Nodes Table")]
        G --> H2[("Edges Table")]
        
        %% Force T3 to be above F
        T3 ~~~ F
    end

    subgraph End[" "]
        direction TB
        T4["<b>4. Holonification</b>"]
        G --> H3["Holon Clusters<br/><i>(DuckDB Sub-trees)</i>"]
        
        %% Force T4 to be above H3
        T4 ~~~ H3
    end

    %% Hide borders and backgrounds for title nodes
    style T1 fill:none,stroke:none
    style T2 fill:none,stroke:none
    style T3 fill:none,stroke:none
    style T4 fill:none,stroke:none

    %% Custom node styles
    style DLQ fill:#f8d7da,stroke:#842029,stroke-width:1.5px,color: black
    style H3 fill:#d1e7dd,stroke:#0f5132,stroke-width:2px,color: black
```
Latency: < 8ms per request (FastAPI + Pydantic V2 Rust Core)
Memory: Zero-copy transfer to Polars / DuckDB / Kuzu Graph DB via PyArrow
```
