from langchain_core.prompts import ChatPromptTemplate
from core.summarizer import get_llm

def generate_email(summary, action_items, decisions):

    llm = get_llm()

    prompt = ChatPromptTemplate.from_template("""
    You are a professional executive assistant.

    Create a concise follow-up email based on:

    Meeting Summary:
    {summary}

    Action Items:
    {action_items}

    Key Decisions:
    {decisions}

    Generate:
    1. Email Subject
    2. Professional Email Body
    """)

    chain = prompt | llm

    response = chain.invoke({
        "summary": summary,
        "action_items": action_items,
        "decisions": decisions
    })

    return response.content