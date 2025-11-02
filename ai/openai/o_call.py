from openai import OpenAI
import logging

def generate_text(api_key: str, prompt: str) -> (str | None, str | None):
    """
    Calls the OpenAI API to generate content.

    Args:
        api_key: The OpenAI API key.
        prompt: The user's prompt.

    Returns:
        A tuple (generated_text, error_message).
        On success, (text, None).
        On failure, (None, error_message).
    """
    try:
        client = OpenAI(api_key=api_key)

        response = client.chat.completions.create(
            model="gpt-4o-mini", # A strong, cost-effective default
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ]
        )
        
        text = response.choices[0].message.content
        return text, None

    except Exception as e:
        logging.error(f"OpenAI API call failed: {e}")
        # Return a user-friendly error message
        return None, f"OpenAI API Error: {str(e)}"

if __name__ == '__main__':
    # Test the function (replace with a real key to test)
    # import os
    # test_key = os.environ.get("OPENAI_API_KEY")
    # if test_key:
    #     text, err = generate_text(test_key, "Explain how AI works in a few words")
    #     if err:
    #         print(f"Error: {err}")
    #     else:
    #         print(f"Success:\n{text}")
    # else:
    #     print("Set OPENAI_API_KEY env var to test.")
    pass
