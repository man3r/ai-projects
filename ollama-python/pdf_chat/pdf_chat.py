import ollama
import chromadb
import pypdf
import os
import sys

# Initialize ChromaDB locally
client = chromadb.Client()
collection = client.create_collection("pdf_docs")

def load_pdf(filepath: str) -> list[str]:
    """Extract text from PDF and split into chunks"""
    print(f"\n📄 Loading PDF: {filepath}")
    
    reader = pypdf.PdfReader(filepath)
    chunks = []
    
    for i, page in enumerate(reader.pages):
        text = page.extract_text()
        if text.strip():
            # Split page into smaller chunks of ~500 chars
            words = text.split()
            chunk = ""
            for word in words:
                chunk += word + " "
                if len(chunk) >= 500:
                    chunks.append(chunk.strip())
                    chunk = ""
            if chunk:
                chunks.append(chunk.strip())
    
    print(f"✅ Loaded {len(reader.pages)} pages → {len(chunks)} chunks")
    return chunks


def index_pdf(filepath: str):
    """Convert PDF chunks to embeddings and store in ChromaDB"""
    chunks = load_pdf(filepath)
    
    print("\n🧮 Creating embeddings...")
    
    for i, chunk in enumerate(chunks):
        # Get embedding for this chunk
        response = ollama.embeddings(
            model="llama3.2:latest",
            prompt=chunk
        )
        
        # Store in ChromaDB
        collection.add(
            ids=[f"chunk_{i}"],
            embeddings=[response["embedding"]],
            documents=[chunk]
        )
        
        if (i + 1) % 10 == 0:
            print(f"  Processed {i + 1}/{len(chunks)} chunks...")
    
    print(f"✅ Indexed {len(chunks)} chunks into vector database!")


def ask_question(question: str):
    """Find relevant chunks and answer question"""
    
    # Convert question to embedding
    question_embedding = ollama.embeddings(
        model="llama3.2:latest",
        prompt=question
    )
    
    # Find most relevant chunks
    results = collection.query(
        query_embeddings=[question_embedding["embedding"]],
        n_results=3  # Get top 3 most relevant chunks
    )
    
    # Build context from relevant chunks
    context = "\n\n".join(results["documents"][0])
    
    # Ask LLM with context
    prompt = f"""Use the following context from a PDF document to answer the question.
Only use information from the context. If the answer is not in the context, say so.

Context:
{context}

Question: {question}

Answer:"""

    print(f"\n🤖 Answer:\n")
    print("-" * 50)
    
    for chunk in ollama.chat(
        model="llama3.2:latest",
        messages=[{"role": "user", "content": prompt}],
        stream=True
    ):
        print(chunk["message"]["content"], end="", flush=True)
    
    print("\n" + "-" * 50)


def main():
    print("📚 Local PDF Chat — Powered by Ollama")
    print("=" * 50)
    
    # Get PDF path
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
    else:
        pdf_path = input("\nEnter path to your PDF file: ").strip()
    
    if not os.path.exists(pdf_path):
        print(f"❌ File not found: {pdf_path}")
        sys.exit(1)
    
    # Index the PDF
    index_pdf(pdf_path)
    
    # Chat loop
    print("\n💬 PDF loaded! Ask me anything about it.")
    print("Type 'exit' to quit\n")
    
    while True:
        question = input("You: ").strip()
        
        if question.lower() == "exit":
            print("Goodbye! 👋")
            break
            
        if not question:
            continue
            
        ask_question(question)


if __name__ == "__main__":
    main()