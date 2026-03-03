from typing import Literal, List, Dict
import urllib.parse
from newsletter.tools.fetchers import fetch_doaj_keyword, fetch_newsapi, fetch_rss_feed, search_arxiv, search_tavily

def search_peer_reviewed_papers(keyword: str) -> List[Dict[str, str]]:
    """
    Searches a vast database of Open Access geoscience journals for peer-reviewed academic papers.
    
    USE CASES: Use this when you need deep academic context, empirical results, or methodological frameworks.
    RULES FOR KEYWORDS:
    - Use specific scientific terms, geological formations, or subfields (e.g., "Porphyry copper", "Paleoclimatology", "Lithosphere").
    - DO NOT use natural language questions (e.g., "What is the latest on copper?").
    - Keep keywords to 1-3 words maximum for the best results.
    """
    # Internally calls the DOAJ fetcher
    return fetch_doaj_keyword(keyword=keyword)

def search_general_geoscience_headlines(query: str) -> List[Dict[str, str]]:
    """
    Searches global news aggregators for broad, mainstream geoscience and planetary headlines.
    
    USE CASES: Use this for high-level overviews of recent events, mainstream climate news, or planetary discoveries.
    RULES FOR QUERY: Can be standard search terms like "Mars rover geology" or "global warming ocean currents".
    """
    # Internally calls the NewsAPI fetcher
    return fetch_newsapi(query=query)

# Define the exact allowed strings for Broad News & Industry
BroadNewsSources = Literal[
    "ScienceDaily_Environmental", "ScienceDaily_EarthScience", "ScienceDaily_Geology",
    "ScienceDaily_Mining", "ScienceDaily_RenewableEnergy", "ScienceDaily_Chemistry",
    "ScienceDaily_Geoengineering", "ScienceDaily_Oceanography", 
    "Mining_com", "Northern_Miner", "USGS_All_News"
]

def fetch_industry_news_and_updates(source_name: BroadNewsSources) -> List[Dict[str, str]]:
    """
    Fetches the latest articles and press releases of the domain, from major earth science aggregators and commercial mining networks.
    
    AVAILABLE SOURCES:
    - "ScienceDaily_*": Hourly updated, digestible summaries of broad earth science, environment, and energy news. Specifics are:
       - ScienceDaily_Environmental
       - ScienceDaily_EarthScience
       - ScienceDaily_Geology
       - ScienceDaily_Mining
       - ScienceDaily_RenewableEnergy
       - ScienceDaily_Chemistry
       - ScienceDaily_Geoengineering
       - ScienceDaily_Oceanography
    - "Mining_com": Global mining news, supply chain vulnerabilities, and commodity market updates.
    - "Northern_Miner": Updates on mine development, exploration activities, and drill assay results.
    - "USGS_All_News": Official agency press releases covering broad US earth science and ecosystems.
    """
    url_map = {
        "ScienceDaily_Environmental": "https://sciencedaily.com/rss/earth_climate/environmental_science.xml",
        "ScienceDaily_EarthScience": "https://sciencedaily.com/rss/earth_climate/earth_science.xml",
        "ScienceDaily_Geology": "https://sciencedaily.com/rss/earth_climate/geology.xml",
        "ScienceDaily_Mining": "https://sciencedaily.com/rss/earth_climate/mining.xml",
        "ScienceDaily_RenewableEnergy": "https://sciencedaily.com/rss/earth_climate/renewable_energy.xml",
        "ScienceDaily_Chemistry": "https://sciencedaily.com/rss/earth_climate/chemistry.xml",
        "ScienceDaily_Geoengineering": "https://sciencedaily.com/rss/earth_climate/geoengineering.xml",
        "ScienceDaily_Oceanography": "https://sciencedaily.com/rss/earth_climate/oceanography.xml",
        "Mining_com": "https://www.mining.com/feed/",
        "Northern_Miner": "https://www.northernminer.com/feed/",
        "USGS_All_News": "https://www.usgs.gov/news/all/feed"
    }
    return fetch_rss_feed(feed_url=url_map[source_name])

