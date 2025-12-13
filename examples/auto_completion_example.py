"""
Example usage of auto-completion feature
Demonstrates how to use AutoCompletionEngine for self-intro and BQ answer completion
"""

import json
import os
import sys
import asyncio

_project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from advance.auto_completion import AutoCompletionEngine


async def example_self_intro():
    """Example: Auto-complete self-introduction"""
    print("=" * 60)
    print("Example 1: Self-Introduction Auto-Completion")
    print("=" * 60)
    
    engine = AutoCompletionEngine()
    
    # Partial self-introduction text
    partial_text = """Hi, I'm John, and I'm a software engineer with 5 years of experience. 
    I've worked on several projects involving distributed systems and microservices."""
    partial_text = "I'm a "
    
    print(f"\nPartial Input:\n{partial_text}\n")
    print("Getting completion suggestions...\n")
    
    result = await engine.complete_self_intro(
        partial_text=partial_text,
        role="Senior Software Engineer",
        company="Google"
    )
    
    print("Result:")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    if result.get("is_complete"):
        print(f"\n✅ {result['message']}")
    else:
        print("\n📝 Completion Suggestions:")
        completions = result.get("completions", [])
        
        # Concurrently check fluency for all completions
        fluency_results = await asyncio.gather(*[
            engine.check_fluency(partial_text, comp['text'])
            for comp in completions
        ])
        
        # Print results
        for i, (comp, fluency_result) in enumerate(zip(completions, fluency_results), 1):
            print(f"\n{i}. {comp['text']}")
            # print(f"   Reason: {comp['reason']}")
            print(f"   Fluency: {fluency_result['is_fluent']}")
            print(f"   Fluency Reason: {fluency_result['reason']}")
            print(f"   Fluency Confidence: {fluency_result['confidence']}")


async def example_bq_answer():
    """Example: Auto-complete BQ answer"""
    print("\n" + "=" * 60)
    print("Example 2: BQ Answer Auto-Completion")
    print("=" * 60)
    
    engine = AutoCompletionEngine()
    
    question = "Tell me about your most challenging project."
    partial_text = """I was leading a team to migrate our monolithic application 
    to a microservices architecture. The challenge was that we had to do this migration 
    while maintaining 99.9% uptime and without disrupting our users.
    
    My task was to design and execute a zero-downtime migration strategy."""
    
    print(f"\nQuestion: {question}\n")
    print(f"Partial Answer:\n{partial_text}\n")
    print("Getting completion suggestions...\n")
    
    result = await engine.complete_bq_answer(
        partial_text=partial_text,
        question=question,
        role="Senior Software Engineer",
        level="Senior"
    )
    
    print("Result:")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    if result.get("is_complete"):
        print(f"\n✅ {result['message']}")
    else:
        print("\n📝 Completion Suggestions:")
        for i, comp in enumerate(result.get("completions", []), 1):
            print(f"\n{i}. {comp['text']}")
            print(f"   Reason: {comp['reason']}")


async def example_complete_answer():
    """Example: Testing with a complete answer (should return is_complete=True)"""
    print("\n" + "=" * 60)
    print("Example 3: Complete Self-Introduction (Should be marked complete)")
    print("=" * 60)
    
    engine = AutoCompletionEngine()
    
    # A more complete self-introduction
    complete_text = """Hi, I'm John, and I'm a software engineer with 5 years of experience 
    building scalable distributed systems. I've worked at several tech companies where I led 
    projects that improved system performance by 40% and reduced costs by 30%. 
    I'm particularly excited about this role at Google because it aligns with my passion 
    for building large-scale systems that impact millions of users. I'm looking forward to 
    contributing to your team and learning from the talented engineers here."""
    
    print(f"\nInput:\n{complete_text}\n")
    print("Checking if complete...\n")
    
    result = await engine.complete_self_intro(
        partial_text=complete_text,
        role="Senior Software Engineer",
        company="Google"
    )
    
    print("Result:")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    if result.get("is_complete"):
        print(f"\n✅ {result['message']}")
    else:
        print("\n📝 Completion Suggestions:")
        for i, comp in enumerate(result.get("completions", []), 1):
            print(f"\n{i}. {comp['text']}")
            print(f"   Reason: {comp['reason']}")


async def main():
    """Run all examples"""
    await example_self_intro()
    # await example_bq_answer()
    # await example_complete_answer()


if __name__ == "__main__":
    asyncio.run(main())

