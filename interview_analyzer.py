"""
BQ Interview Analyzer using LiteLLM
Analyzes behavioral questions and self-introductions for FAANG interviews
"""

import base64
from dotenv import load_dotenv
from litellm import acompletion
from prompts import (
    SystemMessage,
    get_introduction_prompt,
    BQQuestions,
)

load_dotenv()

# Audio-related constants
AUDIO_MODEL = "gpt-4o-audio-preview"
AUDIO_MODEL_MINI = "gpt-4o-mini-audio-preview"
AUDIO_TARGET_FORMAT = "wav"
AUDIO_PLACEHOLDER = "[Audio input - analyzing spoken content]"
TRANSCRIPTION_PROMPT = "Please transcribe the following audio exactly as spoken:"


class InterviewAnalyzer:
    """BQ Interview Analyzer for FAANG standards"""

    def __init__(self, model: str = "gpt-4o-mini", audio_model: str = AUDIO_MODEL_MINI):
        self.model = model
        self.audio_model = audio_model

    async def analyze_introduction(self, introduction: str, role: str, company: str) -> str:
        """
        Analyze self-introduction (1-2 minutes) and provide FAANG-standard feedback

        Args:
            introduction: Self-introduction text (1-2 minutes worth)
            role: Job role being interviewed for
            company: Target company name

        Returns:
            Structured feedback with overall rating, checkpoints, and improvement suggestions
        """
        prompt = get_introduction_prompt(introduction, role, company)

        response = await acompletion(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": SystemMessage.INTRODUCTION
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.3
        )

        return response.choices[0].message.content

    async def analyze_introduction_stream(self, introduction: str, role: str, company: str) -> str:
        """
        Analyze self-introduction (1-2 minutes) and provide FAANG-standard feedback with streaming response.
        """
        prompt = get_introduction_prompt(introduction, role, company)
        
        response_stream = await acompletion(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": SystemMessage.INTRODUCTION
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.3,
            stream=True,
        )

        async for chunk in response_stream:
            if chunk.choices and len(chunk.choices) > 0:
                delta = chunk.choices[0].delta
                if hasattr(delta, 'content') and delta.content:
                    yield delta.content

    async def transcribe_audio(self, audio_content: bytes, audio_format: str = AUDIO_TARGET_FORMAT) -> str:
        """
        Transcribe audio using GPT-4o audio model asynchronously via LiteLLM
        
        Args:
            audio_content: Audio bytes in WAV format
            audio_format: Audio format (should be "wav")
            
        Returns:
            Transcribed text
        """
        audio_b64 = base64.b64encode(audio_content).decode()
        
        response = await acompletion(
            model=self.audio_model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": TRANSCRIPTION_PROMPT
                        },
                        {
                            "type": "input_audio",
                            "input_audio": {
                                "data": audio_b64,
                                "format": audio_format
                            }
                        }
                    ]
                }
            ],
            modalities=["text"]
        )
        
        return response.choices[0].message.content

    async def analyze_audio(self, audio_content: bytes, audio_format: str, role: str, company: str) -> str:
        """
        Analyze audio directly using gpt-4o-audio-preview which supports text+audio mixed input.
        
        Args:
            audio_content: Audio bytes in WAV format
            audio_format: Audio format (should be "wav")
            role: Job role
            company: Company name
            
        Returns:
            Analysis feedback
        """
        audio_b64 = base64.b64encode(audio_content).decode()

        text_prompt = get_introduction_prompt(
            introduction=AUDIO_PLACEHOLDER,
            role=role,
            company=company
        )
        
        response = await acompletion(
            model=self.audio_model,
            messages=[
                {
                    "role": "system",
                    "content": SystemMessage.INTRODUCTION
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": text_prompt
                        },
                        {
                            "type": "input_audio",
                            "input_audio": {
                                "data": audio_b64,
                                "format": audio_format
                            }
                        }
                    ]
                }
            ],
            temperature=0.3,
            modalities=["text"]  # Request text output
        )
        
        return response.choices[0].message.content

    async def analyze_audio_stream(self, audio_content: bytes, audio_format: str, role: str, company: str):
        """
        Analyze audio directly using gpt-4o-audio-preview with streaming response.
        
        Args:
            audio_content: Audio bytes in WAV format
            audio_format: Audio format (should be "wav")
            role: Job role
            company: Company name
            
        Yields:
            Text chunks from streaming response
        """
        audio_b64 = base64.b64encode(audio_content).decode()

        text_prompt = get_introduction_prompt(
            introduction=AUDIO_PLACEHOLDER,
            role=role,
            company=company
        )
        
        response_stream = await acompletion(
            model=AUDIO_MODEL,  # Use full audio model for streaming
            messages=[
                {
                    "role": "system",
                    "content": SystemMessage.INTRODUCTION
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": text_prompt
                        },
                        {
                            "type": "input_audio",
                            "input_audio": {
                                "data": audio_b64,
                                "format": audio_format
                            }
                        }
                    ]
                }
            ],
            temperature=0.3,
            modalities=["text"],  # Request text output
            stream=True  # Enable streaming
        )
        
        async for chunk in response_stream:
            if chunk.choices and len(chunk.choices) > 0:
                delta = chunk.choices[0].delta
                if hasattr(delta, 'content') and delta.content:
                    yield delta.content

    async def analyze_bq_question(self, question: str, answer: str, role: str = "Software Engineer") -> str:
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

        response = await acompletion(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": SystemMessage.BQ_QUESTION
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.3
        )

        return response.choices[0].message.content

    async def analyze_bq_question_stream(self, question: str, answer: str, role: str = "Software Engineer") -> str:
        """
        Analyze a specific BQ question answer following FAANG standards with streaming response.
        """
        bq_questions = BQQuestions()
        prompt = bq_questions.get_prompt(question, answer, role)
        
        response_stream = await acompletion(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": SystemMessage.BQ_QUESTION
                },
                {
                    "role": "user",
                    "content": prompt

                },
            ],
            temperature=0.3,
            stream=True
        )

        async for chunk in response_stream:
            if chunk.choices and len(chunk.choices) > 0:
                delta = chunk.choices[0].delta
                if hasattr(delta, 'content') and delta.content:
                    yield delta.content
