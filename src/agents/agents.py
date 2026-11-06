# LangChain provides the agent factory, model wrapper, prompt template, and
# parser used to build the research workflow.
from langchain.agents import create_agent
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
# These tools are exposed to the agents so they can search and read web pages.
from src.tools.tools import web_search, scrape_url
# dotenv loads local .env settings, and os reads the configured model and key.
from dotenv import load_dotenv
import os

# Load environment variables before creating any provider clients.
load_dotenv()

# Create the shared Groq chat model used by both agents and both text chains.
llm = ChatGroq(
    model=os.getenv("GROQ_MODEL", "openai/gpt-oss-20b"),  # Use configured model or default.
    api_key=os.getenv("GROQ_API_KEY"),  # Authenticate with the key stored in the environment.
    temperature=0  # Keep generated research and critique relatively consistent.
)

# Build an agent that can decide when to call the web-search tool.
def build_search_agent():
    return create_agent(
        model=llm,  # The model interprets the request and formats the final answer.
        tools=[web_search]  # Only this tool is available to the search agent.
    )

# Build a separate agent that can choose and read source URLs.
def build_scrape_agent():
    return create_agent(
        model=llm,  # Reuse the same configured Groq model.
        tools=[scrape_url]  # Limit this agent to page extraction.
    )


# The system message sets the writer's role and evidence constraints; the user
# message supplies the topic and research data when the chain is invoked.
writer_prompt = ChatPromptTemplate.from_messages([
    ("system", "you are a expert research writer. You will be given a topic and you will write a detailed research report on the topic. You will use the information provided by the agents to write the report. You will not make up any information. You will only use the information provided by the agents. You will write in a clear and concise manner. You will use proper grammar and spelling. You will use headings and subheadings to organize the report. You will use bullet points and numbered lists to present information. You will use tables and charts to present data. You will use images and diagrams to illustrate concepts. You will provide references for all information used in the report."),

    ("human", """Write a detailed research report on the topic: {topic}. Research Gathered: {research}.  Use the information provided by the agents to write the report. Do not make up any information. Only use the information provided by the agents. Write in a clear and concise manner. Use proper grammar and spelling. Use headings and subheadings to organize the report. Use bullet points and numbered lists to present information. Use tables and charts to present data. Use images and diagrams to illustrate concepts. Provide references for all information used in the report."""),
    ])

# The pipe sends prompt values to the model, then converts its message response
# into plain text for the pipeline and Streamlit UI.
writer_chain = writer_prompt | llm | StrOutputParser()


# Give the critic the same evidence-only constraint and require a predictable
# response format so the UI can find and display its score.
critic_prompt = ChatPromptTemplate.from_messages([
    ("system", "you are a expert research critic. You will be given a research report and you will critique the report. You will provide feedback on the report. You will provide suggestions for improvement. You will provide references for all information used in the critique."),

    ("human", """Critique the following research report: {report}. Provide feedback on the report. Provide suggestions for improvement. Provide references for all information used in the critique. Respond in this exact format: 1. Summary of the report. 2. Strengths of the report. 3. Weaknesses of the report. 4. Suggestions for improvement. 5. References used in the critique. 6.Score: X/10"""),
    ])

# Format the report for the critic, call Groq, and return the critique as text.
critic_chain = critic_prompt | llm | StrOutputParser()