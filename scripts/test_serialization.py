#!/usr/bin/env python3
"""
Test script to verify that the serialization fixes are working correctly
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from schemas.utils import safe_serialize, safe_json_response
from datetime import datetime, date
import pandas as pd
import numpy as np

def test_safe_serialize():
    """Test the safe_serialize function with various data types"""
    print("Testing safe_serialize function...")
    
    # Test basic types
    assert safe_serialize("test") == "test"
    assert safe_serialize(123) == 123
    assert safe_serialize(123.45) == 123.45
    assert safe_serialize(True) == True
    assert safe_serialize(None) == None
    
    # Test datetime objects
    dt = datetime(2024, 1, 1, 12, 0, 0)
    assert safe_serialize(dt) == "2024-01-01T12:00:00"
    
    # Test date objects
    d = date(2024, 1, 1)
    assert safe_serialize(d) == "2024-01-01"
    
    # Test dictionaries
    test_dict = {
        "string": "test",
        "number": 123,
        "date": dt,
        "nested": {"key": "value"}
    }
    serialized = safe_serialize(test_dict)
    assert serialized["string"] == "test"
    assert serialized["number"] == 123
    assert serialized["date"] == "2024-01-01T12:00:00"
    
    # Test lists
    test_list = ["a", 1, dt, {"key": "value"}]
    serialized = safe_serialize(test_list)
    assert serialized[0] == "a"
    assert serialized[1] == 1
    assert serialized[2] == "2024-01-01T12:00:00"
    
    # Test pandas DataFrame
    df = pd.DataFrame({
        "col1": [1, 2, 3],
        "col2": ["a", "b", "c"],
        "col3": [dt, dt, dt]
    })
    serialized = safe_serialize(df.to_dict(orient="records"))
    assert len(serialized) == 3
    assert serialized[0]["col1"] == 1
    assert serialized[0]["col2"] == "a"
    assert serialized[0]["col3"] == "2024-01-01T12:00:00"
    
    # Test numpy arrays
    arr = np.array([1, 2, 3])
    serialized = safe_serialize(arr)
    assert serialized == [1, 2, 3]
    
    print("✅ All safe_serialize tests passed!")

def test_safe_json_response():
    """Test the safe_json_response function"""
    print("Testing safe_json_response function...")
    
    # Test successful serialization
    test_data = {
        "message": "test",
        "data": [1, 2, 3],
        "date": datetime(2024, 1, 1)
    }
    result = safe_json_response(test_data)
    assert result["message"] == "test"
    assert result["data"] == [1, 2, 3]
    assert result["date"] == "2024-01-01T00:00:00"
    
    # Test with non-serializable object (should handle gracefully)
    class NonSerializable:
        def __init__(self):
            self.value = "test"
    
    non_serializable = NonSerializable()
    result = safe_json_response(non_serializable)
    print(f"Result type: {type(result)}")
    print(f"Result: {result}")
    # Should return a dictionary with error information
    assert isinstance(result, dict)
    assert "error" in result
    
    print("✅ All safe_json_response tests passed!")

if __name__ == "__main__":
    print("Running serialization tests...")
    test_safe_serialize()
    test_safe_json_response()
    print("🎉 All tests passed! The serialization fixes are working correctly.") 