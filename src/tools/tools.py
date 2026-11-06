from langchain.tools import tool
import requests
from dotenv import load_dotenv
import os
from tavily import TavilyClient
from rich import print
from bs4 import BeautifulSoup
from readability import Document
import trafilatura
import re
  


load_dotenv()

tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))


def web_search(query:str) -> str:
    """" search teh web for recent and reliable information on a topic. Returns Titles, urls, and snippets of the top 5 results. """

    results = tavily.search(query=query, max_results=5)
    out=[]
    for r in results['results']:
        out.append(f"Title: {r['title']}\nURL: {r['url']}\nSnippet: {r['content'][:300]}\n")
    return "\n...\n".join(out)



def scrape_url(url:str) -> str:
    """scrape the content of a webpage and return the text content from url. Returns the title and the main text content of the page. Use multiple extraction methods to get the best results. If the page is not in English, translate it to English. If the page is not accessible, return an error message. """

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
        "Accept-Language": "en-US,en;q=0.9",
        "Referrer": "https://www.google.com/"
    }

    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        html = response.text

        # Trafilatura extraction (Best for articles and blogs)
        extracted = trafilatura.extract(html, include_comments=False, include_tables=False)

        if extracted and len(extracted.strip()) > 200:
            cleaned = re.sub(r'\s+', ' ', extracted).strip()
            return cleaned[:500]

        # Readability extraction (Good for general web pages)

        doc = Document(html)
        clean_html = doc.summary()

        soup = BeautifulSoup(clean_html, 'html.parser')

        for tag in soup(['script', 'style', 'nav', 'footer', 'header', 'aside', 'form', 'noscript']):
            tag.decompose()

        text = soup.get_text(separator=' ', strip=True)
        cleaned = re.sub(r'\s+', ' ', text).strip()

        if cleaned:
            return cleaned[:500]
        return "Error: Unable to extract meaningful content from the page."
    except requests.exceptions.Timeout:
        return "Error: The request timed out while trying to access the URL."
    except requests.exceptions.HTTPError as e:
        return f"Error: HTTP error occurred while trying to access the URL. Details: {str(e)}"
    
    except requests.exceptions.RequestException as e:
        return f"Error: An error occurred while trying to access the URL. Details: {str(e)}"
    except Exception as e:
        return f"Error: An unexpected error occurred. Details: {str(e)}"
        


