import os
import sys
import logging
from openai import OpenAI

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def call_llm(prompt: str) -> str:
    """Generate LLM response with automatic fallback to Gemini if local Ollama fails."""
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
            logger.warning(f"Local Ollama generation failed ({e}). Falling back to Gemini.")

    gemini_key: str | None = os.getenv("GEMINI_API_KEY")
    if not gemini_key:
        logger.error("GEMINI_API_KEY environment variable is not set.")
        sys.exit(0)
        
    try:
        logger.info("Using Gemini API...")
        client = OpenAI(
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
            api_key=gemini_key
        )
        response = client.chat.completions.create(
            model="gemini-3-flash-preview",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            top_p=0.1
        )
        content = response.choices[0].message.content
        return content.strip() if content else ""
    except Exception as e:
        logger.error(f"Gemini LLM call failed: {e}")
        sys.exit(0)
