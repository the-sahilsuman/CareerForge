from app.retrieval import retrieval_service


result = retrieval_service.search(
    user_id="section4-test-user",
    query="What technical skills does this candidate have?",
    top_k=5,
)

print()
print("========== RETRIEVAL RESULT ==========")
print("Query:", result.query)
print("Count:", result.count)

for index, chunk in enumerate(
    result.results,
    start=1,
):
    print()
    print(f"--- Result {index} ---")
    print("Key:", chunk.key)
    print("Score:", chunk.score)
    print("Distance:", chunk.distance)
    print("User:", chunk.user_id)
    print("Document:", chunk.document_id)
    print("Chunk:", chunk.chunk_id)
    print("Text:", chunk.text[:500])

print()
print("=======================================")