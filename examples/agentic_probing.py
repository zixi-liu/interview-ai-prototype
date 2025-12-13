"""
Example: Agentic Probing with Learned Stop Policy

This example demonstrates the AgenticInterviewer which uses a learned stop policy
(88% accuracy) to dynamically decide when to stop probing during BQ interviews.

Key features:
- Parses evaluation to extract gaps and probing questions
- Uses ML model trained on 30+ synthetic sessions
- Stops based on: good_responses, gaps_remaining, friction_ratio, etc.
- Single LLM call per turn (classify + decide + generate)
"""

import os
import sys
import asyncio

_project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from interview_analyzer import InterviewAnalyzer, AgenticInterviewer
from prompts import BQQuestions
from utils import Colors

# Add missing color codes
Colors.CYAN = '\033[96m'
Colors.DIM = '\033[2m'


# Sample BQ question and answer
QUESTION = "Tell me about a time you had to influence others without authority."

ANSWER = """
At my previous company, I noticed our deployment process was causing frequent outages.
I wasn't in a leadership position, but I felt strongly we needed to change.
I talked to several team members and eventually we improved the process.
The result was fewer outages and happier customers.
"""

LEVEL = "Senior"

# Simulated user responses to probing questions
SIMULATED_RESPONSES = [
    # Response 1: Still vague
    """I gathered some data about the outages and shared it with the team.
    People were receptive to my ideas.""",

    # Response 2: Getting better - shows some ownership
    """I created a spreadsheet tracking all outages over 3 months, showing we had
    12 incidents costing roughly $50K in engineer time. I presented this to the
    team lead and suggested we pilot a canary deployment approach.""",

    # Response 3: Good - specific metrics and outcome
    """After implementing canary deployments, our incident rate dropped from 12 to 2
    per quarter. I personally championed the change by writing documentation,
    running training sessions, and being the go-to person for questions.
    The CTO mentioned this in our all-hands as a model for bottom-up innovation.""",
]


async def demo_agentic_probing():
    """Demonstrate the agentic probing flow with learned stop policy."""

    analyzer = InterviewAnalyzer()

    print("=" * 70)
    print("AGENTIC PROBING DEMO - With Learned Stop Policy")
    print("=" * 70)

    print(f"\n{Colors.BOLD}Question:{Colors.RESET}")
    print(QUESTION)

    print(f"\n{Colors.BOLD}Initial Answer:{Colors.RESET}")
    print(ANSWER)

    print(f"\n{Colors.BOLD}Level:{Colors.RESET} {LEVEL}")

    # Step 1: Get initial evaluation
    print("\n" + "-" * 70)
    print("Step 1: Getting initial evaluation...")
    print("-" * 70 + "\n")

    prompt = BQQuestions.real_interview(QUESTION, ANSWER, LEVEL)
    result = await analyzer.customized_analyze(prompt, stream=True)
    evaluation = await Colors.stream_and_print(result)

    # Step 2: Initialize AgenticInterviewer
    print("\n" + "-" * 70)
    print("Step 2: Initializing AgenticInterviewer with learned stop policy...")
    print("-" * 70)

    interviewer = AgenticInterviewer(model="gpt-4o-mini", max_turns=8)
    init_result = interviewer.initialize(
        question=QUESTION,
        answer=ANSWER,
        evaluation=evaluation,
        level=LEVEL
    )

    print(f"\nWeak competencies identified: {init_result['weak_competencies']}")
    print(f"Areas for improvement: {init_result['areas_for_improvement']}")
    print(f"Probing questions generated: {len(init_result['probing_questions'])}")
    print(f"First probe: {init_result['first_probe'][:100]}...")

    if init_result["action"] == "STOP":
        print(f"\n{Colors.GREEN}No probing needed - answer is complete!{Colors.RESET}")
        return

    # Step 3: Probing loop with learned stop policy
    print("\n" + "-" * 70)
    print("Step 3: Probing loop (with learned stop policy)")
    print("-" * 70)

    response_idx = 0

    while interviewer.should_continue():
        probe = interviewer.get_current_probe()
        if not probe:
            break

        print(f"\n{Colors.BOLD}Turn {interviewer.turn_count + 1}:{Colors.RESET}")
        print(f"{Colors.CYAN}Interviewer:{Colors.RESET} {probe}")

        # Get simulated response (in real use, this would be user input)
        if response_idx < len(SIMULATED_RESPONSES):
            user_response = SIMULATED_RESPONSES[response_idx]
            response_idx += 1
        else:
            user_response = "I don't have more details to add."

        print(f"\n{Colors.YELLOW}Candidate:{Colors.RESET} {user_response}")

        # Process response with stop policy
        decision = await interviewer.step(user_response)

        print(f"\n{Colors.DIM}--- Decision ---{Colors.RESET}")
        # Response type is in classification sub-dict
        classification = decision.get('classification', {})
        response_type = classification.get('response_type', decision.get('response_type', 'N/A'))
        print(f"  Response type: {response_type}")
        print(f"  Action: {decision.get('action', 'N/A')}")
        print(f"  Reasoning: {decision.get('reasoning', 'N/A')}")

        if decision.get("action") == "STOP":
            print(f"\n{Colors.GREEN}Stop policy triggered!{Colors.RESET}")
            print(f"Message: {decision.get('agent_message', '')}")
            break

    # Step 4: Summary
    print("\n" + "-" * 70)
    print("Step 4: Session Summary")
    print("-" * 70)

    summary = interviewer.get_summary()
    print(f"\nTotal turns: {summary['turns']}")
    print(f"Stop reason: {summary['stop_reason']}")

    print(f"\n{Colors.BOLD}Q&A Pairs collected:{Colors.RESET}")
    for i, (q, a) in enumerate(summary['qa_pairs'], 1):
        print(f"\n  Q{i}: {q[:80]}...")
        print(f"  A{i}: {a[:80]}...")

    # Show decision log
    print(f"\n{Colors.BOLD}Decision Log:{Colors.RESET}")
    for i, d in enumerate(interviewer.get_decision_log(), 1):
        rt = d.get('classification', {}).get('response_type', d.get('response_type', 'N/A'))
        action = d.get('action', 'N/A')
        print(f"  Turn {i}: {rt} -> {action}")


