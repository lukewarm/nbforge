import pytest
import json
from unittest.mock import MagicMock, patch
from app.services.execution_service import ExecutionService

class TestParameterTypeConversion:
    @pytest.fixture
    def execution_service(self):
        mock_db = MagicMock()
        return ExecutionService(mock_db)
    
    @pytest.mark.asyncio
    async def test_convert_parameters_using_metadata(self, execution_service):
        # Mock the entire NotebookMetadataExtractor
        mock_extractor = MagicMock()
        mock_extractor.extract_metadata.return_value = {
            'parameters': [
                {'name': 'int_param', 'type': 'int', 'default': '10'},
                {'name': 'float_param', 'type': 'float', 'default': '3.14'},
                {'name': 'bool_param', 'type': 'bool', 'default': 'False'},
                {'name': 'str_param', 'type': 'str', 'default': 'hello'},
                {'name': 'list_param', 'type': 'List[str]', 'default': '["item1", "item2"]'},
                {'name': 'dict_param', 'type': 'Dict', 'default': '{"key": "value"}'}
            ]
        }
        
        # Patch the NotebookMetadataExtractor class
        with patch('app.services.execution_service.NotebookMetadataExtractor', return_value=mock_extractor):
            # Input parameters (as they would come from API)
            input_params = {
                'int_param': '42',
                'float_param': '2.718',
                'bool_param': 'true',
                'str_param': 'world',
                'list_param': '["one", "two", "three"]',
                'dict_param': '{"name": "test", "value": 123}'
            }
            
            # Execute the conversion
            result = await execution_service._convert_parameters_using_metadata(
                b'mock_notebook_content',
                input_params
            )
            
            # Verify the correct types are returned
            assert isinstance(result['int_param'], int)
            assert result['int_param'] == 42
            
            assert isinstance(result['float_param'], float)
            assert result['float_param'] == 2.718
            
            assert isinstance(result['bool_param'], bool)
            assert result['bool_param'] is True
            
            assert isinstance(result['str_param'], str)
            assert result['str_param'] == 'world'
            
            assert isinstance(result['list_param'], list)
            assert result['list_param'] == ['one', 'two', 'three']
            
            assert isinstance(result['dict_param'], dict)
            assert result['dict_param'] == {'name': 'test', 'value': 123}
    
    @pytest.mark.asyncio
    async def test_convert_parameters_with_edge_cases(self, execution_service):
        # Mock the entire NotebookMetadataExtractor
        mock_extractor = MagicMock()
        mock_extractor.extract_metadata.return_value = {
            'parameters': [
                {'name': 'already_int', 'type': 'int', 'default': '10'},
                {'name': 'empty_string', 'type': 'str', 'default': ''},
                {'name': 'none_value', 'type': 'str', 'default': 'None'},
                {'name': 'comma_list', 'type': 'List[str]', 'default': '[]'},
                {'name': 'unknown_param', 'type': 'unknown', 'default': '123'},
                {'name': 'invalid_json', 'type': 'Dict', 'default': '{}'}
            ]
        }
        
        # Patch the NotebookMetadataExtractor class
        with patch('app.services.execution_service.NotebookMetadataExtractor', return_value=mock_extractor):
            # Input parameters with edge cases
            input_params = {
                'already_int': 42,  # Already an integer
                'empty_string': '',  # Empty string
                'none_value': None,  # None value
                'comma_list': 'a,b,c',  # Comma-separated string
                'unknown_param': 'xyz',  # Unknown parameter type
                'invalid_json': '{not valid json}',  # Invalid JSON
                'missing_type': 'value'  # No type definition
            }
            
            # Execute the conversion
            result = await execution_service._convert_parameters_using_metadata(
                b'mock_notebook_content',
                input_params
            )
            
            # Verify edge cases
            assert isinstance(result['already_int'], int)
            assert result['already_int'] == 42
            
            assert result['empty_string'] == ''
            assert result['none_value'] is None
            
            assert isinstance(result['comma_list'], list)
            assert result['comma_list'] == ['a', 'b', 'c']
            
            assert result['unknown_param'] == 'xyz'
            assert result['invalid_json'] == '{not valid json}'
            assert result['missing_type'] == 'value'
    
    @pytest.mark.asyncio
    async def test_handle_no_parameters(self, execution_service):
        # Mock the entire NotebookMetadataExtractor
        mock_extractor = MagicMock()
        mock_extractor.extract_metadata.return_value = {'parameters': []}
        
        # Patch the NotebookMetadataExtractor class
        with patch('app.services.execution_service.NotebookMetadataExtractor', return_value=mock_extractor):
            # Input parameters
            input_params = {'param1': '123', 'param2': 'abc'}
            
            # Execute the conversion
            result = await execution_service._convert_parameters_using_metadata(
                b'mock_notebook_content',
                input_params
            )
            
            # Should return parameters unchanged if no metadata
            assert result == input_params 