import ollama

# Stream tokens as they generate (feels more responsive)
for chunk in ollama.chat(
    model="llama3.2:latest",
    messages=[{"role": "user", "content": "Write a haiku about coding"}],
    stream=True
):
    print(chunk["message"]["content"], end="", flush=True)