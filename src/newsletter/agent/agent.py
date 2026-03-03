# src/newsletter/agent/agent.py

from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm

# Import our schema and schema-prompt generator
from newsletter.schemas.output_models import NewsletterOutput, _get_json_schema_prompt

# Import our safely constrained tools
from newsletter.tools.agent_tools import (
    search_peer_reviewed_papers,
    search_general_geoscience_headlines,
    fetch_industry_news_and_updates,
    fetch_specialized_reports_and_blogs,
    search_academic_arxiv_papers,
    search_general_knowledge
)
from newsletter.logger_settings import get_logger

logger = get_logger(__name__)

# 1. Generate the strict schema instructions dynamically
try:
    schema_instructions = _get_json_schema_prompt(NewsletterOutput)
except Exception as e:
    logger.error(f"Failed to load schema instructions: {e}")
    schema_instructions = "Output must be valid JSON."

# 2. Define the Agent's brain (System Prompt)
INSTRUCTION = f"""
You are an expert Geoscience Intelligence Agent and Newsletter Editor. 
Your objective is to generate highly informative, professional newsletters for specific geological majors, subfields, or topics requested by the user.

You are strongly encouraged to use emojis and casual writing for the sake of human readability.

WORKFLOW:
1. ANALYZE: Understand the user's requested topic.
2. GATHER: Strategically use your tools to fetch information. Avoid 'spamming' a tool as that will result in an error.
3. SYNTHESIZE: Group the gathered articles by their source. Write engaging titles, concise summaries, and detailed analytical notes explicitly using core scientific concepts.

CONSTRAINTS:
- You MUST output valid JSON only. Do not wrap the JSON in markdown code blocks (no ```json ... ```).
- Your output must EXACTLY follow this JSON schema structure and adhere strictly to the field descriptions provided:

{schema_instructions}

Do not add extra keys. Ensure all URLs from the tools are accurately restated in the "source" field.
"""

# 3. Assemble the available tools
agent_tools = [
    search_peer_reviewed_papers,
    search_general_geoscience_headlines,
    fetch_industry_news_and_updates,
    fetch_specialized_reports_and_blogs,
    search_academic_arxiv_papers,
    search_general_knowledge
]

# 4. Instantiate the ADK Agent and assign it to 'root_agent'
try:
    root_agent = LlmAgent(
        name="geology_newsletter_agent",
        description="An autonomous agent that synthesizes geoscience data into structured newsletters.",
        model=LiteLlm(model="gemini/gemini-3-flash-preview"), 
        tools=agent_tools,
        instruction=INSTRUCTION,
    )
    logger.info("Geology Newsletter Agent initialized successfully.")
except Exception as e:
    logger.error(f"Failed to initialize root_agent: {e}")
    # Fallback minimal agent so the server doesn't crash on boot, but fails gracefully on use
    root_agent = LlmAgent(
        name="fallback_agent",
        description="Fallback agent due to initialization failure.",
        model=LiteLlm(model="gemini/gemini-3-flash-preview"),
        instruction="Tell the user there was a critical error initializing the main agent.",
    )
