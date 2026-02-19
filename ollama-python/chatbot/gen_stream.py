import ollama

for chunk in ollama.generate(
    model="llama3.2:latest",
    prompt="Write a short poem about coding",
    stream=True
):
    print(chunk["response"], end="", flush=True)

print("-------------------")

for chunk in ollama.chat(
    model="llama3.2:latest",
    prompt="Write a short poem about coding",
    stream=True
):
    print(chunk["response"], end="", flush=True)