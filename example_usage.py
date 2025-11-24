"""
Simple example usage
"""

from interview_analyzer import InterviewAnalyzer


def main():
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

Interviewer: What about pagination?

Candidate: Oh right! We should add query parameters like ?page=1&limit=10.
"""

    analyzer = InterviewAnalyzer()
    feedback = analyzer.analyze(transcription, role="Backend Engineer")
    print(feedback)


if __name__ == "__main__":
    main()
