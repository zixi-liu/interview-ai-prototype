"""
Utility functions for audio processing and format conversion
"""

import re
import sys
import os
import asyncio
import subprocess
import textwrap
from dataclasses import dataclass, asdict
from datetime import datetime

from interview_analyzer import AUDIO_TARGET_FORMAT


class AudioConverter:
    """Audio format conversion utilities using ffmpeg"""

    # Map common MIME types to ffmpeg format names
    FORMAT_MAP = {
        "mpeg": "mp3",
        "mp4": "mp4",
        "webm": "webm",
        "ogg": "ogg",
        "opus": "opus",
        "flac": "flac",
        "wav": "wav",
        "aac": "aac",
        "m4a": "m4a",
    }

    @staticmethod
    def get_ffmpeg_input_format(content_type: str) -> str:
        """
        Determine ffmpeg input format from content type
        
        Args:
            content_type: MIME type of the audio (e.g., "audio/mpeg")
            
        Returns:
            ffmpeg format name or "auto" for auto-detection
        """
        # Extract format from content type (e.g., "audio/mpeg" -> "mpeg")
        match = re.match(r"audio/([^;]+)", content_type)
        if match:
            format_name = match.group(1).lower()
            return AudioConverter.FORMAT_MAP.get(format_name, format_name)
        
        # Default to auto-detect
        return "auto"

    @staticmethod
    def convert_to_wav_sync(audio_content: bytes, content_type: str) -> bytes:
        """
        Convert audio to WAV format directly in memory using ffmpeg (no temp files)
        
        Args:
            audio_content: Raw audio bytes
            content_type: MIME type of the audio
            
        Returns:
            WAV format audio bytes
            
        Raises:
            RuntimeError: If audio conversion fails
        """
        input_format = AudioConverter.get_ffmpeg_input_format(content_type)
        
        # Build ffmpeg command to convert from stdin to stdout
        # -f: input format
        # -i pipe:0: read from stdin
        # -f wav: output format as WAV
        # -: output to stdout
        # -y: overwrite output file (not needed for stdout, but harmless)
        cmd = [
            "ffmpeg",
            "-f", input_format,
            "-i", "pipe:0",  # Read from stdin
            "-f", AUDIO_TARGET_FORMAT,  # Output format
            "-",  # Output to stdout
            "-y"  # Overwrite (for stdout this is harmless)
        ]
        
        try:
            # Run ffmpeg with audio content as stdin, capture stdout
            process = subprocess.run(
                cmd,
                input=audio_content,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True
            )
            return process.stdout
        except subprocess.CalledProcessError as e:
            # If format detection fails, try with auto-detect
            if input_format != "auto":
                cmd[2] = "auto"  # Change input format to auto-detect
                try:
                    process = subprocess.run(
                        cmd,
                        input=audio_content,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        check=True
                    )
                    return process.stdout
                except subprocess.CalledProcessError:
                    raise RuntimeError(f"Audio conversion failed: {e.stderr.decode('utf-8', errors='ignore')}")
            else:
                raise RuntimeError(f"Audio conversion failed: {e.stderr.decode('utf-8', errors='ignore')}")

    @staticmethod
    async def convert_to_wav(audio_content: bytes, content_type: str) -> bytes:
        """
        Convert audio content to WAV format asynchronously
        
        Args:
            audio_content: Raw audio bytes
            content_type: MIME type of the audio
            
        Returns:
            WAV format audio bytes
            
        Raises:
            RuntimeError: If audio conversion fails
        """
        # Run CPU-intensive conversion in thread pool to avoid blocking event loop
        return await asyncio.to_thread(
            AudioConverter.convert_to_wav_sync,
            audio_content,
            content_type
        )


