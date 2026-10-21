

from google import genai
from config.settings import settings

client = genai.Client(api_key=settings.gemini_api_key)

try:
    result = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents="Say hello in one sentence."
    )
    print("Gemini response:", result.text)

except Exception as exc:
    print("Error type:", type(exc).__name__)
    print("Error details:", exc)
