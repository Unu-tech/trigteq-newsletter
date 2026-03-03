import json
from pydantic import BaseModel, Field
from typing import List

class ArticleSummary(BaseModel):
    title: str = Field(
        ..., 
        description="The restated, clear, and engaging title of the article or research paper."
    )
    source_url: str = Field(
        ..., 
        description="MUST restate the original source URLs here."
    )
    summary: str = Field(
        ..., 
        description="A concise, reading-friendly summary of the content designed for a general geoscience audience. Focus on the 'what' and 'why'."
    )
    notes: str = Field(
        ..., 
        description="A more detailed analytical note explicitly using the keywords, core scientific concepts, and themes important to the topic. Explain the methodology or broader implications here."
    )

class NewsletterSection(BaseModel):
    source: str = Field(
        ..., 
        description="An informative description of where this information comes from (e.g., 'Peer-reviewed academic paper from the Directory of Open Access Journals', 'Industry update from Mining.com')."
    )
    articles: List[ArticleSummary] = Field(
        ..., 
        description="A list of the summarized articles belonging to this specific source."
    )

class NewsletterOutput(BaseModel):
    sections: List[NewsletterSection] = Field(
        ..., 
        description="The grouped sections of the geoscience newsletter."
    )

def _get_json_schema_prompt(model: BaseModel) -> str:
    """
    Generates a clear, LLM-friendly prompt that describes the required
    JSON output structure based on the Pydantic model's field descriptions.
    """
    schema_info = {}
    for name, field in model.model_fields.items():
        # Handle nested models simply for the prompt representation
        if hasattr(field.annotation, "__args__") and issubclass(field.annotation.__args__[0], BaseModel):
            nested_model = field.annotation.__args__[0]
            nested_info = {n: f.description for n, f in nested_model.model_fields.items()}
            schema_info[name] = f"List of objects containing: {nested_info}"
        else:
            schema_info[name] = field.description or "No description provided."

    return json.dumps(schema_info, indent=2)
