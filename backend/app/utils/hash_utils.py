"""
Utilities for hashing notebooks and parameters to detect duplicate executions.
"""
import hashlib
import json
import re
from typing import Dict, Any, Union
import nbformat


def get_notebook_hash(notebook_content: Union[str, bytes], strip_outputs: bool = True) -> str:
    """
    Compute a hash of the notebook content, optionally stripping outputs first.
    
    Args:
        notebook_content: The notebook content as a string or bytes
        strip_outputs: Whether to remove cell outputs before hashing
        
    Returns:
        A hex string hash of the notebook content
    """
    if isinstance(notebook_content, bytes):
        notebook_content = notebook_content.decode('utf-8')
    
    # Parse the notebook
    if strip_outputs:
        notebook = nbformat.reads(notebook_content, as_version=4)
        
        # Remove outputs and execution counts from cells
        for cell in notebook.cells:
            if cell.cell_type == 'code':
                cell.outputs = []
                cell.execution_count = None
        
        # Convert back to string
        notebook_content = nbformat.writes(notebook)
    
    # Compute hash
    return hashlib.sha256(notebook_content.encode('utf-8')).hexdigest()


def get_parameters_hash(parameters: Dict[str, Any]) -> str:
    """
    Compute a hash of execution parameters.
    
    Args:
        parameters: The parameters dictionary
        
    Returns:
        A hex string hash of the parameters
    """
    # Sort keys to ensure consistent hashing regardless of order
    parameters_json = json.dumps(parameters, sort_keys=True)
    return hashlib.sha256(parameters_json.encode('utf-8')).hexdigest()


def get_execution_hash(notebook_hash: str, parameters_hash: str) -> str:
    """
    Compute a combined hash for notebook and parameters.
    
    Args:
        notebook_hash: The notebook hash
        parameters_hash: The parameters hash
        
    Returns:
        A hex string hash combining both inputs
    """
    combined = f"{notebook_hash}:{parameters_hash}"
    return hashlib.sha256(combined.encode('utf-8')).hexdigest() 