# ANSI color codes
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

    def feedback(feedback: str):
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
        
        # Colorful No-Pass, No Hire (case insensitive) - must come before "Pass" and "Hire"
        colored_feedback = re.sub(
            r'\b(No-Pass|No Hire|Leaning No Hire|Below|Concern)\b',
            f'{Colors.RED}{Colors.BOLD}\\1{Colors.RESET}',
            feedback,
            flags=re.IGNORECASE
        )
        if Colors.RESET in colored_feedback:
            return colored_feedback
        
        # Colorful Weak Hire (case insensitive) - must come before "Hire"
        colored_feedback = re.sub(
            r'\b(Weak Hire|Borderline|Leaning Hire)\b',
            f'{Colors.YELLOW}{Colors.BOLD}\\1{Colors.RESET}',
            colored_feedback,
            flags=re.IGNORECASE
        )
        if Colors.RESET in colored_feedback:
            return colored_feedback
        
        # Colorful Pass, Hire (case insensitive) - comes after "No-Pass" and "Strong Hire"/"Weak Hire"
        colored_feedback = re.sub(  
            r'\b(Strong Hire|Pass|Hire|Meets+|Strong)\b',
            f'{Colors.GREEN}{Colors.BOLD}\\1{Colors.RESET}',
            colored_feedback,
            flags=re.IGNORECASE
        )
        
        return colored_feedback

    @staticmethod
    async def stream_and_print(stream_generator) -> str:
        """Helper function to stream and print chunks"""
        text = ''
        buffer = ''
        async for chunk in stream_generator:
            buffer += chunk
            text += chunk
            
            # Print complete lines when we encounter newlines
            while '\n' in buffer:
                line, buffer = buffer.split('\n', 1)
                print(Colors.feedback(line + '\n'), end='')
        
        # Print remaining content
        if buffer:
            print(Colors.feedback(buffer), end='')
        print()

        return text


class StreamProcessor:
    @staticmethod
    async def get_text(stream_generator) -> str:
        text = ''
        async for chunk in stream_generator:
            text += chunk
        return text



@dataclass
class ParsedEvaluation:
    """Structured evaluation data parsed from markdown output."""
    raw_notes: list[str]
    summary: str
    strengths: list[str]
    areas_for_improvement: list[str]
    competency_ratings: dict[str, str]
    weak_competencies: list[str]
    recommendation: str
    recommendation_justification: str
    probing_questions: list[str]

    def to_dict(self) -> dict:
        return asdict(self)


