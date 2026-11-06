from src.agents.agents import build_search_agent, build_scrape_agent, writer_chain, critic_chain
from collections.abc import Callable
import groq

def run_research_pipeline(
    topic: str,
    progress_callback: Callable[[str], None] | None = None,
) -> dict:
    state = {}
    # step 1 - search agent
    if progress_callback:
        progress_callback("Searching for reliable sources")
    print('\n'+'='*50)
    print('step 1 - search agent is working ...')
    print('='*50)

    search_agent = build_search_agent()
    search_results = search_agent.invoke({
        'messages': [('user', f"Find recent, reliable and detailed information on the topic: {topic}. Provide titles, urls, and snippets of the top 5 results.")]
    })
    state['search_results'] = search_results['messages'][-1].content
    print('\n search results: \n', state['search_results'])


    #step 2 - scrape agent
    if progress_callback:
        progress_callback("Reading selected sources")
    print('\n'+'='*50)
    print('step 2 - scrape agent is working ...')
    print('='*50)

    reader_agent = build_scrape_agent()
    reader_results = reader_agent.invoke({
        'messages': [('user',
          f"Based on the following search results about '{topic}', "
          f"pick the most relevant urls and scrape the content of those pages.\n\n"
          f"Search Results:\n{state['search_results'][:800]}"
          )]
    })
    state['scrape_content'] = reader_results['messages'][-1].content
    print('\n scrape content: \n', state['scrape_content'])


    # step 3 - writer report
    if progress_callback:
        progress_callback("Drafting the research report")
    print('\n'+'='*50)
    print('step 3 - writer chain is working ...')
    print('='*50)

    research_combined = {
        f"search_results": state['search_results'],
        f"scrape_content": state['scrape_content']
    }

    state['report'] = writer_chain.invoke({
        'topic': topic,
        'research': research_combined
    })

    print('\n final report: \n', state['report'])


    # step 4 - critic report
    if progress_callback:
        progress_callback("Reviewing the report")
    print('\n'+'='*50)
    print('step 4 - critic chain is working ...')
    print('='*50)

    try:
        state['feedback'] = critic_chain.invoke({
            'report': state['report']
        })
    except groq.RateLimitError as exc:
        state['feedback'] = (
            'The critique step was skipped because Groq rate limits were reached. '
            'Please wait a moment and try again. '
            f'Details: {exc}'
        )
    except Exception as exc:
        state['feedback'] = f'Critique step failed: {exc}'

    print('\n feedback: \n', state['feedback'])
    return state



