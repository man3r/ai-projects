import ollama

response = ollama.chat(
    model="llama3.2:latest",
    messages=[
        {"role": "user", "content": "Explain Python decorators simply"}
    ]
)

print(response["message"]["content"])