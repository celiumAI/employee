from crewai import Agent, Task, Crew, Process

from langchain.llms.ollama import Ollama
import random

from langchain.tools import tool

llm = Ollama(model="mistral:instruct")

def run_task(tasks, agents):
    crew = Crew(
        agents=agents,
        tasks=tasks,
        verbose=2,
        process=Process.sequential
    )
    return crew.kickoff()

@tool("interpret task")
def interpret_task(query):
    """
    Interpret a task using a large language model and a query to find the most relevant information.
    Input is a string that contains the plain text prompt that is used to generate the output.
    Output is a string that contains the generated text.
    """
    interpreter = Agent(
        role="interpreter",
        goal="you interpret and find value from the given task in a way that is more understandable without losing depth",
        backstory="you have learned to identify core concepts without losing depth. you are able to interpret the given task and find the most relevant information.",
        verbose=True,
        llm=llm,
    )

    task = Task(
        description=query,
        agent=interpreter
    )

    result = run_task([task], [interpreter])

    return llm(result)

def run_query(query: str) -> str:
    interpreter = Agent(
        role="interpreter",
        goal="you use large language models and need to interpret and find value from the given task in a way that is more understandable without losing depth",
        backstory="as a manager you bear the responsibility of ensuring that the task is completed to a satisfactory level. you deal with a lot of people and have to make sure that everyone is on the same page.",
        verbose=True,
        llm=llm,
        tools=[interpret_task],
        allow_delegation=True
    )

    recruiter = Agent(
        role="recruiter",
        goal="you need to come up with an agile team of individual employees that can solve the given task. its important to first understand the given task",
        backstory="the recruiter uses their experience to find the right people for the job. they have a lot of connections and know how to find the right people for the job.",
        verbose=True,
        llm=llm,
        tools=[],
    )

    # manager = Agent(
    #     role="manager",
    #     goal="you need to rephrase the given task in a way that is more understandable for the recruiter",
    #     backstory="as a manager you bear the responsibility of ensuring that the task is completed to a satisfactory level. you deal with a lot of people and have to make sure that everyone is on the same page.",
    #     verbose=True,
    #     llm=llm,
    #     tools=[chat],
    #     allow_delegation=True
    # )


    task = Task(
        description=query,
        agent=interpreter
    )

    result = run_task([task], [interpreter])
    return result


