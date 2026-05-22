from app.llm_client import LLMClient


def main():
    client = LLMClient()

    prompt = """
    Summarize this customer support issue professionally:

    "I was charged twice during checkout and still didn't receive my premium subscription."
    """

    response = client.generate_response(prompt)

    print("\n===== AI RESPONSE =====\n")
    print(response)


if __name__ == "__main__":
    main()