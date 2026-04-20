# Function Specification for sample_code.py

## divide(a, b) Function

### Purpose
Divide two numbers safely with proper type checking and error handling.

### Behavior
```
divide(10, 2)        → 5 (exact int division)
divide(10.0, 2)      → 5.0 (float involved)
divide(10, 2.0)      → 5.0 (float involved)
divide(9, 2)         → 4.5 (non-exact int division → float)
divide(0, 5)         → 0 (zero division is OK)
divide(10, 0)        → ZeroDivisionError (cannot divide by zero)
divide("10", 2)      → TypeError (unsupported type)
divide(10, None)     → TypeError (unsupported type)
```

### Rules
1. If both inputs are integers AND division is exact → return int
2. If division is not exact OR any input is float → return float
3. If divisor is zero → raise ZeroDivisionError
4. If inputs are not numeric → raise TypeError

### Type Checking
- Accepted: int, float
- Rejected: str, list, dict, None, custom objects without `__truediv__`

---

## get_element(arr, index) Function

### Purpose
Safely get element from array-like objects with type validation.

### Behavior
```
get_element([1, 2, 3], 0)      → 1
get_element((1, 2, 3), 1)      → 2
get_element("hello", 2)        → "l" (strings support indexing)
get_element([1, 2, 3], -1)     → 3 (negative indexing OK)
get_element([1, 2, 3], 10)     → IndexError (out of bounds)
get_element([1, 2, 3], "0")    → TypeError (invalid index type)
get_element([1, 2, 3], 1.5)    → TypeError (float index not allowed)
get_element(None, 0)           → TypeError (None is not indexable)
get_element({}, 0)             → TypeError (dict requires specific index type, reject as unsupported)
get_element(42, 0)             → TypeError (int is not indexable)
```

### Rules
1. Accept: list, tuple, str, any object with `__getitem__` method
2. Index must be: int (positive or negative)
3. Reject: None, custom non-indexable objects, dict
4. Raise TypeError for invalid index types (str, float, etc.)
5. Raise IndexError for out-of-bounds access (normal Python behavior)

---

## Expected Test Coverage

### divide() tests
- ✅ Normal cases (int/int, float/int, int/float, float/float)
- ✅ Edge cases (zero numerator, negative numbers)
- ✅ Large numbers
- ✅ Type validation (reject non-numeric)
- ✅ ZeroDivisionError
- ✅ Exact vs non-exact division return type

### get_element() tests
- ✅ Normal cases (list, tuple, string)
- ✅ Index ranges (positive, negative)
- ✅ Type validation (only int indices)
- ✅ Type rejection (string index, float index)
- ✅ Invalid objects (None, dict)
- ✅ Out of bounds (IndexError)

---

## Implementation Guideline

Use this spec as the **single source of truth** for code fixes.
When a test fails, check spec first:
- If spec says "should return int" but code returns float → fix code
- If spec says "should raise TypeError" but code doesn't → fix code
- If spec is ambiguous → this is a problem, not the code's fault
