# Solution Explanation

## What was going wrong

The score was stuck at 0 because the tests were fighting each other. There was no clear rule for what `divide()` and `get_element()` should do, so one test would expect one result and another test would expect the opposite.

For example:
- one test expected `divide(10, 2)` to return `5`
- another test expected the same call to return `5.0`

That meant the code could never satisfy everything at once. The agent kept fixing one case and breaking another.

## What fixed it

I added a clear specification file, `FUNCTION_SPEC.md`, that says exactly what each function should do. That gave the test generator and the code fixer one shared source of truth.

I also updated the sample code so it follows that spec directly. After that, the agent no longer had to guess whether the result should be an `int`, `float`, or an error.

## Why this mattered

Once the spec existed, the whole loop became much more stable:
- tests were generated around the same rules
- fixes were based on the same rules
- rule learning started to produce useful guidance instead of noise

## Result

Before the spec, the agent kept looping with failed tests and a score of 0.

After the spec, the run became much more consistent and the score started to move upward instead of staying stuck.

## Main lesson

The system could not learn until it had a clear definition of success. The issue was not just the model or the code. The bigger problem was that the parts of the system were not agreeing on what “correct” meant.

## How to use it

Run the pipeline with:

```bash
python main.py
```

The agent will:
1. Read the spec
2. Generate tests
3. Run the tests
4. Learn from failures
5. Update the code if needed
6. Repeat for the next iteration

## Files changed

- `FUNCTION_SPEC.md` - the source of truth for function behavior
- `test_generator.py` - now reads the spec
- `code_fixer.py` - now uses the spec when proposing fixes
- `tasks/sample_code.py` - updated to match the spec

## Bottom line

The system was not broken in a deep way. It was missing agreement. Once I added a clear spec, the agent had a consistent target and the whole pipeline started behaving much better.
