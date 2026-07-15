import json
from textwrap import dedent
from typing import Dict, AsyncIterator, Optional, List, Any
from agno.agent import Agent
from agno.models.groq import Groq
from agno.db.sqlite import SqliteDb
from agno.utils.log import logger
import os
from agno.utils.pprint import pprint_run_response
from dotenv import load_dotenv
import asyncio
from agno.tools.duckduckgo import DuckDuckGoTools
import datetime

# Load environment variables
load_dotenv()

# Get API keys from environment variables
DUCKDUCKGO_API_KEY = os.getenv("DUCKDUCKGO_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Validate API keys
if not DUCKDUCKGO_API_KEY:
    raise ValueError("DUCKDUCKGO_API_KEY environment variable is not set. Please set it in your .env file or environment.")
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY environment variable is not set. Please set it in your .env file or environment.")

# Ensure database directory exists before initializing DB
os.makedirs("tmp", exist_ok=True)

# Define storage database correctly outside the agent instantiation
newsletter_db = SqliteDb(db_file="tmp/newsletter_data.db")

# Newsletter Research Agent: Handles web searching and content extraction using duckduckgo
newsletter_agent = Agent(
    model=Groq(
        id="llama-3.1-8b-instant",
        api_key=GROQ_API_KEY,
        max_tokens=1024
    ),
    tools=[
        DuckDuckGoTools(
            # enable_search=True,           # Enables the search functionality
            # search_params={},             # Instantiates an empty dictionary (avoids NoneType)
            # formats=[ "links"] # Pass your structural requirements here safely, can also add "markdown",
        ), 
    ],
    # In Agno v2, 'storage' is replaced by 'db'
    db=newsletter_db,
    description=dedent("""\
    You are NewsletterResearch-X, an elite research assistant specializing in discovering
    and extracting high-quality content for compelling newsletters. Your expertise includes:

    - Finding authoritative and trending sources across multiple domains
    - Extracting and synthesizing content efficiently while maintaining accuracy
    - Evaluating content credibility, relevance, and potential impact
    - Identifying diverse perspectives, expert opinions, and emerging trends
    - Ensuring comprehensive topic coverage with balanced viewpoints
    - Maintaining journalistic integrity and ethical reporting standards
    - Creating engaging narratives that resonate with target audiences
    - Adapting content style and depth based on audience expertise level\
    """),
    instructions=[
        f"Today's date and time is {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}.",
        "Search for the latest, up-to-date newsletter content based on this timeframe.",
        "1. Initial Research & Discovery:",
        "   - Use duckduckgo_search to find recent articles about the topic",
        "   - Search for authoritative sources, expert opinions, and industry leaders",
        "   - Focus on the most recent and relevant content (prioritize last 7 days)",
        "2. Content Analysis & Processing:",
        "   - Extract key insights, trends, and patterns from each article",
        "3. Content Organization & Structure:",
        "   - Group related information by theme and significance",
        "4. Newsletter Creation:",
        "   - Follow the exact template structure below",
    ],
    expected_output=dedent("""\
        # ${Compelling Subject Line}

        ## Welcome
        {Engaging hook and context}

        ## ${Main Story}
        {Key insights and analysis}
        {Expert quotes and statistics}

        ## Featured Content
        {Deeper exploration}
        {Real-world examples}

        ## Quick Updates
        {Actionable insights}
        {Expert recommendations}

        ## This Week's Highlights
        - {Notable update 1}
        - {Important news 2}
        - {Key development 3}

        ## Sources & Further Reading
        {Properly attributed sources with links}
    """),
    markdown=True,
    debug_mode=True,
)

def NewsletterGenerator(topic: str, search_limit: int = 2, time_range: str = "qdr:w") -> Dict[str, Any]:
    """
    Generate a newsletter based on the given topic and search parameters.
    """
    try:
        # Update search parameters dynamically via the instantiated toolkit
        prompt = (
            f"Search for recent updates on: '{topic}'. "
            f"Retrieve a maximum of {search_limit} results from within the past week."
        )
        
        response = newsletter_agent.run(prompt)
        logger.info('Newsletter generated successfully')
        return response
    except ValueError as ve:
        logger.error('Configuration error: %s', ve)
        raise
    except Exception as e:
        logger.error('Unexpected error in newsletter generation: %s', e, exc_info=True)
        raise RuntimeError('Newsletter generation failed: %s' % e) from e

if __name__ == "__main__":
    NewsletterGenerator("Latest developments in AI")
