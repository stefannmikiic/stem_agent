# STEM Agent: Approach & Results

## Summary

This project is a QA agent that improves over time by learning from failures. The main idea is to turn each test failure into something reusable instead of treating it as a one-off problem.

The most important part is the rule extraction layer. It reads failures, pulls out the useful lesson, and stores that lesson for the next run.

## Approach

I split the project into three practical pieces:

1. Generate tests from the current strategy.
2. Run the tests and collect the result.
3. Turn failures into rules and use those rules in the next iteration.

I also added a backend API and a small dashboard so I could see what the agent was doing during each run.

## What changed over time

The early version was mostly reactive. The agent would fail, patch something, and then often hit a similar issue again.

Once rule extraction and memory were added, the loop became more useful:
- failures were stored
- similar failures could be recognized later
- the test generator and code fixer could use the learned rules as hints

The biggest improvement came when the system had a clear spec to follow. That reduced conflicting test expectations and made the results easier to understand.

## What worked

- Rule extraction from failures worked well enough to be useful.
- Memory helped the agent avoid repeating the same mistakes.
- Retry and timeout handling kept the pipeline from getting stuck too easily.
- The dashboard made debugging much easier because I could see the latest state in one place.

## What was harder than expected

- LLM output was not always clean JSON, so parsing needed several fallback paths.
- Not every extracted rule was useful, so some filtering is still needed.
- The effect of learning was not immediate. Early runs looked similar, and the gains became easier to see only after several iterations.

## Before and after

Before the spec and rule layer, the loop could keep repeating the same kinds of errors.

After those pieces were added, the agent had a better chance of improving from one run to the next because the tests, the fixes, and the learned rules were all pointing in the same direction.

## What surprised me

The biggest surprise was that the spec mattered more than I expected. I originally thought the main challenge would be model quality, but the bigger issue was giving the system one clear definition of correctness.

I was also surprised by how often the surrounding code, not the model, caused the biggest issues. A small parsing bug or state bug could make the whole pipeline look unreliable.

## What failed

Strategy-only improvement did not work well on its own. Changing the wording of the strategy was not enough to create real progress.

Regex-based JSON parsing also failed too often, so I had to make the parsing more defensive.

Another early mistake was not being careful enough about live state vs. stored history in the UI. That made the dashboard misleading until I tied it more directly to the latest backend snapshot.

## What I would do next

If I had more time, I would:

- add a validation step for learned rules
- improve the score explanation in the dashboard
- batch repeated LLM calls so runs are faster
- add a clearer live/fallback indicator in the UI
- test the same approach on a second domain

## Conclusion

The project works best when the system has one clear spec, a way to remember failures, and a way to reuse that memory later. That is the main result: the agent is not just running tests, it is slowly learning from them.
