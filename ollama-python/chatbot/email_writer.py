import ollama

def write_email(description: str, tone: str = "professional") -> str:
    prompt = f"""Write a {tone} email based on this description:
{description}

Format the output as:
Subject: <subject line>

<email body>

Keep it concise and clear."""

    response = ""
    print("\n✉️  Writing your email...\n")
    print("-" * 50)

    for chunk in ollama.chat(
        model="llama3.2:latest",
        messages=[{"role": "user", "content": prompt}],
        stream=True
    ):
        content = chunk["message"]["content"]
        print(content, end="", flush=True)
        response += content

    print("\n" + "-" * 50)
    return response


def main():
    print("📧 Local AI Email Writer")
    print("=" * 50)

    while True:
        print("\nDescribe the email you want to write:")
        print("(or type 'exit' to quit)\n")

        description = input("You: ").strip()

        if description.lower() == "exit":
            print("Goodbye! 👋")
            break

        if not description:
            print("Please enter a description!")
            continue

        print("\nChoose tone:")
        print("1. Professional (default)")
        print("2. Friendly")
        print("3. Formal")
        print("4. Casual")

        tone_choice = input("\nTone (1-4): ").strip()

        tones = {
            "1": "professional",
            "2": "friendly",
            "3": "formal",
            "4": "casual"
        }

        tone = tones.get(tone_choice, "professional")

        write_email(description, tone)

        print("\n✅ Done! Write another? (or type 'exit')")


if __name__ == "__main__":
    main()