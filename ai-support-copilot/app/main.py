from app.llm_client import LLMClient


def main():
    client = LLMClient()

    prompt = "Summarize this customer issue: Payment failed twice."

    response = client.generate_response(prompt)

    print("\nAI RESPONSE:")
    print(response)


if __name__ == "__main__":
    main()