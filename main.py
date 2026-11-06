from src.tools.tools import web_search, scrape_url
from rich import print
output = scrape_url("https://www.quora.com/What-are-the-latest-innovations-in-artificial-intelligence-and-machine-learning")
print(output)