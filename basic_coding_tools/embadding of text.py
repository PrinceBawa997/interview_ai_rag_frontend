from langchain_huggingface import HuggingFaceEmbeddings

# Create embedding model
embeddings = HuggingFaceEmbeddings(
    model_name="all-MiniLM-L6-v2"
)

# Sample text
text = "Hello, I am learning RAG with LangChain"

# Convert text to embedding (vector)
vector = embeddings.embed_query(text)

# Print result
print("Vector length:", len(vector))
print("First 10 values:", vector[:10])