class EvaluationParser:
    """Parse real_interview() markdown output to structured JSON."""

    @staticmethod
    def parse(evaluation: str) -> ParsedEvaluation:
        """
        Parse markdown evaluation to structured data.
        Uses simple string splitting on "====" delimiters.
        """
        sections = evaluation.split("=" * 60)

        raw_notes = []
        summary = ""
        strengths = []
        areas_for_improvement = []
        competency_ratings = {}
        weak_competencies = []
        recommendation = ""
        recommendation_justification = ""
        probing_questions = []

        for section in sections:
            section = section.strip()
            if not section:
                continue

            if "1. Real-Time Raw Notes" in section:
                raw_notes = EvaluationParser._extract_bullets(section)

            elif "2. Formal Interview Summary" in section:
                lines = section.split('\n')
                content_lines = [l.strip() for l in lines[1:] if l.strip()]
                summary = ' '.join(content_lines)

            elif "3. Strengths" in section:
                strengths = EvaluationParser._extract_bullets(section)

            elif "4. Areas for Improvement" in section:
                areas_for_improvement = EvaluationParser._extract_bullets(section)

            elif "5. Competency Ratings" in section:
                competency_ratings, weak_competencies = EvaluationParser._extract_ratings(section)

            elif "6. Final Overall Recommendation" in section:
                recommendation, recommendation_justification = EvaluationParser._extract_recommendation(section)

            elif "7. Probing Follow-up Questions" in section:
                probing_questions = EvaluationParser._extract_probing_questions(section)

        return ParsedEvaluation(
            raw_notes=raw_notes,
            summary=summary,
            strengths=strengths,
            areas_for_improvement=areas_for_improvement,
            competency_ratings=competency_ratings,
            weak_competencies=weak_competencies,
            recommendation=recommendation,
            recommendation_justification=recommendation_justification,
            probing_questions=probing_questions
        )

    @staticmethod
    def _extract_bullets(section: str) -> list[str]:
        """Extract bullet points (lines starting with - or •)."""
        bullets = []
        for line in section.split('\n'):
            line = line.strip()
            if line.startswith('-') or line.startswith('•'):
                bullets.append(line[1:].strip())
        return bullets

    @staticmethod
    def _extract_ratings(section: str) -> tuple[dict[str, str], list[str]]:
        """Extract competency ratings and identify weak ones."""
        ratings = {}
        weak = []

        for line in section.split('\n'):
            line = line.strip()
            if line.startswith('-') and ':' in line:
                parts = line[1:].split(':', 1)
                if len(parts) == 2:
                    name = parts[0].strip()
                    rating = parts[1].strip()
                    ratings[name] = rating

                    if 'Below' in rating or 'Concern' in rating or '🤔' in rating or '❌' in rating:
                        weak.append(name)

        return ratings, weak

    @staticmethod
    def _extract_recommendation(section: str) -> tuple[str, str]:
        """Extract recommendation and justification."""
        recommendation = ""
        justification_lines = []
        found_rec = False

        for line in section.split('\n'):
            line = line.strip()
            if any(emoji in line for emoji in ['🌟', '👍', '🤔', '🤨', '❌']):
                if 'Hire' in line:
                    recommendation = line.lstrip('- ')
                    found_rec = True
            elif found_rec and line and not line.startswith('STRICT') and not line.startswith('Choose'):
                justification_lines.append(line)

        justification = ' '.join(justification_lines).strip()
        return recommendation, justification

    @staticmethod
    def _extract_probing_questions(section: str) -> list[str]:
        """Extract probing questions from bullet points or numbered lists."""
        import re
        questions = []
        for line in section.split('\n'):
            line = line.strip()
            # Skip header line
            if 'Probing' in line and 'Question' in line:
                continue

            # Match bullet points (-) or numbered lists (1., 2., etc.)
            if line.startswith('-'):
                q = line[1:].strip()
            elif re.match(r'^\d+[\.\)]\s*', line):
                q = re.sub(r'^\d+[\.\)]\s*', '', line).strip()
            else:
                continue

            # Clean up if there's a label like "Ownership: \"question\""
            if ':' in q and '"' in q:
                q = q.split(':', 1)[1].strip().strip('"')

            if q:
                questions.append(q)
        return questions


class FeedbackParser:
    """Regex-based parsing for feedback content"""

    @staticmethod
    def extract_rating(content: str) -> str:
        """Extract rating from feedback (checks Final Overall Recommendation first, then header)"""
        # From AI response
        match = re.search(r'Final Overall Recommendation.*?(Strong Hire|Leaning No Hire|Leaning Hire|No Hire|Hire)', content, re.IGNORECASE | re.DOTALL)
        if match:
            return match.group(1)
        # From saved file header
        match = re.search(r'\*\*Rating\*\*:\s*(\w+)', content)
        if match:
            return match.group(1).replace("_", " ")
        return None

    @staticmethod
    def extract_question(content: str) -> str:
        """Extract question from feedback markdown"""
        match = re.search(r'## Question\s*\n\n(.+?)(?=\n\n##)', content, re.DOTALL)
        return match.group(1).strip() if match else None

    @staticmethod
    def extract_answer(content: str) -> str:
        """Extract answer from feedback markdown"""
        match = re.search(r'## Answer\s*\n\n(.+?)(?=\n\n##)', content, re.DOTALL)
        return match.group(1).strip() if match else None

    @staticmethod
    def extract_probing_questions(feedback: str) -> list:
        """Extract probing follow-up questions from feedback text"""
        questions = []
        match = re.search(r'Probing Follow-up Questions(.*?)(?:={3,}|$)', feedback, re.DOTALL | re.IGNORECASE)
        if match:
            for line in match.group(1).strip().split('\n'):
                line = line.strip()
                line = re.sub(r'^[-*•]\s*', '', line)
                line = re.sub(r'^\d+[\.\)]\s*', '', line)
                if line and '?' in line:
                    questions.append(line)
        return questions[:6]


