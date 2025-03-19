"""
Notebook Metadata Extractor

This module provides functionality to extract metadata from Jupyter notebooks,
including parameters, requirements, resource specifications, and identity information.
It supports various metadata formats and conventions used in notebooks.
"""

import json
import logging
import nbformat
from typing import Dict, List, Optional, Any, Tuple
import re

logger = logging.getLogger(__name__)


class NotebookMetadataExtractor:
    """
    Extract and parse metadata from Jupyter notebooks.
    
    This class handles extracting various types of metadata from notebooks:
    - Parameters: Input parameters with types, defaults, and descriptions
    - Requirements: Python package dependencies
    - Resources: CPU, memory, and other resource requirements
    - Identity: Name, description, author, and tags
    
    The extractor supports multiple metadata formats:
    1. Notebook-level metadata in the notebook JSON
    2. Cell-level metadata in parameter cells
    3. Special comment formats in code cells
    """
    
    def __init__(self, notebook_content: bytes):
        """
        Initialize with notebook content.
        
        Args:
            notebook_content: String containing the notebook JSON content
        """
        # Load the notebook to determine its version
        notebook = nbformat.reads(notebook_content, as_version=nbformat.NO_CONVERT)
        
        # Extract the version
        version = notebook['nbformat']
        
        # Handle different versions
        if version == 4:
            self.notebook = nbformat.reads(notebook_content, as_version=4)
        elif version == 3:
            self.notebook = nbformat.reads(notebook_content, as_version=3)
        else:
            raise ValueError(f"Unsupported notebook version: {version}")            
    
    @staticmethod
    def parse_notebook(notebook_content: bytes) -> Dict[str, Any]:
        """Parse notebook content and extract metadata and parameters"""
        notebook = json.loads(notebook_content)
        
        # Extract metadata from notebook
        metadata = {}
        if 'metadata' in notebook and 'notebook_spec' in notebook['metadata']:
            metadata = notebook['metadata']['notebook_spec']
        
        # Extract parameters from cells
        parameters = []
        for cell in notebook.get('cells', []):
            if cell.cell_type == 'code' and 'tags' in cell.metadata and 'parameters' in cell.metadata['tags']:
                for param in cell['metadata']['parameters']:
                    parameters.append(param)


        return {
            'metadata': metadata,
            'parameters': parameters
        }
    
    def extract_metadata(self) -> Dict[str, Any]:
        """
        Extract all metadata from a notebook.
        
        Args:
            notebook_content: Raw notebook content as bytes
            
        Returns:
            Dictionary containing extracted metadata         
        """
                        
        # Extract metadata
        metadata = {
            'parameters': self.extract_parameters(self.notebook),
            'requirements': self.extract_requirements(self.notebook),
            'identity': self.extract_identity(self.notebook),
            'resources': self.extract_resources(self.notebook)
        }
        
        return metadata
    
    def extract_parameters(self, notebook: Dict) -> List[Dict]:
        """
        Extract parameters from a notebook.
        
        Args:
            notebook: Parsed notebook object
            
        Returns:
            List of parameter dictionaries
        """
        parameters = []
        
        # Look for cells tagged with 'parameters'
        for cell in notebook.cells:
            if cell.cell_type == 'code' and 'tags' in cell.metadata and 'parameters' in cell.metadata['tags']:
                # Parse the parameter cell
                lines = cell.source.split('\n')
                for line in lines:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        # Extract parameter name, type, and default value
                        param_info = self._parse_parameter_line(line)
                        if param_info:
                            parameters.append(param_info)
        
        return parameters
    
    def _parse_parameter_line(self, line: str) -> Optional[Dict]:
        """Parse a single parameter line."""
        try:
            # Split by '=' and get the left part (name and type)
            name_type, value_part = line.split('=', 1)
            name_type = name_type.strip()
            
            # Extract name and type
            if ':' in name_type:
                name, param_type = name_type.split(':', 1)
                name = name.strip()
                param_type = param_type.strip()
            else:
                name = name_type
                param_type = 'Any'
            
            # Extract default value
            value_part = value_part.strip()
            
            # Check for JSON metadata in comments
            metadata = {}
            if '#' in value_part:
                value_str, comment = value_part.split('#', 1)
                value_str = value_str.strip()
                comment = comment.strip()
                
                # Try to extract JSON metadata from comment
                try:
                    if comment.startswith('{') and comment.endswith('}'):
                        metadata = json.loads(comment)
                except json.JSONDecodeError:
                    pass
            else:
                value_str = value_part
            
            # Create parameter info
            param_info = {
                'name': name,
                'type': param_type,
                'default': value_str
            }
            
            # Add metadata if available
            if metadata:
                param_info.update(metadata)
            
            return param_info
        except Exception:
            return None
    
    def extract_requirements(self, notebook: Dict) -> Dict[str, str]:
        """
        Extract package requirements from a notebook.
        
        Args:
            notebook: Parsed notebook object
            
        Returns:
            Dictionary of package requirements
        """
        # First check if requirements are in notebook_spec metadata
        if 'notebook_spec' in notebook.metadata and 'requirements' in notebook.metadata['notebook_spec']:
            return notebook.metadata['notebook_spec']['requirements']

        return {}
    
    def extract_resources(self, notebook: Dict) -> Dict[str, Any]:
        """
        Extract resource requirements from a notebook.
        
        Args:
            notebook: Parsed notebook object
            
        Returns:
            Dictionary of resource requirements
        """
        resources = {
            'cpu_milli': 1000,  # Default: 1 CPU core
            'memory_mib': 2048,  # Default: 2 GB
            'timeout_seconds': 3600  # Default: 1 hour
        }
        
        # Check if resources are specified in notebook_spec metadata
        if 'notebook_spec' in notebook.metadata:
            spec = notebook.metadata['notebook_spec']
            if 'resources' in spec:
                resources.update(spec['resources'])
            elif 'cpu' in spec:
                resources['cpu_milli'] = int(float(spec['cpu']) * 1000)
            elif 'memory' in spec:
                resources['memory_mib'] = int(spec['memory'])
            elif 'timeout' in spec:
                resources['timeout_seconds'] = int(spec['timeout'])
        
        return resources
    
    def extract_identity(self, notebook: Dict) -> Dict[str, Any]:
        """
        Extract identity information from a notebook.
        
        Args:
            notebook: Parsed notebook object
            
        Returns:
            Dictionary of identity information
        """
        identity = {
            'name': '',
            'description': '',
            'tags': [],
            'python_version': '3.10'  # Default Python version
        }
        
        # Check if identity is specified in notebook_spec metadata
        if 'notebook_spec' in notebook.metadata:            
            spec = notebook.metadata['notebook_spec']
            if 'name' in spec:
                identity['name'] = spec['name']
            if 'description' in spec:
                identity['description'] = spec['description']
            if 'tags' in spec:
                identity['tags'] = spec['tags']
            if 'python_version' in spec:
                identity['python_version'] = spec['python_version']
        
        return identity 