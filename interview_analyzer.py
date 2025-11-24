"""
Simple Interview Analyzer using LiteLLM
Analyzes interview transcriptions and provides feedback
"""

from dotenv import load_dotenv
from litellm import completion

load_dotenv()


class InterviewAnalyzer:
    """Simple interview analyzer"""

    def __init__(self, model: str = "gpt-4o-mini"):
        self.model = model

    def analyze(self, transcription: str, role: str = "Software Engineer") -> str:
        """
        Analyze interview transcription and return feedback
        
        Args:
            transcription: Interview transcription text
            role: Job role being interviewed for
            
        Returns:
            Feedback text from LLM
        """
        prompt = f"""Analyze the following interview transcription for a {role} position and provide feedback including:
- Hiring decision (Strong Hire / Weak Hire / No Hire)
- Key strengths
- Areas of concern
- Overall assessment

INTERVIEW TRANSCRIPTION:
{transcription}
"""

        response = completion(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert technical interviewer. Provide honest and constructive feedback."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.3
        )

        return response.choices[0].message.content


def main():
    """Example usage"""
    transcription = """
Interviewer: Can you write a function to reverse a linked list?

Candidate: Sure! I'll use three pointers: previous, current, and next.
Here's my approach:
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
The time complexity is O(n) and space complexity is O(1).

Interviewer: Great! How would you design a URL shortener service?

Candidate: We could use a hash function like MD5 and take the first few characters.
We'd need a database to store the mappings and handle collisions.
"""

    analyzer = InterviewAnalyzer()
    feedback = analyzer.analyze(transcription, role="Software Engineer")
    print(feedback)


if __name__ == "__main__":
    main()
