from crewai import Agent, Task, Crew, Process

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.llms.ollama import Ollama
from langchain.embeddings.ollama import OllamaEmbeddings
from langchain.chains import HypotheticalDocumentEmbedder
from langchain_community.vectorstores import Chroma
from langchain.memory import ConversationSummaryMemory
from .mail import Message, MailBox
from note.model import Node

from langchain.tools import tool

llm = Ollama(model="mistral:instruct")
llm_embeddings = OllamaEmbeddings(model="mistral:instruct")
memory = ConversationSummaryMemory(
    llm=llm, memory_key="chat_history", return_messages=True
)


def run_task(tasks, agents):
    crew = Crew(
        agents=agents,
        tasks=tasks,
        verbose=2,
        process=Process.sequential
    )
    return crew.kickoff()


def get_interpreter():
    interpreter = Agent(
        role="interpreter",
        goal="you interpret and find value from the given task in a way that is more understandable without losing depth",
        backstory="you have learned to identify core concepts without losing depth. you are able to interpret the given task and find the most relevant information.",
        verbose=True,
        llm=llm,
        tools=[get_answer],
        allow_delegation=False
    )
    return interpreter


@tool("get answer")
def get_answer(inquiry: str) -> str:
    """
    Get an answer to a given question.
    using a large language model so define the inquiry as specific as possible.
    Input is a string that contains the plain text inquiry that is the sole context.
    Output is a string that contains the answer.
    """
    return llm(inquiry)

@tool("interpret inquiry")
def interpret(inquiry: str) -> str:
    """
    Interpret what a given piece of text actually means.
    using a large language model and a query to find the most relevant information.
    Input is a string that contains the plain text inquiry that is the sole context.
    Output is a string that contains the interpreted text.
    """

    agent = get_interpreter()

    task = Task(
        description=inquiry,
        agent=agent
    )

    result = run_task([task], [agent])

    return llm(inquiry + result)

@tool("ask manager")
def ask_manager(inquiry: str) -> str:
    """
    Ask the manager for a decision.
    clearly define the question and demand a specific actionable answer.
    input is a string that contains the plain text inquiry that is the sole context.
    output is a string that contains the decision.
    """

    agent = get_assistant()

    task = Task(
        description=inquiry,
        agent=agent
    )

    result = run_task([task], [agent])

    return llm(inquiry + result)

@tool("ask assistant")
def ask(inquiry: str) -> str:
    """
    Ask the assistant any question.
    the assistant is a large language model that is able to answer questions.
    clearly define the question and the assistant will answer it.
    input is a string that contains the plain text inquiry that is the sole context.
    output is a string that contains the answer.
    """

    agent = get_assistant()

    task = Task(
        description=inquiry,
        agent=agent
    )

    result = run_task([task], [agent])

    return llm(inquiry + result)


def get_context(nodes: list[Node], inquiry: str) -> str:
    """
    Get check past conversations for context.
    We have a lot of information that can be used to answer questions.
    so we can use that information to answer questions.
    input is a string that contains the plain text inquiry that is the sole context.
    output is a string that contains the answer.
    """
    documents = []
    for node in nodes:
        print(node)
        if node.sender != "manager":
            continue
        text = str(node)
        print(text)
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=512, chunk_overlap=128)
        docs = text_splitter.split_text(text)
        documents += docs
    embeddings = HypotheticalDocumentEmbedder.from_llm(llm, llm_embeddings, "web_search")
    db = Chroma.from_texts(documents, embeddings)
    docs = db.similarity_search(inquiry)
    response = "\n".join([doc.page_content for doc in docs])
    print(response)
    return response


def get_assistant():
    assistant = Agent(
        role="assistant",
        goal="you are an assistant that obediently answers questions",
        backstory="you do exactly what is asked of you and nothing else. you carfully consider the question and answer it after reflecting deeply. reflect before you give your final answer. make sure you show your work. its best if you first get some context",
        verbose=True,
        llm=llm,
        tools=[interpret, get_answer],
        allow_delegation=False
    )
    return assistant


 
def do_work(assignment: str) -> str:
    manager = Agent(
        role="router",
        goal="you distribute tasks to the right agents",
        backstory="you do exactly what is asked of you and nothing else. its best if you thorougly review the context",
        verbose=True,
        llm=llm,
        tools=[interpret, get_answer],
        allow_delegation=True
    )

    mailbox = MailBox()
    context = get_context(mailbox.nodes, assignment)

    task = Task(
        description=f"# assignment\n{assignment}\n# context\n{context}",
        agent=manager
    )

    result = run_task([task], [manager, get_assistant(), get_interpreter()])
    return result