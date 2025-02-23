"""Utility & helper functions."""

import os
import json
import re
import ast
from typing import List

from langchain.chat_models import init_chat_model
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import BaseMessage
from langchain_core.documents import Document


def get_message_text(msg: BaseMessage) -> str:
    """Get the text content of a message."""
    content = msg.content
    if isinstance(content, str):
        return content
    elif isinstance(content, dict):
        return content.get("text", "")
    else:
        txts = [c if isinstance(c, str) else (c.get("text") or "") for c in content]
        return "".join(txts).strip()


def load_chat_model(fully_specified_name: str) -> BaseChatModel:
    """Load a chat model from a fully specified name.

    Args:
        fully_specified_name (str): String in the format 'provider/model'.
    """
    provider, model = fully_specified_name.split("/", maxsplit=1)
    return init_chat_model(model, model_provider=provider)


def extract_functions(code_text: str) -> List[str]:
    try:
        # Parse the code text into an AST
        tree = ast.parse(code_text)
        
        # Find all function definitions
        function_nodes = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
        
        # Extract the source code for each function
        functions = []
        for node in function_nodes:
            # Get the line numbers for the function
            start_line = node.lineno - 1
            end_line = node.end_lineno
            
            # Split the code text into lines and extract the function definition
            lines = code_text.split('\n')
            function_code = '\n'.join(lines[start_line:end_line])
            functions.append(function_code)
            
        return functions
    
    except SyntaxError:
        print("Syntax error in code")
        return []
    
    
def extract_elements(code):
    # Extract identifiers (variable assignments, including multi-line values)
    identifier_pattern = re.compile(r'^(\w+\s*=\s*(?:""".*?"""|\'\'\'.*?\'\'\'|\([^)]*\)|[^\n]+))', re.MULTILINE | re.DOTALL)
    identifiers = identifier_pattern.findall(code)
    functions = extract_functions(code)
    return {
        "identifiers": identifiers,
        "functions": functions,
    }



ext_to_consider = ['py']
def create_function_documents(file_, functions):
    docs = []
    for func in functions:
        doc = Document(
            page_content=func,
            metadata={"type": "function", "file": file_}
        )
        docs.append(doc)
    return docs


def create_identifiers_documents(file_, identifiers):
    docs = []
    for item in identifiers:
        doc = Document(
            page_content=item,
            metadata={"type": "identifier", "file": file_}
        )
        docs.append(doc)
    return docs


def get_documents(directory):
    documents = []
    for root, dirs, files in os.walk(directory):
        dirs[:] = [d for d in dirs if not d.startswith('__')]
        
        for file in files:
            # Consider python files and exclude files starting with double underscore 
            if not file.startswith('__') and file.split('.')[-1] in ext_to_consider:
                file_path = os.path.join(root, file)
                with open(file_path, 'r') as f:
                    code = f.read()
                    print(f"Reading file: {file_path}")
                    splitted_code = extract_elements(code)
                    identifiers_docs = create_identifiers_documents(file_path, splitted_code["identifiers"])
                    functions_docs = create_function_documents(file_path, splitted_code['functions'])
                    documents.extend(identifiers_docs)
                    documents.extend(functions_docs)
    return documents
    # return "\n\n\n".join(code_data)
