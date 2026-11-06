# LangChain's decorator turns these Python functions into callable agent tools.
from langchain.tools import tool
# requests performs HTTP fetches; dotenv and os load the API configuration.
import requests
from dotenv import load_dotenv
import os
# Tavily supplies search results; the remaining libraries extract readable page text.
from tavily import TavilyClient
from rich import print
from bs4 import BeautifulSoup
from readability import Document
import trafilatura
import re

# Load keys from .env before constructing the Tavily client.
load_dotenv()

# Keep the key available for validation and initialize Tavily with a safe empty fallback.
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
tavily = TavilyClient(api_key=TAVILY_API_KEY or "")


@tool
def web_search(query: str) -> str:
    """Search the web for recent, reliable information on a topic and return the top 5 results with titles, URLs, and snippets."""

    # Avoid sending a known placeholder or missing key to the external service.
    if not TAVILY_API_KEY or TAVILY_API_KEY == "your_tavily_api_key_here":
        return "Error: Tavily API key is missing or invalid. Add a valid TAVILY_API_KEY to your .env file."

    try:
        # Ask Tavily for up to five web results matching the agent's query.
        results = tavily.search(query=query, max_results=5)
    except Exception as e:
        # Return a readable tool result so the agent can explain the search failure.
        return f"Error: Tavily search failed. Details: {str(e)}"

    # Convert the provider response into compact text that fits the agent context.
    out=[]
    for r in results['results']:
        # Include the title, URL, and only the first 300 characters of each snippet.
        out.append(f"Title: {r['title']}\nURL: {r['url']}\nSnippet: {r['content'][:300]}\n")
    # Separate records clearly for the model that will choose pages to read.
    return "\n...\n".join(out)


@tool
def scrape_url(url: str) -> str:
    """Scrape the text content of a webpage and return a concise summary extracted from the page. Use the URL as input."""

    # Send browser-like headers to improve compatibility with ordinary web servers.
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
        "Accept-Language": "en-US,en;q=0.9",
        "Referrer": "https://www.google.com/"
    }

    try:
        # Fetch the page with a timeout, then raise for HTTP error status codes.
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        # Keep the source HTML for either of the text extraction libraries below.
        html = response.text

        # Prefer Trafilatura for article-style pages because it removes boilerplate.
        extracted = trafilatura.extract(html, include_comments=False, include_tables=False)

        # Use the primary extraction when it contains enough text to be useful.
        if extracted and len(extracted.strip()) > 200:
            # Collapse whitespace and cap output to avoid flooding the model context.
            cleaned = re.sub(r'\s+', ' ', extracted).strip()
            return cleaned[:500]

        # If Trafilatura finds too little text, fall back to Readability's main-content view.
        doc = Document(html)
        clean_html = doc.summary()

        # Parse the extracted fragment so navigation and other non-content elements can be removed.
        soup = BeautifulSoup(clean_html, 'html.parser')

        # Remove common page regions that are not part of the article body.
        for tag in soup(['script', 'style', 'nav', 'footer', 'header', 'aside', 'form', 'noscript']):
            tag.decompose()

        # Join visible text into one line and normalize repeated whitespace.
        text = soup.get_text(separator=' ', strip=True)
        cleaned = re.sub(r'\s+', ' ', text).strip()

        # Return extracted content when available, otherwise give the agent a clear result.
        if cleaned:
            return cleaned[:500]
        return "Error: Unable to extract meaningful content from the page."
    except requests.exceptions.Timeout:
        # Report timeouts separately so the agent can distinguish slow sites from other errors.
        return "Error: The request timed out while trying to access the URL."
    except requests.exceptions.HTTPError as e:
        # Include the HTTP status details when the remote server rejects the request.
        return f"Error: HTTP error occurred while trying to access the URL. Details: {str(e)}"
    
    except requests.exceptions.RequestException as e:
        # Catch connection and other transport-level errors from requests.
        return f"Error: An error occurred while trying to access the URL. Details: {str(e)}"
    except Exception as e:
        # Keep unexpected parsing failures inside the tool instead of crashing the agent run.
        return f"Error: An unexpected error occurred. Details: {str(e)}"
        


