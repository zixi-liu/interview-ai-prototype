"""
Utility functions for audio processing and format conversion
"""

import re
import sys
import asyncio
import subprocess

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
            r'\b(No-Pass|No Hire)\b',
            f'{Colors.RED}{Colors.BOLD}\\1{Colors.RESET}',
            feedback,
            flags=re.IGNORECASE
        )
        if Colors.RESET in colored_feedback:
            return colored_feedback
        
        # Colorful Weak Hire (case insensitive) - must come before "Hire"
        colored_feedback = re.sub(
            r'\b(Weak Hire|Borderline)\b',
            f'{Colors.YELLOW}{Colors.BOLD}\\1{Colors.RESET}',
            colored_feedback,
            flags=re.IGNORECASE
        )
        if Colors.RESET in colored_feedback:
            return colored_feedback
        
        # Colorful Pass, Hire (case insensitive) - comes after "No-Pass" and "Strong Hire"/"Weak Hire"
        colored_feedback = re.sub(  
            r'\b(Strong Hire|Pass|Hire)\b',
            f'{Colors.GREEN}{Colors.BOLD}\\1{Colors.RESET}',
            colored_feedback,
            flags=re.IGNORECASE
        )
        
        return colored_feedback

    async def stream_and_print(stream_generator):
        """Helper function to stream and print chunks"""
        buffer = ''
        async for chunk in stream_generator:
            buffer += chunk
            
            # Print complete lines when we encounter newlines
            while '\n' in buffer:
                line, buffer = buffer.split('\n', 1)
                print(Colors.feedback(line + '\n'), end='')
        
        # Print remaining content
        if buffer:
            print(Colors.feedback(buffer), end='')
        print()