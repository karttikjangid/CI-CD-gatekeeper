import os
import sys
import logging
from openai import OpenAI

try:
    from google import genai
except ImportError:
    pass

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def call_llm(prompt: str) -> str:
    """Generate LLM response with automatic fallback logic."""
    env_mode: str = os.getenv("ENV_MODE", "production")
    
    if env_mode == "local":
        try:
            logger.info("Attempting local Ollama generation...")
            client = OpenAI(
                base_url="http://localhost:11434/v1",
                api_key="ollama"
            )
            response = client.chat.completions.create(
                model="gemma4:e4b",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                top_p=0.1
            )
            content = response.choices[0].message.content
            return content.strip() if content else ""
        except Exception as e:
            logger.warning(f"Local Ollama generation failed ({e}). Falling back to primary provider.")

    gemini_key = os.getenv("GEMINI_API_KEY")
    if gemini_key:
        try:
            logger.info("Using Gemini API...")
            os.environ["GEMINI_API_KEY"] = gemini_key
            client = genai.Client()
            response = client.models.generate_content(
                model="gemini-3-flash-preview",
                contents=prompt,
            )
            if response.text:
                return response.text.strip()
            return ""
        except Exception as e:
            logger.warning(f"Gemini LLM call failed: {e}. Falling back to OpenRouter.")
    else:
        logger.warning("GEMINI_API_KEY is not set. Trying OpenRouter directly.")
        
    openrouter_key = os.getenv("OPENROUTER_API_KEY")
    if not openrouter_key:
        logger.error("Both GEMINI_API_KEY and OPENROUTER_API_KEY are missing or failed.")
        sys.exit(0)
        
    try:
        logger.info("Using OpenRouter API...")
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=openrouter_key,
            default_headers={
                "HTTP-Referer": "https://github.com/karttikjangid/CI-CD-gatekeeper",
                "X-Title": "DataOps Gatekeeper"
            }
        )
        response = client.chat.completions.create(
            model="google/gemma-4-31b-it:free",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            top_p=0.1
        )
        content = response.choices[0].message.content
        return content.strip() if content else ""
    except Exception as e:
        logger.error(f"OpenRouter LLM call failed: {e}")
        sys.exit(0)
