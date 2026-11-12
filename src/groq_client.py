
import os
import time
from dotenv import load_dotenv
from groq import Groq
from groq import APIStatusError, APIConnectionError, APITimeoutError

load_dotenv(override=True)

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise ValueError("API key not found in .env file")

client = Groq(api_key=api_key, timeout=30.0, max_retries=0)

MAX_RETRIES = 3


def send_request(question):
    retries = 0
    start_time = time.perf_counter()

    while True:
        try:
            response = client.chat.completions.create(
                model="openai/gpt-oss-20b",
                messages=[
                    {
                        "role": "user",
                        "content": question
                    }
                ],
                max_completion_tokens=1000
            )

            end_time = time.perf_counter()

            print("\nAI ANSWER:")
            print(response.choices[0].message.content)

            print("\nREQUEST DETAILS:")
            print("Status: ok")
            print("Retries:", retries)
            print("Latency:", round(
                (end_time - start_time) * 1000, 2
            ), "ms")
            print("Input tokens:", response.usage.prompt_tokens)
            print("Output tokens:", response.usage.completion_tokens)
            print("Total tokens:", response.usage.total_tokens)

            return response

        except APIStatusError as error:
            status_code = error.status_code

            if status_code == 429 or status_code >= 500:
                if retries >= MAX_RETRIES:
                    print("\nRequest given up after maximum retries.")
                    print("Status:", status_code)
                    print("Retries:", retries)
                    return None

                retries += 1
                delay = 2 ** (retries - 1)

                print(
                    f"\nTemporary HTTP error {status_code}. "
                    f"Retry {retries}/{MAX_RETRIES} in {delay} seconds."
                )
                time.sleep(delay)

            else:
                print("\nNon-retryable HTTP error:", status_code)
                return None

        except (APIConnectionError, APITimeoutError) as error:
            if retries >= MAX_RETRIES:
                print("\nRequest given up after maximum retries.")
                print("Error:", type(error).__name__)
                print("Retries:", retries)
                return None

            retries += 1
            delay = 2 ** (retries - 1)

            print(
                f"\nConnection/timeout error. "
                f"Retry {retries}/{MAX_RETRIES} in {delay} seconds."
            )
            time.sleep(delay)


if __name__ == "__main__":
    question = (
        "Explain the Transformer attention mechanism "
        "in simple English."
    )

    print("Sending question to Groq...")
    send_request(question)
