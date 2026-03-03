from google.adk.agents import LlmAgent, SequentialAgent
from newsletter.schemas.output_models import NewsletterOutput, _get_json_schema_prompt
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

# 1. Generate Schema Instructions
try:
    schema_instructions = _get_json_schema_prompt(NewsletterOutput)
except Exception as e:
    logger.error(f"Failed to load schema instructions: {e}")
    schema_instructions = "Output must be valid JSON."

# 2. Assemble Tools
agent_tools = [
    search_peer_reviewed_papers,
    search_general_geoscience_headlines,
    fetch_industry_news_and_updates,
    fetch_specialized_reports_and_blogs,
    search_academic_arxiv_papers,
    search_general_knowledge
]

# 3. Agent 1: The Researcher (Thinking & Tool Use)
researcher_agent = LlmAgent(
    name="GeoscienceResearcher",
    model="gemini-3-flash-preview",
    tools=agent_tools,
    instruction="""
    You are an expert Geoscience Intelligence Agent. 
    Your objective is to thoroughly research the user's requested topic using your tools.
    1. ANALYZE the topic from professional perspective and consider important related topics.
    2. GATHER articles using your tools. Never spam the tools but be thorough.
        Note that there are tools for you to enrich your understanding (general web search etc.)
    3. SYNTHESIZE your findings into a highly detailed, accurate, unstructured text report.
    Ensure you explicitly include user query, all original article titles, exact URLs, and your analytical notes.
    """,
    description="Researches geoscience topics and writes a comprehensive text report.",
    output_key="research_report"
)

# 4. Agent 2: The Structurer (Formatting & Validation)
structurer_agent = LlmAgent(
    name="NewsletterStructurer",
    model="gemini-3-pro-preview",
    instruction=f"""
    You are a strict Newsletter Editor.
    Your objective is to generate highly informative, professional newsletters for specific geological majors, subfields, or topics requested by the user.
    You are strongly encouraged to use emojis and casual writing in freeform fields for the sake of human readability.
  
    
    CONSTRAINTS:
    - Output ONLY valid JSON. Do not wrap in markdown code blocks (no ```json).
    - Hallucinated keys are strictly forbidden. Do not add fields outside the schema.
    - Adhere EXACTLY to this schema. Both in terms of structure and content specifications:
    {schema_instructions}
    
    RESEARCH REPORT TO FORMAT:
    {{research_report}}
    """,
    description="Formats the unstructured research report into strict JSON.",
    output_schema=NewsletterOutput,
    output_key="structured_json"
)

# 5. Assemble the Sequential Pipeline
try:
    root_agent = SequentialAgent(
        name="geology_newsletter_pipeline",
        sub_agents=[researcher_agent, structurer_agent],
        description="A pipeline that researches geoscience news and formats it into strict JSON."
    )
    logger.info("Sequential Pipeline initialized successfully.")
except Exception as e:
    logger.error(f"Failed to initialize pipeline: {e}")
    root_agent = LlmAgent(name="fallback", model=GEMINI_MODEL, instruction="Error state.")
