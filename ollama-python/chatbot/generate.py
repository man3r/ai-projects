import ollama

# Generate API - simple prompt in, text out
generate_response = ollama.generate(
    model="llama3.2:latest",
    prompt="Write a short poem about coding"
)
print("GENERATE:", generate_response["response"])

# Chat API - same question but with message structure
chat_response = ollama.chat(
    model="llama3.2:latest",
    messages=[{"role": "user", "content": "Write a short poem about coding"}]
)
print("CHAT:", chat_response["message"]["content"])