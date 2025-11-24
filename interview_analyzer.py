"""
Interview Feedback System using LiteLLM
Analyzes interview transcriptions and provides hiring recommendations
"""

import os
from typing import Dict, List, Optional
from dotenv import load_dotenv
from litellm import completion

# Load environment variables
load_dotenv()


class InterviewAnalyzer:
    """Analyzes interview transcriptions and generates feedback"""

    def __init__(self, model: str = "gpt-4o-mini"):
        """
        Initialize the analyzer with a specific model

        Args:
            model: LiteLLM model identifier (e.g., "gpt-4o-mini", "claude-3-5-sonnet-20241022")
        """
        self.model = model

    def analyze_interview(
        self,
        transcription: str,
        role: str = "Software Engineer",
        level: str = "Mid-level",
        focus_areas: Optional[List[str]] = None
    ) -> Dict[str, any]:
        """
        Analyze an interview transcription and generate feedback

        Args:
            transcription: Full interview transcription text
            role: Job role being interviewed for
            level: Experience level (Entry, Mid-level, Senior, Staff, etc.)
            focus_areas: Optional list of specific areas to evaluate

        Returns:
            Dictionary containing decision, checkpoints, and reasoning
        """

        # Build the prompt
        prompt = self._build_prompt(transcription, role, level, focus_areas)

        # Call LiteLLM
        response = completion(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert technical interviewer with years of experience evaluating candidates. Provide honest, constructive, and actionable feedback."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.3  # Lower temperature for more consistent evaluations
        )

        # Extract the response
        feedback_text = response.choices[0].message.content

        # Parse the structured response
        parsed_feedback = self._parse_feedback(feedback_text)

        return {
            "decision": parsed_feedback["decision"],
            "checkpoints": parsed_feedback["checkpoints"],
            "reasoning": parsed_feedback["reasoning"],
            "raw_feedback": feedback_text,
            "model_used": self.model
        }

    def _build_prompt(
        self,
        transcription: str,
        role: str,
        level: str,
        focus_areas: Optional[List[str]]
    ) -> str:
        """Build the analysis prompt"""

        focus_areas_text = ""
        if focus_areas:
            focus_areas_text = f"\nFocus particularly on these areas: {', '.join(focus_areas)}"

        prompt = f"""Analyze the following interview transcription for a {level} {role} position.

INTERVIEW TRANSCRIPTION:
{transcription}
{focus_areas_text}

Please provide a structured evaluation in the following format:

DECISION: [Strong Hire / Weak Hire / No Hire]

CHECKPOINTS:
- [Checkpoint 1]: [Pass/Fail/Partial] - [Brief explanation]
- [Checkpoint 2]: [Pass/Fail/Partial] - [Brief explanation]
- [Checkpoint 3]: [Pass/Fail/Partial] - [Brief explanation]
(Include 5-8 relevant checkpoints covering technical skills, communication, problem-solving, etc.)

REASONING:
[2-3 paragraphs explaining the decision, highlighting strengths and areas of concern]

KEY STRENGTHS:
- [Strength 1]
- [Strength 2]

AREAS OF CONCERN:
- [Concern 1]
- [Concern 2]

RECOMMENDATIONS:
[Suggestions for next steps or areas for the candidate to improve]
"""
        return prompt

    def _parse_feedback(self, feedback_text: str) -> Dict[str, any]:
        """Parse the structured feedback from LLM response"""

        lines = feedback_text.strip().split('\n')

        decision = "No Hire"
        checkpoints = []
        reasoning = ""

        current_section = None
        reasoning_lines = []

        for line in lines:
            line_upper = line.upper().strip()

            # Detect sections
            if line_upper.startswith("DECISION:"):
                decision_text = line.split(':', 1)[1].strip().upper()
                if "STRONG HIRE" in decision_text:
                    decision = "Strong Hire"
                elif "WEAK HIRE" in decision_text:
                    decision = "Weak Hire"
                else:
                    decision = "No Hire"
                current_section = "decision"

            elif line_upper.startswith("CHECKPOINTS:"):
                current_section = "checkpoints"

            elif line_upper.startswith("REASONING:"):
                current_section = "reasoning"

            elif line_upper.startswith("KEY STRENGTHS:") or \
                 line_upper.startswith("AREAS OF CONCERN:") or \
                 line_upper.startswith("RECOMMENDATIONS:"):
                current_section = "other"

            # Parse checkpoint lines
            elif current_section == "checkpoints" and line.strip().startswith('-'):
                checkpoints.append(line.strip()[1:].strip())

            # Collect reasoning lines
            elif current_section == "reasoning" and line.strip():
                reasoning_lines.append(line.strip())

        reasoning = ' '.join(reasoning_lines)

        return {
            "decision": decision,
            "checkpoints": checkpoints,
            "reasoning": reasoning
        }

    def format_output(self, result: Dict[str, any]) -> str:
        """Format the analysis result as readable text"""

        output = []
        output.append("=" * 60)
        output.append("INTERVIEW FEEDBACK REPORT")
        output.append("=" * 60)
        output.append(f"\nModel Used: {result['model_used']}")
        output.append(f"\n{'HIRING DECISION:':<20} {result['decision']}")
        output.append("\n" + "-" * 60)
        output.append("\nCHECKPOINTS:")
        output.append("-" * 60)

        for i, checkpoint in enumerate(result['checkpoints'], 1):
            output.append(f"{i}. {checkpoint}")

        output.append("\n" + "-" * 60)
        output.append("REASONING:")
        output.append("-" * 60)
        output.append(f"\n{result['reasoning']}")
        output.append("\n" + "=" * 60)

        return "\n".join(output)


