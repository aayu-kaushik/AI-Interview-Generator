import os
import time

from dotenv import load_dotenv
from google import genai

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError("GEMINI_API_KEY is missing from the .env file.")

client = genai.Client(api_key=API_KEY)


def generate_llm_response(prompt):

    # Try primary model first, then fallback models
    models = [
        "gemini-3.5-flash-lite",
        "gemini-3.8-flash"
    ]

    for model in models:

        print(f"\nTrying model: {model}")

        for attempt in range(1):

            try:
                response = client.models.generate_content(
                    model=model,
                    contents=prompt
                )

                if response.text:
                    print(f"Success using: {model}\n")
                    return response.text.strip()

            except Exception as error:

                error_text = str(error)

                # Temporary server overload
                if "503" in error_text or "UNAVAILABLE" in error_text:

                    wait_time = 2 ** attempt

                    print(
                        f"{model} is busy. "
                        f"Retrying in {wait_time} seconds..."
                    )

                    time.sleep(wait_time)

                else:
                    print(f"Error with {model}: {error}")
                    break

        print(f"{model} failed. Trying fallback model...")

    print("\nAll available models failed.")
    return None