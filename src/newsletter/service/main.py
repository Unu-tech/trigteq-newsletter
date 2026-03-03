import json
import uuid
from typing import Dict, Any

from fastapi import FastAPI, HTTPException, Query
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

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

@app.get("/api/v1/newsletter", response_model=Dict[str, Any])
async def get_newsletter(
    major: GeologyMajor = Query(..., description="The geological major to fetch news for (e.g., ?major=Mineralogy/Petrology)"),
    force_refresh: bool = Query(False, description="Bypass the cache and force a new generation")
):
    """
    Fetches the latest newsletter for a given major via query parameter.
    Returns cached data if available, otherwise triggers the ADK agent asynchronously.
    """
    major_name = major.value
    
    # 1. Check Cache
    if major_name in newsletter_cache and not force_refresh:
        logger.info(f"Cache HIT for major: {major_name}")
        return newsletter_cache[major_name]

    # 2. Cache Miss: Setup session and prompt
    logger.info(f"Cache MISS (or forced refresh) for major: {major_name}. Triggering agent...")
    prompt = f"Latest advancements and updates in {major_name}"
    session_id = str(uuid.uuid4())
    user_id = "default_api_user" # Hardcoded for now, can be wired to auth later

    try:
        # Create the ADK session
        session = await session_service.create_session(
            app_name=runner.app_name,
            user_id=user_id,
            session_id=session_id
        )
        session_id_used = getattr(session, "id", session_id)
        
        # 3. Execute the Agent
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
                        
        # 4. Parse and Cache the Result
        # Strip potential markdown code blocks (e.g., ```json ... ```) just in case the LLM disobeys the prompt
        clean_json_str = full_response.strip()
        if clean_json_str.startswith("```json"):
            clean_json_str = clean_json_str[7:]
        if clean_json_str.endswith("```"):
            clean_json_str = clean_json_str[:-3]

        parsed_data = json.loads(clean_json_str.strip())
        newsletter_cache[major_name] = parsed_data
        
        logger.info(f"Successfully generated and cached newsletter for {major_name}")
        return parsed_data
        
    except json.JSONDecodeError as e:
        logger.error(f"Agent failed to return valid JSON. Error: {e}\nRaw Output: {full_response}")
        raise HTTPException(status_code=500, detail="Agent generated invalid JSON format.")
    except Exception as e:
        logger.error(f"Critical error executing agent: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error during agent generation: {e}")
