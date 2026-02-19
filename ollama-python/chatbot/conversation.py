import ollama

history = []

while True:
    user_input = input("You: ")
    if user_input == "exit":
        break

    history.append({"role": "user", "content": user_input})

    response = ollama.chat(
        model="llama3.2:latest",
        messages=history
    )

    reply = response["message"]["content"]
    history.append({"role": "assistant", "content": reply})

    print(f"AI: {reply}\n")