"""
Example usage of the Interview Feedback System
Demonstrates different ways to use the analyzer
"""

from interview_analyzer import InterviewAnalyzer


def example_1_basic_usage():
    """Basic usage with default settings"""
    print("\n" + "="*60)
    print("EXAMPLE 1: Basic Usage")
    print("="*60)

    transcription = """
Interviewer: Can you explain what a REST API is?

Candidate: A REST API is an application programming interface that follows REST
architectural principles. It uses HTTP methods like GET, POST, PUT, and DELETE
to perform operations on resources.

Interviewer: Good. Can you design a simple API for a blog system?

Candidate: Sure. We'd have endpoints like:
- GET /posts - list all posts
- GET /posts/:id - get a specific post
- POST /posts - create a new post
- PUT /posts/:id - update a post
- DELETE /posts/:id - delete a post

We'd also need user authentication and probably endpoints for comments.

Interviewer: What about pagination?

Candidate: Oh right! We should add query parameters like ?page=1&limit=10 to
the GET /posts endpoint.
"""

    analyzer = InterviewAnalyzer(model="gpt-4o-mini")
    result = analyzer.analyze_interview(
        transcription=transcription,
        role="Backend Engineer",
        level="Junior"
    )

    print(analyzer.format_output(result))


def example_2_custom_focus_areas():
    """Using custom focus areas"""
    print("\n" + "="*60)
    print("EXAMPLE 2: Custom Focus Areas")
    print("="*60)

    transcription = """
Interviewer: Tell me about a time you had to resolve a conflict with a team member.

Candidate: In my previous role, I had a disagreement with another developer about
code architecture. They wanted to use microservices but I thought it was overkill
for our use case. Instead of arguing, I proposed we both present our approaches in
a team meeting with pros and cons. We ended up choosing a modular monolith which
was a good compromise.

Interviewer: How did you handle the technical side of that decision?

Candidate: I created a proof of concept showing how we could structure the monolith
to make it easy to extract services later if needed. I also documented the decision
and reasoning so future team members would understand why we chose that approach.

Interviewer: What would you say is your greatest weakness?

Candidate: I sometimes struggle with time estimation. I've been working on breaking
down tasks into smaller chunks and tracking my actual time to improve this skill.
"""

    analyzer = InterviewAnalyzer(model="gpt-4o-mini")
    result = analyzer.analyze_interview(
        transcription=transcription,
        role="Senior Engineer",
        level="Senior",
        focus_areas=["Leadership", "Communication", "Conflict resolution", "Technical judgment"]
    )

    print(analyzer.format_output(result))


def example_3_different_model():
    """Using a different LLM model (Claude)"""
    print("\n" + "="*60)
    print("EXAMPLE 3: Using Claude Model")
    print("="*60)

    transcription = """
Interviewer: Explain the difference between SQL and NoSQL databases.

Candidate: Um, SQL is like... structured? And NoSQL is not structured?

Interviewer: Can you be more specific?

Candidate: SQL uses tables and NoSQL doesn't?

Interviewer: What about use cases? When would you choose one over the other?

Candidate: I'm not really sure. Maybe SQL for big data?
"""

    # Note: This will only work if you have ANTHROPIC_API_KEY set
    analyzer = InterviewAnalyzer(model="claude-3-5-sonnet-20241022")

    try:
        result = analyzer.analyze_interview(
            transcription=transcription,
            role="Data Engineer",
            level="Entry"
        )
        print(analyzer.format_output(result))
    except Exception as e:
        print(f"Error using Claude (make sure ANTHROPIC_API_KEY is set): {e}")
        print("\nFalling back to GPT-4...")
        analyzer = InterviewAnalyzer(model="gpt-4o-mini")
        result = analyzer.analyze_interview(
            transcription=transcription,
            role="Data Engineer",
            level="Entry"
        )
        print(analyzer.format_output(result))


def example_4_file_input():
    """Reading transcription from a file"""
    print("\n" + "="*60)
    print("EXAMPLE 4: Reading from File")
    print("="*60)

    # First, create a sample transcription file
    sample_file = "sample_interview.txt"

    with open(sample_file, 'w') as f:
        f.write("""
Interviewer: How would you optimize a slow database query?

Candidate: First, I'd look at the EXPLAIN plan to see what's happening. Then I'd
check for missing indexes. If there are table scans on large tables, adding indexes
on the WHERE clause columns usually helps. I'd also look for N+1 queries and consider
using joins or batch loading instead.

Interviewer: Good. What if indexes don't solve the problem?

Candidate: Then I'd look at query structure - maybe rewrite it, add caching for
frequently accessed data, or consider partitioning if the table is huge. In some
cases, denormalization might be needed, though that comes with tradeoffs.

Interviewer: Have you worked with query caching before?

Candidate: Yes, I've used Redis for caching query results. We set appropriate TTLs
based on how often the data changes and implemented cache invalidation on updates.
""")

    # Read and analyze
    with open(sample_file, 'r') as f:
        transcription = f.read()

    analyzer = InterviewAnalyzer(model="gpt-4o-mini")
    result = analyzer.analyze_interview(
        transcription=transcription,
        role="Database Engineer",
        level="Mid-level",
        focus_areas=["Database optimization", "Technical depth"]
    )

    print(analyzer.format_output(result))
    print(f"\nTranscription was read from: {sample_file}")


if __name__ == "__main__":
    # Run all examples
    example_1_basic_usage()

    print("\n\n" + "#"*60)
    input("Press Enter to continue to Example 2...")
    example_2_custom_focus_areas()

    print("\n\n" + "#"*60)
    input("Press Enter to continue to Example 3...")
    example_3_different_model()

    print("\n\n" + "#"*60)
    input("Press Enter to continue to Example 4...")
    example_4_file_input()

    print("\n\nAll examples completed!")
