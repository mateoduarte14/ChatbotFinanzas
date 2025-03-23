import requests
import os

def ask_groq(question):
    """
    This function uses the Groq API to answer a question.
    """
    api_key = "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"  # Replace with your actual API key
    model = "llama3-70b-8192"

    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": model,
        "messages": [{"role": "user", "content": question}],
        "temperature": 0.7
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        return response.json()["choices"][0]["message"]["content"]
    except requests.exceptions.RequestException as e:
        print(f"Error calling Groq API: {e}")
        return None

if __name__ == "__main__":
    question = "What is the capital of France?"
    answer = ask_groq(question)
    if answer:
        print(f"Question: {question}")
        print(f"Answer: {answer}")