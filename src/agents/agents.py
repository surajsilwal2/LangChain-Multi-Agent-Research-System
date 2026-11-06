from langchain.agents import create_agent
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from src.tools.tools import web_search, scrape_url
from dotenv import load_dotenv
import os

load_dotenv()

# Groq model name can be set via env; default is an actively available model.
llm = ChatGroq(
    model=os.getenv("GROQ_MODEL", "openai/gpt-oss-20b"),
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0
)

# first agent
def build_search_agent():
    return create_agent(
        model=llm,
        tools=[web_search]
    )

# second agent
def build_scrape_agent():
    return create_agent(
        model=llm,
        tools=[scrape_url]
    )


# writer chain
writer_prompt = ChatPromptTemplate.from_messages([
    ("system", "you are a expert research writer. You will be given a topic and you will write a detailed research report on the topic. You will use the information provided by the agents to write the report. You will not make up any information. You will only use the information provided by the agents. You will write in a clear and concise manner. You will use proper grammar and spelling. You will use headings and subheadings to organize the report. You will use bullet points and numbered lists to present information. You will use tables and charts to present data. You will use images and diagrams to illustrate concepts. You will provide references for all information used in the report."),

    ("human", """Write a detailed research report on the topic: {topic}. Research Gathered: {research}.  Use the information provided by the agents to write the report. Do not make up any information. Only use the information provided by the agents. Write in a clear and concise manner. Use proper grammar and spelling. Use headings and subheadings to organize the report. Use bullet points and numbered lists to present information. Use tables and charts to present data. Use images and diagrams to illustrate concepts. Provide references for all information used in the report."""),
    ])

writer_chain = writer_prompt | llm | StrOutputParser()


# critic chain
critic_prompt = ChatPromptTemplate.from_messages([
    ("system", "you are a expert research critic. You will be given a research report and you will critique the report. You will provide feedback on the report. You will provide suggestions for improvement. You will provide references for all information used in the critique."),

    ("human", """Critique the following research report: {report}. Provide feedback on the report. Provide suggestions for improvement. Provide references for all information used in the critique. Respond in this exact format: 1. Summary of the report. 2. Strengths of the report. 3. Weaknesses of the report. 4. Suggestions for improvement. 5. References used in the critique. 6.Score: X/10"""),
    ])

critic_chain = critic_prompt | llm | StrOutputParser()