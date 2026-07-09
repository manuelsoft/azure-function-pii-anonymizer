import datetime
import logging
import json

import azure.functions as func

from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine

app = func.FunctionApp()

# Se crean una sola vez
analyzer = AnalyzerEngine()
anonymizer = AnonymizerEngine()

@app.route(route="anonymize", auth_level=func.AuthLevel.FUNCTION, methods=["POST"])
def anonymize(req: func.HttpRequest) -> func.HttpResponse:

    logging.info("PII Anonymization request received.")

    try:
        body = req.get_json()

        text = body.get("text")

        if not text:
            return func.HttpResponse(
                json.dumps({"error": "Field 'text' is required."}),
                status_code=400,
                mimetype="application/json"
            )

        # Detectar PII
        analyzer_results = analyzer.analyze(
            text=text,
            language="en"
        )

        # Anonimizar
        anonymized_result = anonymizer.anonymize(
            text=text,
            analyzer_results=analyzer_results
        )

        response = {
            "original_text": text,
            "anonymized_text": anonymized_result.text,
            "entities_detected": [
                {
                    "entity_type": entity.entity_type,
                    "start": entity.start,
                    "end": entity.end,
                    "score": entity.score
                }
                for entity in analyzer_results
            ]
        }

        return func.HttpResponse(
            json.dumps(response),
            mimetype="application/json",
            status_code=200
        )

    except Exception as ex:

        logging.exception(ex)

        return func.HttpResponse(
            json.dumps({"error": str(ex)}),
            mimetype="application/json",
            status_code=500
        )