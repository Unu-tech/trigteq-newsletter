import json
import uuid
from typing import Dict, Any

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException, Query
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from pydantic import ValidationError
from newsletter.schemas.output_models import NewsletterOutput

from newsletter.schemas.majors import GeologyMajor
from newsletter.agent.agent import root_agent
from newsletter.logger_settings import get_logger

logger = get_logger(__name__)

app = FastAPI(
    title="Geoscience Newsletter API",
    description="Fetches AI-synthesized newsletters for specific geoscience subfields.",
    version="1.0.0"
)

# --- ADK Runner and Session Setup ---
session_service = InMemorySessionService()
runner = Runner(
    app_name="geology_newsletter_app",
    agent=root_agent,
    session_service=session_service
)

# --- Simple In-Memory Cache ---
# Key: string (the major name), Value: dict (the parsed JSON response)
newsletter_cache: Dict[str, Any] = {}

@app.get("/api/v1/newsletter", response_model=NewsletterOutput)
async def get_newsletter(
    major: GeologyMajor = Query(..., description="The geological major to fetch news for"),
    force_refresh: bool = Query(False, description="Bypass the cache")
):
    major_name = major.value

    if major_name in newsletter_cache and not force_refresh:
        logger.info(f"Cache HIT for major: {major_name}")
        return newsletter_cache[major_name]

    logger.info(f"Cache MISS for major: {major_name}. Triggering pipeline...")
    prompt = f"Latest advancements and updates in {major_name}"
    user_id = "default_api_user"

    MAX_RETRIES = 2

    for attempt in range(1, MAX_RETRIES + 1):
        # Generate a new session ID for each attempt so the agent starts with a clean slate
        session_id = str(uuid.uuid4())

        try:
            session = await session_service.create_session(
                app_name=runner.app_name,
                user_id=user_id,
                session_id=session_id
            )
            session_id_used = getattr(session, "id", session_id)

            # 1. Run the Sequential Pipeline
            full_response = ""
            async for event in runner.run_async(
                user_id=user_id,
                session_id=session_id_used,
                new_message=types.Content(role="user", parts=[types.Part(text=prompt)])
            ):
                if event.content and event.content.parts:
                    for part in event.content.parts:
                        if getattr(part, "text", None):
                            full_response += part.text

            # 2. Clean Markdown Formatting
            clean_json_str = full_response.strip()
            if clean_json_str.startswith("```json"):
                clean_json_str = clean_json_str[7:]
            if clean_json_str.endswith("```"):
                clean_json_str = clean_json_str[:-3]

            # 3. Parse JSON
            parsed_data = json.loads(clean_json_str.strip())

            # 4. Strict Pydantic Validation
            # This throws a ValidationError if the schema is violated
            validated_newsletter = NewsletterOutput.model_validate(parsed_data)

            # 5. Cache and Return
            newsletter_cache[major_name] = validated_newsletter.model_dump()
            logger.info(f"Successfully generated and validated newsletter on attempt {attempt}")
            return validated_newsletter

        except (json.JSONDecodeError, ValidationError) as e:
            logger.warning(f"Attempt {attempt} failed validation. Error: {e}")
            if attempt == MAX_RETRIES:
                logger.error(f"Failed to generate valid schema after {MAX_RETRIES} attempts. Raw Output: {full_response}")
                raise HTTPException(status_code=500, detail="Pipeline failed to format data correctly.")
        except Exception as e:
            logger.error(f"Critical pipeline error: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Internal server error: {e}")