class FeedbackRecorder:
    """Feedback recorder for real interview evaluation"""

    FEEDBACK_DIR = "feedbacks"

    RATING_PATTERNS = [
        r"\b🌟 Strong Hire\b",
        r"\b👍 Hire\b",
        r"\b🤔 Leaning Hire\b",
        r"\b🤨 Leaning No Hire\b",
        r"\b❌ No Hire\b",
        r"\bStrong Hire\b",
        r"\bWeak Hire\b",
        r"\bLeaning Hire\b",
        r"\bBorderline\b",
        r"\bLeaning No Hire\b",
        r"\bNo-Pass\b",
        r"\bNo Hire\b",
        r"\bPass\b",
        r"\bHire\b",
    ]

    def __init__(self, base_dir: str | None = None) -> None:
        """
        Args:
            base_dir: Optional base directory to store feedback files.
                      Defaults to current working directory.
        """
        self.base_dir = base_dir or os.getcwd()

    def _extract_rating(self, feedback: str) -> str:
        """Try to extract a rating label from the feedback text."""
        for pattern in self.RATING_PATTERNS:
            match = re.search(pattern, feedback, flags=re.IGNORECASE)
            if match:
                # Normalize spaces and capitalization a bit for file name
                rating = match.group(0)
                rating = rating.replace(" ", "_")
                return rating
        return "NA"

    def _ensure_feedback_dir(self) -> str:
        """Ensure feedback directory exists and return its full path."""
        path = os.path.join(self.base_dir, self.FEEDBACK_DIR)
        os.makedirs(path, exist_ok=True)
        return path

    def _unique_filepath(self, directory: str, filename: str) -> str:
        """Avoid overwriting existing files by appending a numeric suffix."""
        base, ext = os.path.splitext(filename)
        candidate = os.path.join(directory, filename)
        counter = 1
        while os.path.exists(candidate):
            candidate = os.path.join(directory, f"{base}_{counter}{ext}")
            counter += 1
        return candidate

    def save_feedback(
        self, 
        question: str, 
        answer: str, 
        feedback: str,
        red_flag: str | None = None) -> str:
        """
        Save a single interview feedback record as a markdown file.

        The file name format is: yyyymmdd-{rating}.md

        Args:
            question: The interview question text.
            answer: The candidate's answer text.
            feedback: The evaluation/feedback text (containing rating keywords).
            red_flag: Optional red flag evaluation text.

        Returns:
            The full file path of the created markdown file.
        """
        date_str = datetime.now().strftime("%Y%m%d")
        rating = self._extract_rating(feedback)

        filename = f"{date_str}-{rating}.md"
        directory = self._ensure_feedback_dir()
        filepath = self._unique_filepath(directory, filename)

        # Normalize blocks to avoid extra indentation in markdown
        norm_question = textwrap.dedent(question).strip()
        norm_answer = textwrap.dedent(answer).strip()
        norm_feedback = textwrap.dedent(feedback).strip()

        content_lines = [
            f"# {'Red Flag Evaluation' if red_flag else 'Interview Feedback'} ({date_str})",
            "",
            f"**Rating**: {rating}",
            "",
            "## Question",
            "",
            norm_question,
            "",
            "## Answer",
            "",
            norm_answer,
            "",
            "## Feedback",
            "",
            norm_feedback,
            "",
        ]

        if red_flag:
            norm_red_flag = textwrap.dedent(red_flag).strip()
            content_lines.extend([
                "## Red Flag",
                "",
                norm_red_flag,
                "",
            ])
        else:
            content_lines.extend([
                "## Feedback",
                "",
                norm_feedback,
                "",
            ])

        with open(filepath, "w", encoding="utf-8") as f:
            f.write("\n".join(content_lines))

        return filepath