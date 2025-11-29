"""
BQ Interview Analyzer using LiteLLM
Analyzes behavioral questions and self-introductions for FAANG interviews
"""

import base64
from typing import AsyncIterator, List, Dict, Any
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

    @staticmethod
    def _build_audio_messages(
        system_content: str, 
        text_prompt: str, 
        audio_b64: str, 
        audio_format: str
    ) -> List[Dict[str, Any]]:
        """Build messages with audio input for LLM API."""
        return [
            {"role": "system", "content": system_content},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": text_prompt},
                    {
                        "type": "input_audio",
                        "input_audio": {
                            "data": audio_b64,
                            "format": audio_format
                        }
                    }
                ]
            }
        ]

    @staticmethod
    async def _extract_stream_chunks(response_stream: AsyncIterator) -> AsyncIterator[str]:
        """Extract content chunks from streaming response."""
        async for chunk in response_stream:
            if chunk.choices and len(chunk.choices) > 0:
                delta = chunk.choices[0].delta
                if hasattr(delta, 'content') and delta.content:
                    yield delta.content

    async def analyze_introduction(
        self, 
        introduction: str, 
        role: str, 
        company: str, 
        stream: bool = False
    ):
        """
        Analyze self-introduction (1-2 minutes) and provide FAANG-standard feedback.

        Args:
            introduction: Self-introduction text (1-2 minutes worth)
            role: Job role being interviewed for
            company: Target company name
            stream: Whether to stream the response

        Returns:
            If stream=False: Complete feedback string
            If stream=True: Async iterator yielding text chunks
        """
        prompt = get_introduction_prompt(introduction, role, company)
        messages = [
            {"role": "system", "content": SystemMessage.INTRODUCTION},
            {"role": "user", "content": prompt}
        ]
        
        response = await acompletion(
            model=self.model,
            messages=messages,
            temperature=0.3,
            stream=stream
        )

        if stream:
            return self._extract_stream_chunks(response)
        else:
            return response.choices[0].message.content

    async def transcribe_audio(
        self, 
        audio_content: bytes, 
        audio_format: str = AUDIO_TARGET_FORMAT
    ) -> str:
        """
        Transcribe audio using GPT-4o audio model asynchronously via LiteLLM.
        
        Args:
            audio_content: Audio bytes in WAV format
            audio_format: Audio format (should be "wav")
            
        Returns:
            Transcribed text
        """
        audio_b64 = base64.b64encode(audio_content).decode()
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": TRANSCRIPTION_PROMPT},
                    {
                        "type": "input_audio",
                        "input_audio": {
                            "data": audio_b64,
                            "format": audio_format
                        }
                    }
                ]
            }
        ]
        
        response = await acompletion(
            model=self.audio_model,
            messages=messages,
            modalities=["text"]
        )
        
        return response.choices[0].message.content

    async def analyze_audio(
        self, 
        audio_content: bytes, 
        audio_format: str, 
        role: str, 
        company: str, 
        stream: bool = False
    ):
        """
        Analyze audio directly using gpt-4o-audio-preview which supports text+audio mixed input.
        
        Args:
            audio_content: Audio bytes in WAV format
            audio_format: Audio format (should be "wav")
            role: Job role
            company: Company name
            stream: Whether to stream the response
            
        Returns:
            If stream=False: Complete analysis feedback string
            If stream=True: Async iterator yielding text chunks
        """
        audio_b64 = base64.b64encode(audio_content).decode()
        text_prompt = get_introduction_prompt(
            introduction=AUDIO_PLACEHOLDER,
            role=role,
            company=company
        )
        messages = self._build_audio_messages(
            SystemMessage.INTRODUCTION,
            text_prompt,
            audio_b64,
            audio_format
        )
        
        # Use full audio model for streaming, mini for non-streaming
        model = AUDIO_MODEL if stream else self.audio_model
        
        response = await acompletion(
            model=model,
            messages=messages,
            temperature=0.3,
            stream=stream,
            modalities=["text"]
        )

        if stream:
            return self._extract_stream_chunks(response)
        else:
            return response.choices[0].message.content

    async def analyze_bq_question(
        self, 
        question: str, 
        answer: str, 
        role: str = "Software Engineer",
        stream: bool = False
    ):
        """
        Analyze a specific BQ question answer following FAANG standards.
        
        Args:
            question: The BQ question asked (e.g., "Tell me about your most challenging project")
            answer: The candidate's answer
            role: Job role being interviewed for
            stream: Whether to stream the response
            
        Returns:
            If stream=False: Complete feedback string
            If stream=True: Async iterator yielding text chunks
        """
        bq_questions = BQQuestions()
        prompt = bq_questions.get_prompt(question, answer, role)
        messages = [
            {"role": "system", "content": SystemMessage.BQ_QUESTION},
            {"role": "user", "content": prompt}
        ]

        response = await acompletion(
            model=self.model,
            messages=messages,
            temperature=0.3,
            stream=stream
        )

        if stream:
            return self._extract_stream_chunks(response)
        else:
            return response.choices[0].message.content

    async def customized_analyze(
        self,
        prompt: str,
        stream: bool = False
    ):
        """
        Customized analyze using a custom prompt

        Args:
            prompt: Custom prompt
            stream: Whether to stream the response

        Returns:
            If stream=False: Complete feedback string
            If stream=True: Async iterator yielding text chunks
        """
        messages = [
            {"role": "user", "content": prompt}
        ]

        response = await acompletion(
            model=self.model,
            messages=messages,
            temperature=0.3,
            stream=stream
        )

        if stream:
            return self._extract_stream_chunks(response)
        else:
            return response.choices[0].message.content