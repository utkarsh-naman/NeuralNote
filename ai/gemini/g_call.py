import google.generativeai as genai
import logging

def generate_text(api_key: str, prompt: str) -> (str | None, str | None):
    """
    Calls the Gemini API to generate content.

    Args:
        api_key: The Google AI Studio API key.
        prompt: The user's prompt.

    Returns:
        A tuple (generated_text, error_message).
        On success, (text, None).
        On failure, (None, error_message).
    """
    try:
        genai.configure(api_key=api_key)
        
        # We use "gemini-1.5-flash" as a robust default.
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        response = model.generate_content(prompt)
        
        return response.text, None
        
    except Exception as e:
        logging.error(f"Gemini API call failed: {e}")
        # Return a user-friendly error message
        return None, f"Gemini API Error: {str(e)}"

if __name__ == '__main__':
    # Test the function (replace with a real key to test)
    # import os
    # test_key = os.environ.get("GEMINI_API_KEY")
    # if test_key:
    #     text, err = generate_text(test_key, "Explain how AI works in a few words")
    #     if err:
    #         print(f"Error: {err}")
    #     else:
    #         print(f"Success:\n{text}")
    # else:
    #     print("Set GEMINI_API_KEY env var to test.")
    pass
