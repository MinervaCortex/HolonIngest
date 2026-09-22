import csv
import io
import json
from typing import Any, Dict, Union
import xmltodict
from fastapi import FastAPI, HTTPException, Request, Response, status

app = FastAPI(title="Enterprise Dynamic Ingestion Gateway")


class PayloadDecoder:
    """Decodifica formati binari o testuali eterogenei in strutture ad albero Python."""

    @staticmethod
    def decode(raw_content: bytes, content_type: str) -> Union[Dict[str, Any], list]:
        ct = content_type.lower()

        if "json" in ct:
            return json.loads(raw_content.decode("utf-8"))

        elif "xml" in ct:
            parsed = xmltodict.parse(raw_content)
            # Normalizzazione: rimuove il nodo radice XML per linearizzare la struttura
            return next(iter(parsed.values()))

        elif "csv" in ct or "text/plain" in ct or "tab-separated-values" in ct:
            text = raw_content.decode("utf-8")
            delimiter = "\t" if "tsv" in ct or "\t" in text.splitlines()[0] else ","
            reader = csv.DictReader(io.StringIO(text), delimiter=delimiter)
            return list(reader)

        raise ValueError(f"Content-type non supportato: {content_type}")


@app.post("/api/v1/ingest", status_code=status.HTTP_202_ACCEPTED)
async def ingest_raw_event(request: Request):
    """
    Endpoint di ingestione agnostico. Accetta qualsiasi formato di payload.
    """
    content_type = request.headers.get("content-type", "application/json")
    raw_body = await request.body()

    if not raw_body:
        raise HTTPException(
            status_code=400, detail="Il body della richiesta non può essere vuoto."
        )

    try:
        decoded_payload = PayloadDecoder.decode(raw_body, content_type)
        return {
            "status": "received",
            "content_type": content_type,
            "data_sample": decoded_payload,
        }
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Errore durante la decodifica del payload: {str(e)}"
        )