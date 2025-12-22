import os
import sys
import asyncio

_project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from interview_analyzer import InterviewAnalyzer
from prompts import BQQuestions
from utils import Colors, FeedbackRecorder

QUESTION = "Name a project/accomplishment you’re most proud of."
YOUR_ANSWER = """In my previous role, I was part of a team responsible for developing
 a real-time data processing pipeline for a large-scale analytics platform.  
 The platform was intended to provide insights to clients by processing massive 
 amounts of data in real-time, such as user activity logs and sensor data. This was 
 a critical project because it would directly affect the accuracy and speed of the insights 
 provided to clients, which in turn impacted their business decisions.

 The existing monolithic architecture was unable to handle increasing data loads efficiently, 
 leading to slower processing times and higher latency.

 I led the transition to a microservices-based architecture, using Kafka for real-time data 
 streaming and integrating scalable storage solutions like AWS S3 and DynamoDB. I also introduced 
 automated testing and CI/CD pipelines to streamline deployments.

 The new architecture reduced data processing latency by 50% and allowed the platform to handle 3x the data volume, 
 improving overall performance and enabling faster, data-driven decision-making for clients.

 This project deepened my understanding of scalable system design and further convinced me that building engineering 
 solutions aligned with business goals is better if you want to achieve long-term impact.
    """


async def solve_conflict():
    analyzer = InterviewAnalyzer(model="gpt-4o")
    question = QUESTION
    print("=" * 80)
    print(f"Question: {question}")
    answer = YOUR_ANSWER

    print("=" * 80)
    print("Answer:")
    print(answer)

    prompt = BQQuestions.real_interview(question, answer, "Junior-Mid") + BQQuestions.bar_raiser()
    result = await analyzer.customized_analyze(prompt, stream=True)
    feedback = await Colors.stream_and_print(result)

    red_flag_prompt = BQQuestions.red_flag(question, answer, "Junior-Mid") + BQQuestions.bar_raiser()
    red_flag_result = await analyzer.customized_analyze(red_flag_prompt, stream=True)
    red_flag_feedback = await Colors.stream_and_print(red_flag_result)

    feedback_recorder = FeedbackRecorder()
    await feedback_recorder.save_feedback(question, answer, feedback, red_flag_feedback)

async def main():
    await solve_conflict()

if __name__ == "__main__":
    asyncio.run(main())