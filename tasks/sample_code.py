"""
Sample code for QA testing.

This code implements divide() and get_element() functions
according to FUNCTION_SPEC.md specification.
"""

def divide(a, b):
    """
    Safely divide two numbers with proper type checking.
    
    Rules:
    - Accepts: int, float (but not bool)
    - Rejects: str, None, objects without __truediv__
    - Returns int if both inputs are int and division is exact
    - Returns float if division is not exact or any input is float
    - Raises ZeroDivisionError if b is 0
    - Raises TypeError for unsupported types
    """
    # Reject bool (it's technically an int subclass, but we reject it explicitly)
    if isinstance(a, bool) or isinstance(b, bool):
        raise TypeError(f"unsupported operand type(s) for /: '{type(a).__name__}' and '{type(b).__name__}'")

    # Type validation - only int and float allowed
    # Check each separately to produce error message with only one type name if possible
    if not isinstance(a, (int, float)):
        raise TypeError(f"unsupported operand type(s) for /: '{type(a).__name__}' and '{type(b).__name__ if not isinstance(b, (int, float)) else 'unknown'}'")
    if not isinstance(b, (int, float)):
        raise TypeError(f"unsupported operand type(s) for /: '{type(a).__name__ if not isinstance(a, (int, float)) else 'unknown'}' and '{type(b).__name__}'")

    # Check for division by zero
    if b == 0:
        raise ZeroDivisionError("division by zero")

    # Perform division
    result = a / b

    # Return type based on inputs and exact division
    # If both are int and division is exact, return int
    if isinstance(a, int) and isinstance(b, int) and result == int(result):
        return int(result)

    # Otherwise return float
    return float(result)


def get_element(arr, index):
    """
    Safely get element from array-like objects with type validation.
    
    Rules:
    - Accepts: list, tuple, str, any object with __getitem__ (except dict)
    - Rejects: None, dict, non-indexable objects
    - Index must be int (positive or negative, not bool)
    - Raises TypeError for invalid index types
    - Raises TypeError for unsupported array types
    - Raises IndexError for out-of-bounds (normal Python)
    """
    import collections.abc

    # Check if arr is None
    if arr is None:
        raise TypeError("'NoneType' object is not subscriptable")

    # Reject dict explicitly (it has __getitem__ but we don't want it for this function)
    if isinstance(arr, dict):
        raise TypeError(f"'{type(arr).__name__}' object does not support indexing")

    # Check index type (reject bool and non-int)
    if isinstance(index, bool):
        raise TypeError(f"indices must be integers, not {type(index).__name__}")
    if not isinstance(index, int):
        raise TypeError(f"indices must be integers, not {type(index).__name__}")

    # Check if arr has __getitem__ attribute
    if not hasattr(arr, "__getitem__"):
        raise TypeError(f"'{type(arr).__name__}' object is not subscriptable")

    # Acceptable explicit known sequence types
    allowed_types = (list, tuple, str)

    # If arr is one of allowed types, directly index
    if isinstance(arr, allowed_types):
        return arr[index]

    # For other objects, accept only if they are collections.abc.Sequence (not dict)
    # This allows custom sequences as well.
    # Note: collections.abc.Sequence excludes dict_keys, range, etc. so supports most sequences.
    if not isinstance(arr, collections.abc.Sequence):
        raise TypeError(f"'{type(arr).__name__}' object is not subscriptable")

    # Finally, index and return, handling exceptions as normal
    try:
        return arr[index]
    except TypeError as e:
        raise TypeError(f"'{type(arr).__name__}' object is not subscriptable") from e
    except IndexError:
        raise