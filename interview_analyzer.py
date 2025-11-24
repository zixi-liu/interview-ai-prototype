"""
BQ Interview Analyzer using LiteLLM
Analyzes behavioral questions and self-introductions for FAANG interviews
"""

from dotenv import load_dotenv
from litellm import completion
from prompts import (
    SYSTEM_MESSAGE_INTRODUCTION,
    SYSTEM_MESSAGE_BQ_QUESTION,
    get_introduction_prompt,
    BQQuestions,
)

load_dotenv()


class InterviewAnalyzer:
    """BQ Interview Analyzer for FAANG standards"""

    def __init__(self, model: str = "gpt-4o-mini"):
        self.model = model

    def analyze_introduction(self, introduction: str, role: str = "Software Engineer", yoe: int = None) -> str:
        """
        Analyze self-introduction (1-2 minutes) and provide FAANG-standard feedback
        
        Args:
            introduction: Self-introduction text (1-2 minutes worth)
            role: Job role being interviewed for
            yoe: Years of experience (optional, will be inferred if not provided)
            
        Returns:
            Structured feedback with overall rating, checkpoints, and improvement suggestions
        """
        prompt = get_introduction_prompt(introduction, role, yoe)

        response = completion(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_MESSAGE_INTRODUCTION
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.3
        )

        return response.choices[0].message.content

    def analyze_bq_question(self, question: str, answer: str, role: str = "Software Engineer") -> str:
        """
        Analyze a specific BQ question answer following FAANG standards
        
        Args:
            question: The BQ question asked (e.g., "Tell me about your most challenging project")
            answer: The candidate's answer
            role: Job role being interviewed for
            
        Returns:
            Structured feedback with result, checkpoints, and improvement suggestions
        """
        bq_questions = BQQuestions()
        prompt = bq_questions.get_prompt(question, answer, role)

        response = completion(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_MESSAGE_BQ_QUESTION
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
    analyzer = InterviewAnalyzer()
    
    # Example 1: Self-introduction analysis
    print("=" * 80)
    print("EXAMPLE 1: Self-Introduction Analysis")
    print("=" * 80)
    
    introduction = """
    Hi, I'm John. I've been a software engineer for about 5 years now. 
    I started my career at a startup where I worked on web applications, 
    then moved to a mid-size company where I focused on backend systems. 
    I'm really interested in distributed systems and have worked with 
    microservices architecture. I'm excited about this opportunity because 
    I want to work on systems at scale.
    """
    
    feedback = analyzer.analyze_introduction(introduction, role="Software Engineer", yoe=5)
    print(feedback)
    
    print("\n" + "=" * 80)
    print("EXAMPLE 2: BQ Question Analysis")
    print("=" * 80)
    
    # Example 2: BQ question analysis
    question = "Tell me about your most challenging project."
    answer = """
    So, I was working on this project where we had to migrate our 
    database. It was challenging because we had a lot of data and 
    couldn't have downtime. I worked with the team to plan it out, 
    and we did it over a weekend. It went pretty well.
    """
    
    feedback = analyzer.analyze_bq_question(question, answer, role="Software Engineer")
    print(feedback)


if __name__ == "__main__":
    main()