def main():
    """Example usage"""

    # Sample transcription
    sample_transcription = """
Interviewer: Hi, thanks for joining us today. Let's start with a coding question.
Can you write a function to reverse a linked list?

Candidate: Sure! I'll write this in Python. So basically, we need to reverse the
pointers in the linked list. I'll use three pointers: previous, current, and next.

Interviewer: That sounds good. Go ahead.

Candidate: Here's my approach:
```python
def reverse_linked_list(head):
    prev = None
    current = head

    while current:
        next_node = current.next
        current.next = prev
        prev = current
        current = next_node

    return prev
```

The time complexity is O(n) and space complexity is O(1) since we're doing it in place.

Interviewer: Great! Can you explain what happens at each step?

Candidate: Yes, so we iterate through the list. At each node, we save the next node,
then point the current node backwards to the previous node, then move our pointers forward.
When we reach the end, prev will be pointing to the new head.

Interviewer: Excellent. Now, let's say I want you to design a URL shortener service.
How would you approach this?

Candidate: Hmm, okay. So we need to take long URLs and create short codes for them.
I guess we could use a hash function? Maybe MD5 and take the first few characters?

Interviewer: What are some potential issues with that approach?

Candidate: Well... hash collisions could be an issue. Two different URLs might generate
the same short code.

Interviewer: Right. How would you handle that?

Candidate: Maybe... we could check if the code already exists and if it does, try adding
a number to the end? Or use a different hashing algorithm?

Interviewer: Those could work. What about scale? How would you handle millions of URLs?

Candidate: Um, we'd probably need a database. Maybe use caching for popular URLs.
I'm not super experienced with distributed systems though.

Interviewer: That's okay. Do you have any questions for me?

Candidate: Yes! What does the team culture look like?
"""

    # Initialize analyzer
    analyzer = InterviewAnalyzer(model="gpt-4o-mini")

    # Analyze the interview
    print("Analyzing interview transcription...\n")
    result = analyzer.analyze_interview(
        transcription=sample_transcription,
        role="Software Engineer",
        level="Mid-level",
        focus_areas=["Data structures", "System design", "Communication"]
    )

    # Print formatted output
    print(analyzer.format_output(result))

    # Optionally print raw feedback
    print("\n\nRAW FEEDBACK FROM LLM:")
    print("-" * 60)
    print(result['raw_feedback'])


if __name__ == "__main__":
    main()
