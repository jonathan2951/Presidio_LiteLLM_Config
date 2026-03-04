import requests


def test_analyzer():
    """Test Presidio Analyzer service"""
    print("=" * 80)
    print("1. TESTING PRESIDIO ANALYZER")
    print("=" * 80)

    # text = "My name is John Doe, email is john@email.com, and phone is 212-555-5555. The number_of_rows is 1234567890"
    text="My name is John Doe, email is john@email.com, and phone is 212-555-5555. I live in SF, Ca. A random IP: 192.168.0.1." \
    "number_of_rows is 1234567890"
    print(f"Original text: {text}\n")

    try:
        response = requests.post(
            "http://localhost:5002/analyze",
            json={"text": text, "language": "en"}
        )
        response.raise_for_status()
        results = response.json()

        print(f"Status: {response.status_code}")
        print(f"\nEntities detected: {len(results)}")
        for result in results:
            entity_text = text[result['start']:result['end']]
            print(f"  - {result['entity_type']}: '{entity_text}' (score: {result['score']:.2f})")

        return results
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None


def test_anonymizer(analyzer_results=None):
    """Test Presidio Anonymizer service"""
    print("\n" + "=" * 80)
    print("2. TESTING PRESIDIO ANONYMIZER")
    print("=" * 80)

    text = "My name is John Doe, email is john@email.com, and phone is 212-555-5555. I live in SF, Ca. A random IP: 192.168.0.1." \
    "number_of_rows is 1234567890"
    print(f"Original text: {text}\n")

    # If no analyzer results provided, get them first
    if analyzer_results is None:
        analyzer_results = requests.post(
            "http://localhost:5002/analyze",
            json={"text": text, "language": "en"}
        ).json()

    try:
        response = requests.post(
            "http://localhost:5001/anonymize",
            json={
                "text": text,
                "analyzer_results": analyzer_results
            }
        )
        response.raise_for_status()
        result = response.json()

        print(f"Status: {response.status_code}")
        print(f"Anonymized text: {result['text']}")
        print(f"\nItems masked: {len(result.get('items', []))}")

        return result
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None


def test_litellm():
    """Test LiteLLM proxy with presidio guardrails"""
    print("\n" + "=" * 80)
    print("3. TESTING LITELLM WITH PRESIDIO GUARDRAILS")
    print("=" * 80)

    text = "My name is John Doe, my email is john@email.com and phone is 212-555-5555. " \
    "What's my first name, my email and my phone number?"
    print(f"Prompt with PII: {text}\n")

    try:
        response = requests.post(
            "http://localhost:4000/v1/chat/completions",
            headers={"Authorization": "Bearer anything"},
            json={
                "model": "gpt-4o",
                "messages": [{"role": "user", "content": text}]
            }
        )
        response.raise_for_status()
        result = response.json()

        print(f"Status: {response.status_code}")
        print(f"\nLLM Response:")
        print(f"  {result['choices'][0]['message']['content']}")
        print(f"\nModel used: {result.get('model', 'N/A')}")
        print(f"Tokens: {result.get('usage', {})}")
        print(f"Full response :{response.json()}")

        return result
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response: {e.response.text}")
        return None


if __name__ == "__main__":
    # Test 1: Analyzer
    analyzer_results = test_analyzer()

    # Test 2: Anonymizer
    if analyzer_results:
        test_anonymizer(analyzer_results)

    # Test 3: LiteLLM with guardrails
    test_litellm()

    print("\n" + "=" * 80)
    print("TESTS COMPLETE")
    print("=" * 80)
