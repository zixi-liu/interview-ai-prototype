"""
Example usage for BQ Interview Analyzer
"""

import asyncio
import re
import sys
from interview_analyzer import InterviewAnalyzer


# ANSI color codes
class Colors:
    GREEN = '\033[92m'
    LIGHT_GREEN = '\033[92m'
    RED = '\033[91m'
    LIGHT_RED = '\033[91m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


def print_colored_feedback(feedback: str, end: str = '\n'):
    """
    Print feedback with Pass in green and No-Pass in red
    
    Args:
        feedback: The feedback text to print
        end: String appended after the last value (default: newline)
    """
    # Enable ANSI color support on Windows
    if sys.platform == 'win32':
        import ctypes
        kernel32 = ctypes.windll.kernel32
        kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
    
    # Replace Pass, Hire, Strong Hire with green Pass (case insensitive)
    colored_feedback = re.sub(
        r'\b(Pass|Hire|Strong Hire)\b',
        f'{Colors.GREEN}{Colors.BOLD}\\1{Colors.RESET}',
        feedback,
        flags=re.IGNORECASE
    )
    
    # Replace No-Pass, No hire with red No-Pass (case insensitive)
    colored_feedback = re.sub(
        r'\b(No-Pass|No hire)\b',
        f'{Colors.RED}{Colors.BOLD}\\1{Colors.RESET}',
        colored_feedback,
        flags=re.IGNORECASE
    )
    
    print(colored_feedback, end=end)


async def example_1_introduction():
    """Example 1: Self-introduction analysis"""
    print("=" * 80)
    print("EXAMPLE 1: Self-Introduction Analysis")
    print("=" * 80)
    print()
    
    analyzer = InterviewAnalyzer()
    
    introduction = """
    Hi, I'm Sarah. I'm a software engineer with 7 years of experience, 
    primarily focused on backend systems and distributed architecture. 
    I started my career at a fintech startup where I built payment processing 
    systems handling millions of transactions daily. I then moved to a larger 
    tech company where I led a team of 5 engineers to redesign our microservices 
    architecture, which improved system reliability by 40% and reduced latency by 30%.
    
    I'm particularly passionate about building scalable systems and have deep 
    experience with cloud infrastructure, particularly AWS. I've also contributed 
    to several open-source projects in the distributed systems space.
    
    I'm excited about this opportunity at your company because I want to work 
    on problems at an even larger scale and learn from some of the best engineers 
    in the industry. I believe my experience in building resilient systems would 
    be a great fit for your team.
    """
    
    async for chunk in analyzer.analyze_introduction_stream(
        introduction=introduction,
        role="Senior Software Engineer",
        company="Google"
    ):
        print_colored_feedback(chunk, end='')
    print()  # 在streaming结束后添加换行


async def example_2_bq_question():
    """Example 2: BQ question analysis"""
    print("=" * 80)
    print("EXAMPLE 2: BQ Question Analysis")
    print("=" * 80)
    print()
    
    analyzer = InterviewAnalyzer()
    
    question = "Tell me about your most challenging project."
    
    answer = """
    Sure. The most challenging project I worked on was when I had to lead 
    the migration of our entire payment processing system from a monolithic 
    architecture to a microservices architecture. This was at my previous 
    company, and it was critical because we were experiencing scaling issues 
    and the system was becoming a bottleneck.
    
    The situation was that we were processing about 10 million transactions 
    per day, and our monolithic system was struggling. We were seeing increased 
    latency and occasional outages during peak hours. The business needed us 
    to migrate without any downtime and without impacting the user experience.
    
    My task was to design and execute the migration strategy. I was the tech 
    lead for this project, so I was responsible for the overall architecture 
    design, coordinating with multiple teams, and ensuring we met our deadlines.
    
    For the action part, I first spent a month doing a deep analysis of the 
    existing system to identify all the dependencies and potential breaking points. 
    I then designed a phased migration approach where we would migrate one 
    service at a time using a strangler fig pattern. I worked closely with 
    the infrastructure team to set up the new microservices infrastructure on AWS, 
    and I implemented comprehensive monitoring and rollback mechanisms.
    
    We also did extensive load testing to ensure each service could handle the 
    traffic. I coordinated with the product team to schedule the migrations 
    during low-traffic periods, and we did blue-green deployments for each service.
    
    The result was that we successfully migrated all 15 services over 6 months 
    with zero downtime. The new system reduced our average latency from 200ms 
    to 50ms, and we improved our system reliability from 99.5% to 99.95%. 
    We also reduced infrastructure costs by 20% because we could scale services 
    independently. The project was considered a huge success, and I received 
    recognition from the CTO.
    """
    
    async for chunk in analyzer.analyze_bq_question_stream(question, answer, role="Senior Software Engineer"):
        print_colored_feedback(chunk, end='')
    print()  # 在streaming结束后添加换行


async def main():
    """Run both examples"""
    await example_1_introduction()
    print("\n\n")
    await example_2_bq_question()


if __name__ == "__main__":
    asyncio.run(main())
