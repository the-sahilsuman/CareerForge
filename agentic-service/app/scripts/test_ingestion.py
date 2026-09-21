from app.ingestion.models import IngestionMessage
from app.ingestion.service import ingestion_service


message = IngestionMessage(
    user_id="section4-test-user",
    document_id="section4-test-document",
    s3_key="SAHIL_SUMAN.pdf",
    document_type="resume",
    metadata={
        "source": "section4-test",
    },
)

result = ingestion_service.process(
    message,
)

print()
print("========== INGESTION RESULT ==========")
print("User:", result.user_id)
print("Document:", result.document_id)
print("Chunks:", result.chunks_created)
print("Vectors:", result.vectors_created)
print("======================================")