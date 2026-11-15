from langchain.agents import create_agent
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from tools import web_search , scrape_url 
from dotenv import load_dotenv

load_dotenv()

llm = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0,
    max_tokens=512,
    reasoning_effort="low",
)

def build_search_agent():
    return create_agent(
        model = llm,
        tools = [web_search],
    )
    
def build_scrape_agent():
    return create_agent(
        model = llm,
        tools = [scrape_url],
    )
    

writer_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "Write concise, clear, factual reports. Use only supplied research; "
        "do not invent claims or sources."
    ),
    (
        "human",
        """Write a 150-word report on {topic} using this research:
{research}

Include a brief introduction, key findings, conclusion, and supplied source
URLs. Keep it factual and avoid repetition."""
    ),
])

writer_chain = writer_prompt | llm.bind(max_tokens=1024) | StrOutputParser()



critic_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "Briefly and fairly assess report accuracy, evidence, and clarity. "
        "Do not assume unsupported claims are true."
    ),
    (
        "human",
        """Review this report:
{report}

Give an overall score out of 10, one strength, one improvement, and a
one-sentence verdict. Keep the review under 60 words."""
    ),
])

critic_chain = critic_prompt | llm | StrOutputParser()
