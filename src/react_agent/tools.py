"""This module provides example tools for web scraping and search functionality.

It includes a basic Tavily search function (as an example)

These tools are intended as free examples to get started. For production use,
consider implementing more robust and specialized tools tailored to your needs.
"""
import os
from typing import Any, Callable, List, Optional, cast
from typing_extensions import Annotated

from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import InjectedToolArg
from langchain.tools.retriever import create_retriever_tool

from react_agent.configuration import Configuration
from react_agent.rag_retriever import get_retriever

from langchain_core.tools import tool
from e2b_code_interpreter import Sandbox


retriever = get_retriever()


async def search(
    query: str, *, config: Annotated[RunnableConfig, InjectedToolArg]
) -> Optional[list[dict[str, Any]]]:
    """Search for general web results.

    This function performs a search using the Tavily search engine, which is designed
    to provide comprehensive, accurate, and trusted results. It's particularly useful
    for answering questions about current events.
    """
    configuration = Configuration.from_runnable_config(config)
    wrapped = TavilySearchResults(max_results=configuration.max_search_results)
    result = await wrapped.ainvoke({"query": query})
    return cast(list[dict[str, Any]], result)


async def python_interpretor(
    code: str, *, config: Annotated[RunnableConfig, InjectedToolArg]
) -> Optional[list[dict[str, Any]]]:
    """Execute python code.

    This function executes python code in a sandbox environment. It's particularly useful
    for executing & testing code to see if it's working as expected.
    """
    configuration = Configuration.from_runnable_config(config)
    sbx = Sandbox()
    execution = sbx.run_code(code)
    print(execution.logs)

    return cast(list[dict[str, Any]], execution)
    
    
retriever_tool = create_retriever_tool(
    retriever,
    "retrieve_code_data",
    "Search and return relevant code section for user query.",
)

TOOLS: List[Callable[..., Any]] = [search, python_interpretor, retriever_tool]