# Define the exact allowed strings for Specialized Blogs & Reports
SpecializedSources = Literal[
    "USGS_Publications", "USGS_Volcano_Alerts", "Smithsonian_Global_Volcanism",
    "AGU_Blogosphere", "AGU_JGR_Solid_Earth", "AGU_Earths_Future",
    "EGU_Geochemistry_Blog", "EGU_Tectonics_Blog", 
    "EarthByte_Tectonics_News", "GeoEngineers_Blog"
]

def fetch_specialized_reports_and_blogs(source_name: SpecializedSources) -> List[Dict[str, str]]:
    """
    Fetches highly technical updates, hazard alerts, and informal scientific discourse from specialized geological societies and research groups.
    
    AVAILABLE SOURCES:
    - "USGS_Publications": Official releases of new USGS research and data reports.
    - "USGS_Volcano_Alerts": Current hazard monitoring and alert level changes for US volcanoes.
    - "Smithsonian_Global_Volcanism": Weekly vetted narrative summaries of global volcanic eruptions and thermal anomalies.
    - "AGU_Blogosphere": Organizational updates and commentary on critical science policy developments.
    - "AGU_JGR_Solid_Earth": Peer-reviewed geophysics research on mantle structures and tectonic forces.
    - "AGU_Earths_Future": High-impact research on climate change, paleoclimatology, and global warming.
    - "EGU_Geochemistry_Blog": Active discourse on mineralogy, petrology, and volcanology.
    - "EGU_Tectonics_Blog": Active discourse on structural geology, fault mechanics, and upper crustal strain.
    - "EarthByte_Tectonics_News": Research group updates on global climate modulation by plate boundaries and structural modeling.
    - "GeoEngineers_Blog": Practical, project-oriented engineering geology and infrastructure design updates.
    """
    url_map = {
        "USGS_Publications": "https://pubs.usgs.gov/pubs-services/publication/rss/",
        "USGS_Volcano_Alerts": "https://volcanoes.usgs.gov/rss/vhpcaprss.xml",
        "Smithsonian_Global_Volcanism": "https://volcano.si.edu/news/WeeklyVolcanoRSS.xml",
        "AGU_Blogosphere": "https://blogs.agu.org/feed/",
        "AGU_JGR_Solid_Earth": "https://agupubs.onlinelibrary.wiley.com/feed/21699356/most-recent",
        "AGU_Earths_Future": "https://agupubs.onlinelibrary.wiley.com/feed/23284277/most-recent",
        "EGU_Geochemistry_Blog": "https://blogs.egu.eu/divisions/gmpv/feed/",
        "EGU_Tectonics_Blog": "https://blogs.egu.eu/divisions/ts/feed/",
        "EarthByte_Tectonics_News": "https://www.earthbyte.org/category/news/feed/",
        "GeoEngineers_Blog": "https://geoengineers.com/feed/"
    }
    return fetch_rss_feed(feed_url=url_map[source_name])

def search_academic_arxiv_papers(query: str) -> List[Dict[str, str]]:
    """
    Searches the Arxiv database for scientific pre-prints and academic papers.

    USE CASES: Use this for technical, academic, or scientific queries that fall outside
    of the specific Geoscience DOAJ search (e.g., computer science, physics, planetary math).
    RULES FOR QUERY: Use specific scientific terms or methodologies.
    """
    return search_arxiv(query=query)

def search_general_knowledge(query: str) -> List[Dict[str, str]]:
    """
    Performs a general web search for current events, news, or broad facts.

    USE CASES: Use this as a fallback when you need information on current events,
    general industry facts, policy changes, or items not covered by geoscience-specific feeds.
    RULES FOR QUERY: Can be natural language or specific keywords.
    """
    return search_tavily(query=query)
