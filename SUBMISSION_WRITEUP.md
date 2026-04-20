# STEM Agent: Write-up

**Project**: Self-Evolving QA Agent  
**Date**: April 2026

## Approach

I built the project as a feedback loop instead of a fixed QA script. The agent makes a plan, generates tests, runs them, looks at the failures, and uses those failures to improve the next round. The main idea was simple: if the system can turn mistakes into useful rules, it should improve over time.

The pipeline has four main steps. It creates a strategy, turns that strategy into pytest tests, runs the tests, and then stores useful rules from the failures. If needed, it can also try to fix the sample code and run again.

I also added a React dashboard and a small FastAPI backend. That made the project much easier to follow because I could see the strategy, stage status, memory, rules, and latest run in one place.

## Experiments

I approached the project as a set of small experiments.

The first experiment was the loop itself. I wanted to see if the agent could generate tests, run them, and feed the result back into the next iteration. That worked, but only after I made the pipeline more resilient and improved how it handled LLM output.

The second experiment was rule extraction. I wanted to know if a failure could be turned into something reusable instead of being kept only as raw history. That worked better than I expected. The system could often turn failures into useful categories like type checking, input validation, or error handling.

The third experiment was using a clear specification. Once the tests and fixes were pointed at the same spec, the system became much more stable. Without that, it could generate conflicting tests or chase the wrong signals.

I also tested the frontend-backend connection separately. That helped me catch a different kind of problem: not whether the AI loop worked, but whether the app actually saved and showed the right live state after a run.

## What Surprised Me

The biggest surprise was that the spec mattered more than I expected. I thought the hard part would be making the model smarter. In practice, the bigger issue was making sure all parts of the system agreed on what success meant.

I was also surprised that many failures came from the plumbing around the model, not the model itself. A small parsing or state bug could make the whole system look broken even when the basic idea was fine.

Another surprise was that the learned rules were fairly readable. Instead of a black box, the system could store rules like “validate input types before indexing” or “handle error branches explicitly.” That made the behavior easier to explain.

## What Failed

Strategy-only improvement did not work well. Changing the wording of the strategy did not lead to meaningful progress by itself. The system needed actual rule extraction and feedback, not just nicer text.

Parsing was another weak spot. LLM output is not always clean JSON, so a single parsing method was not enough. I had to add more defensive parsing and fallback logic.

I also had to fix a bug where the dashboard health value was based on memory history instead of the latest run. That made the UI look stuck even when the backend had finished correctly.

The fixing stage was another small UX issue. I originally treated it as pending unless a fix was applied. That was technically true, but it made successful runs look incomplete. I would now treat that more carefully in the UI.

## What I Would Do With More Time

With more time, I would add a simple validation step for learned rules. Right now the system can extract rules, but it does not always check whether they actually help in the next run.

I would also improve the metrics. The current score is useful, but I would like a clearer explanation of why a run improved or got worse.

On the engineering side, I would add caching and batching for repeated LLM calls so the system runs faster and costs less.

For the dashboard, I would make the live vs. fallback state more obvious and add a timeline of runs so the system is easier to inspect.

Finally, I would try the same approach on another domain. That would show whether the method is general or only works well for this QA task.

## Conclusion

This project showed me that a self-evolving agent is possible, but only if the whole loop is designed carefully. The model matters, but state, feedback, and clear rules matter just as much. The biggest lesson was that the system improves when it has a clear spec, reliable persistence, and a way to learn from mistakes.
