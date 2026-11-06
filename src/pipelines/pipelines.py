# Import the agents and text chains that perform each research stage.
from src.agents.agents import build_search_agent, build_scrape_agent, writer_chain, critic_chain
# The callback lets the UI show progress without making Streamlit a pipeline dependency.
from collections.abc import Callable
# TypeVar preserves the result type of whichever invoke function is retried.
from typing import TypeVar
# time provides a short pause between transient connection retries.
import time
# Groq exception classes let the pipeline retry connection failures and report rate limits.
import groq

# A generic return type allows this helper to wrap agents and text chains alike.
T = TypeVar("T")


def _invoke_with_retry(invoke: Callable[[], T]) -> T:
    """Retry a Groq call up to three times when its connection drops."""
    for attempt in range(3):
        try:
            return invoke()  # Return immediately when the model call succeeds.
        except groq.APIConnectionError:
            if attempt == 2:
                raise  # Preserve the last failure so the UI can report it accurately.
            time.sleep(2 ** attempt)  # Wait 1s, then 2s, before making another attempt.


def run_research_pipeline(
    topic: str,
    progress_callback: Callable[[str], None] | None = None,
) -> dict:
    # Collect each stage's output here; later stages consume earlier results.
    state = {}
    # Tell the UI which stage is starting; terminal runs can omit this callback.
    if progress_callback:
        progress_callback("Searching for reliable sources")
    # Print a clear stage boundary in terminal logs.
    print('\n'+'='*50)
    print('step 1 - search agent is working ...')
    print('='*50)

    # Create an agent with the search tool, then ask for five sourced results.
    search_agent = build_search_agent()
    search_results = _invoke_with_retry(lambda: search_agent.invoke({
        'messages': [('user', f"Find recent, reliable and detailed information on the topic: {topic}. Provide titles, urls, and snippets of the top 5 results.")]
    }))
    # Agent state includes a message history; keep the latest assistant response.
    state['search_results'] = search_results['messages'][-1].content
    print('\n search results: \n', state['search_results'])


    # Move the UI to source reading and mark the next stage in terminal logs.
    if progress_callback:
        progress_callback("Reading selected sources")
    print('\n'+'='*50)
    print('step 2 - scrape agent is working ...')
    print('='*50)

    # Give the reader the topic and a shortened search response so it can select URLs.
    reader_agent = build_scrape_agent()
    reader_results = _invoke_with_retry(
        lambda: reader_agent.invoke(
            {
                'messages': [('user',
                    f"Based on the following search results about '{topic}', "
                    f"pick the most relevant urls and scrape the content of those pages.\n\n"
                    f"Search Results:\n{state['search_results'][:800]}"
                )]
            }
        )
    )
    # Save the reader agent's final response for the writer stage.
    state['scrape_content'] = reader_results['messages'][-1].content
    print('\n scrape content: \n', state['scrape_content'])


    # Let the UI show report drafting, then log the same stage for terminal users.
    if progress_callback:
        progress_callback("Drafting the research report")
    print('\n'+'='*50)
    print('step 3 - writer chain is working ...')
    print('='*50)

    # Keep search evidence and extracted page text distinct in the writer input.
    research_combined = {
        f"search_results": state['search_results'],
        f"scrape_content": state['scrape_content']
    }

    # Fill the writer prompt's topic/research fields and store its plain-text report.
    state['report'] = _invoke_with_retry(lambda: writer_chain.invoke({
        'topic': topic,
        'research': research_combined
    }))

    print('\n final report: \n', state['report'])


    # Start the optional critique stage and keep progress visible in the UI.
    if progress_callback:
        progress_callback("Reviewing the report")
    print('\n'+'='*50)
    print('step 4 - critic chain is working ...')
    print('='*50)

    try:
        # Ask the critic to review the finished report; transient connection errors retry.
        state['feedback'] = _invoke_with_retry(lambda: critic_chain.invoke({
            'report': state['report']
        }))
    except groq.RateLimitError as exc:
        # Preserve the report even when Groq will not accept another critique request.
        state['feedback'] = (
            'The critique step was skipped because Groq rate limits were reached. '
            'Please wait a moment and try again. '
            f'Details: {exc}'
        )
    except Exception as exc:
        # Treat other critique-only errors as feedback so earlier results remain usable.
        state['feedback'] = f'Critique step failed: {exc}'

    # Return all stage outputs for the terminal caller or UI to render.
    print('\n feedback: \n', state['feedback'])
    return state



