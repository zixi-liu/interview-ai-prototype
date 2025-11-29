"""
Local storage for interview practice history
Saves to ./history.json (under the project directory)
"""

import json
import uuid
import re
from datetime import datetime
from pathlib import Path
from typing import Optional


DEFAULT_STORAGE_DIR = Path(__file__).parent
HISTORY_FILE = "history.json"


class LocalStorage:
    """Manage local storage of practice sessions"""

    def __init__(self, storage_dir: Path = DEFAULT_STORAGE_DIR):
        self.storage_dir = storage_dir
        self.history_file = storage_dir / HISTORY_FILE
        self._ensure_storage_dir()

    def _ensure_storage_dir(self):
        """Create storage directory if it doesn't exist"""
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def _load_history(self) -> dict:
        """Load history from file"""
        if not self.history_file.exists():
            return {"sessions": []}
        with open(self.history_file, "r") as f:
            return json.load(f)

    def _save_history(self, data: dict):
        """Save history to file"""
        with open(self.history_file, "w") as f:
            json.dump(data, f, indent=2)
        self._generate_html(data)

    def _format_text(self, text: str) -> str:
        """Format text with markdown-like styling for HTML"""
        import re
        # Escape HTML
        text = text.replace("<", "&lt;").replace(">", "&gt;")
        # Bold **text** or __text__
        text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
        text = re.sub(r'__(.+?)__', r'<strong>\1</strong>', text)
        # Italic *text* or _text_
        text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
        text = re.sub(r'(?<![_\w])_(.+?)_(?![_\w])', r'<em>\1</em>', text)
        # Headers ## Header
        text = re.sub(r'^### (.+)$', r'<h4>\1</h4>', text, flags=re.MULTILINE)
        text = re.sub(r'^## (.+)$', r'<h3>\1</h3>', text, flags=re.MULTILINE)
        text = re.sub(r'^# (.+)$', r'<h2>\1</h2>', text, flags=re.MULTILINE)
        # Bullet points
        text = re.sub(r'^- (.+)$', r'<li>\1</li>', text, flags=re.MULTILINE)
        text = re.sub(r'^• (.+)$', r'<li>\1</li>', text, flags=re.MULTILINE)
        # Numbered lists
        text = re.sub(r'^\d+\. (.+)$', r'<li>\1</li>', text, flags=re.MULTILINE)
        # Colorize ratings - only match standalone ratings (with word boundaries)
        text = re.sub(r'\b(Strong Hire)\b', r'<span style="color: #28a745; font-weight: 600;">\1</span>', text, flags=re.IGNORECASE)
        text = re.sub(r'\b(Leaning No Hire)\b', r'<span style="color: #fd7e14; font-weight: 600;">\1</span>', text, flags=re.IGNORECASE)
        text = re.sub(r'\b(Leaning Hire)\b', r'<span style="color: #ffc107; font-weight: 600;">\1</span>', text, flags=re.IGNORECASE)
        text = re.sub(r'(?<!Leaning )(?<!Strong )\b(No Hire)\b', r'<span style="color: #dc3545; font-weight: 600;">\1</span>', text, flags=re.IGNORECASE)
        text = re.sub(r'(?<!No )(?<!Strong )(?<!Leaning )\b(Hire)\b', r'<span style="color: #28a745; font-weight: 600;">\1</span>', text, flags=re.IGNORECASE)
        # Pass/No Pass ratings - only standalone
        text = re.sub(r'\b(No-Pass|No Pass)\b', r'<span style="color: #dc3545; font-weight: 600;">\1</span>', text, flags=re.IGNORECASE)
        text = re.sub(r'(?<!No[ -])\b(Pass)\b', r'<span style="color: #28a745; font-weight: 600;">\1</span>', text, flags=re.IGNORECASE)
        return text

    def _generate_html(self, data: dict):
        """Generate readable HTML version of history"""
        html_file = self.storage_dir / "history.html"
        sessions = data.get("sessions", [])

        # Count stats
        total = len(sessions)
        by_rating = {}
        for s in sessions:
            r = s.get("rating", "N/A")
            by_rating[r] = by_rating.get(r, 0) + 1

        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Interview Bro - Practice History</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 1200px; margin: 0 auto; padding: 20px; background: #fff; color: #333; }}
        h1 {{ color: #333; }}
        h2, h3, h4 {{ color: #333; margin: 10px 0 5px 0; }}
        .stats {{ background: #f8f9fa; padding: 15px 20px; border-radius: 8px; margin-bottom: 20px; border: 1px solid #e0e0e0; }}
        .stats span {{ margin-right: 20px; }}
        .session {{ background: #fff; padding: 20px; border-radius: 8px; margin-bottom: 15px; border: 1px solid #e0e0e0; box-shadow: 0 1px 3px rgba(0,0,0,0.08); }}
        .session-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; cursor: pointer; }}
        .session-header:hover {{ opacity: 0.8; }}
        .session-meta {{ color: #666; font-size: 14px; }}
        .session-question {{ font-weight: 600; font-size: 16px; color: #333; }}
        .rating {{ padding: 4px 10px; border-radius: 4px; font-size: 12px; font-weight: 600; }}
        .rating-strong-hire {{ background: #28a745; color: #fff; }}
        .rating-hire {{ background: #28a745; color: #fff; }}
        .rating-leaning-hire {{ background: #ffc107; color: #000; }}
        .rating-leaning-no-hire {{ background: #fd7e14; color: #fff; }}
        .rating-no-hire {{ background: #dc3545; color: #fff; }}
        .session-content {{ display: none; border-top: 1px solid #e0e0e0; padding-top: 15px; margin-top: 15px; }}
        .session.expanded .session-content {{ display: block; }}
        .section {{ margin-bottom: 20px; }}
        .section-title {{ font-weight: 700; color: #333; margin-bottom: 8px; font-size: 15px; }}
        .section-body {{ background: #f8f9fa; padding: 15px; border-radius: 4px; white-space: pre-wrap; font-size: 14px; line-height: 1.2; }}
        .section-body li {{ margin-left: 20px; margin-top: 0; margin-bottom: 0; padding: 0; list-style-type: disc; }}
        .toggle-icon {{ font-size: 12px; color: #666; }}
    </style>
</head>
<body>
    <h1>Interview Bro - Practice History</h1>
    <div class="stats">
        <span><strong>Total:</strong> {total}</span>
        {' '.join(f'<span><strong>{r}:</strong> {c}</span>' for r, c in by_rating.items())}
    </div>
"""

        for s in reversed(sessions):  # Most recent first
            rating = s.get("rating", "N/A")
            if "Strong Hire" in rating:
                rating_class = "rating-strong-hire"
            elif "Leaning No Hire" in rating:
                rating_class = "rating-leaning-no-hire"
            elif "Leaning Hire" in rating:
                rating_class = "rating-leaning-hire"
            elif "No Hire" in rating:
                rating_class = "rating-no-hire"
            elif "Hire" in rating:
                rating_class = "rating-hire"
            else:
                rating_class = "rating-leaning-hire"

            timestamp = s.get("timestamp", "")[:16].replace("T", " ")
            session_type = s.get("type", "").upper()
            category = s.get("category", "")
            question = s.get("question", "")
            answer = self._format_text(s.get("answer", ""))
            feedback = self._format_text(s.get("feedback", ""))
            red_flag = s.get("red_flag_feedback", "")
            if red_flag:
                red_flag = self._format_text(red_flag)

            html += f"""
    <div class="session" id="session-{s.get('id', '')}">
        <div class="session-header" onclick="this.parentElement.classList.toggle('expanded')">
            <div>
                <div class="session-question">{question}</div>
                <div class="session-meta">{timestamp} · {session_type} {('· ' + category) if category else ''}</div>
            </div>
            <div>
                <span class="rating {rating_class}">{rating}</span>
                <span class="toggle-icon">▼</span>
            </div>
        </div>
        <div class="session-content">
            <div class="section">
                <div class="section-title">Your Answer</div>
                <div class="section-body">{answer}</div>
            </div>
            <div class="section">
                <div class="section-title">Feedback</div>
                <div class="section-body">{feedback}</div>
            </div>
            {"<div class='section'><div class='section-title'>Red Flag Analysis</div><div class='section-body'>" + red_flag + "</div></div>" if red_flag else ""}
        </div>
    </div>
"""

        html += """
</body>
</html>"""

        with open(html_file, "w") as f:
            f.write(html)

    def _extract_rating(self, feedback: str) -> Optional[str]:
        """Extract rating from feedback text"""
        # First try to find rating in "Overall Rating" section (more accurate)
        overall_match = re.search(r'Overall Rating[:\s]*\*?\*?([^*\n]+)\*?\*?', feedback, re.IGNORECASE)
        if overall_match:
            overall_text = overall_match.group(1).strip()
            # Check for known ratings in the overall section
            for rating in ['Strong Hire', 'Weak Hire', 'Leaning No Hire', 'Leaning Hire', 'No Hire', 'Hire']:
                if rating.lower() in overall_text.lower():
                    return rating

        # Fallback: search entire feedback (order matters - more specific first)
        patterns = [
            r'(Strong Hire)',
            r'(Weak Hire)',
            r'(Leaning No Hire)',
            r'(Leaning Hire)',
            r'(No Hire)',
            r'(Hire)',
        ]
        for pattern in patterns:
            match = re.search(pattern, feedback, re.IGNORECASE)
            if match:
                return match.group(1)
        return None

    def save_session(
        self,
        session_type: str,
        question: str,
        answer: str,
        feedback: str,
        category: Optional[str] = None,
        level: Optional[str] = None,
        role: Optional[str] = None,
        company: Optional[str] = None,
        red_flag_feedback: Optional[str] = None
    ) -> str:
        """
        Save a practice session

        Args:
            session_type: "intro" or "bq"
            question: The question asked (or "Self-Introduction" for intro)
            answer: User's answer
            feedback: AI feedback
            category: BQ category (conflict, failure, etc.)
            level: Interview level (Junior-Mid, Senior, Staff)
            role: Target job role
            company: Target company
            red_flag_feedback: Red flag analysis (if any)

        Returns:
            Session ID
        """
        history = self._load_history()

        session_id = str(uuid.uuid4())[:8]
        session = {
            "id": session_id,
            "timestamp": datetime.now().isoformat(),
            "type": session_type,
            "question": question,
            "answer": answer,
            "feedback": feedback,
            "rating": self._extract_rating(feedback),
        }

        if category:
            session["category"] = category
        if level:
            session["level"] = level
        if role:
            session["role"] = role
        if company:
            session["company"] = company
        if red_flag_feedback:
            session["red_flag_feedback"] = red_flag_feedback

        history["sessions"].append(session)
        self._save_history(history)

        return session_id

    def get_all_sessions(self) -> list:
        """Get all practice sessions"""
        history = self._load_history()
        return history["sessions"]

    def get_sessions_by_category(self, category: str) -> list:
        """Get sessions filtered by category"""
        sessions = self.get_all_sessions()
        return [s for s in sessions if s.get("category") == category]

    def get_sessions_by_type(self, session_type: str) -> list:
        """Get sessions filtered by type (intro or bq)"""
        sessions = self.get_all_sessions()
        return [s for s in sessions if s.get("type") == session_type]

    def get_sessions_by_rating(self, rating: str) -> list:
        """Get sessions filtered by rating"""
        sessions = self.get_all_sessions()
        return [s for s in sessions if s.get("rating") and rating.lower() in s["rating"].lower()]

    def get_sessions_by_question(self, question_substring: str) -> list:
        """Get sessions where question contains substring"""
        sessions = self.get_all_sessions()
        return [s for s in sessions if question_substring.lower() in s.get("question", "").lower()]

    def get_last_n_sessions(self, n: int) -> list:
        """Get the last n sessions"""
        sessions = self.get_all_sessions()
        return sessions[-n:] if len(sessions) >= n else sessions

    def get_session_by_id(self, session_id: str) -> Optional[dict]:
        """Get a specific session by ID"""
        sessions = self.get_all_sessions()
        for s in sessions:
            if s.get("id") == session_id:
                return s
        return None

    def get_stats(self) -> dict:
        """Get practice statistics"""
        sessions = self.get_all_sessions()

        if not sessions:
            return {"total": 0}

        stats = {
            "total": len(sessions),
            "intro": len([s for s in sessions if s.get("type") == "intro"]),
            "bq": len([s for s in sessions if s.get("type") == "bq"]),
            "by_category": {},
            "by_rating": {},
        }

        for s in sessions:
            cat = s.get("category", "intro")
            stats["by_category"][cat] = stats["by_category"].get(cat, 0) + 1

            rating = s.get("rating")
            if rating:
                stats["by_rating"][rating] = stats["by_rating"].get(rating, 0) + 1

        return stats

    def clear_history(self):
        """Clear all history"""
        self._save_history({"sessions": []})
