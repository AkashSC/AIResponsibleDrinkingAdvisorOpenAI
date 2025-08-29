import os
from openai import OpenAI

# Initialize client with API key from environment
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_ai_response(prompt: str) -> str:
    """Send prompt to OpenAI and return response"""
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"