async def demo_stop_policy_features():
    """Show how the stop policy uses features to make decisions."""

    print("\n" + "=" * 70)
    print("STOP POLICY FEATURE ANALYSIS")
    print("=" * 70)

    from policy.stop_policy import StateFeatures, HybridStopPolicy

    policy = HybridStopPolicy()

    # Scenario 1: Early in conversation, many gaps
    state1 = StateFeatures(
        gaps_remaining=3,
        gaps_resolved=0,
        turn_count=1,
        good_responses=0,
        vague_responses=1,
        friction_ratio=0.0,
        level="Senior"
    )
    decision1, reasoning1, policy_used1 = policy.should_stop(state1)
    print(f"\nScenario 1: Turn 1, no good responses, 3 gaps remaining")
    print(f"  Decision: {decision1.value} ({policy_used1})")
    print(f"  Reasoning: {reasoning1}")

    # Scenario 2: Good progress, some gaps resolved
    state2 = StateFeatures(
        gaps_remaining=1,
        gaps_resolved=2,
        turn_count=3,
        good_responses=2,
        vague_responses=1,
        friction_ratio=0.1,
        level="Senior"
    )
    decision2, reasoning2, policy_used2 = policy.should_stop(state2)
    print(f"\nScenario 2: Turn 3, 2 good responses, 1 gap remaining")
    print(f"  Decision: {decision2.value} ({policy_used2})")
    print(f"  Reasoning: {reasoning2}")

    # Scenario 3: High friction
    state3 = StateFeatures(
        gaps_remaining=2,
        gaps_resolved=0,
        turn_count=2,
        good_responses=0,
        vague_responses=0,
        idk_count=2,
        friction_ratio=0.5,
        level="Senior"
    )
    decision3, reasoning3, policy_used3 = policy.should_stop(state3)
    print(f"\nScenario 3: Turn 2, 2 IDK responses, high friction")
    print(f"  Decision: {decision3.value} ({policy_used3})")
    print(f"  Reasoning: {reasoning3}")


async def main():
    print("\n" + "=" * 70)
    print("AGENTIC INTERVIEWER EXAMPLES")
    print("Uses learned stop policy with 88% accuracy")
    print("=" * 70 + "\n")

    # Run main demo
    await demo_agentic_probing()

    # Show policy feature analysis
    await demo_stop_policy_features()

    print("\n" + "=" * 70)
    print("DONE")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
