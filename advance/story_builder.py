import csv
import os
import sys
from pathlib import Path

_project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from interview_analyzer import InterviewAnalyzer
from prompts import StoryBuilder as StoryBuilderPrompts
from utils import StreamProcessor


class TaxonomyLoader:
    """Load and query the BQ taxonomy"""

    def __init__(self, path: str = "promptbase/bq/taxonomy.csv"):
        self.path = Path(_project_root) / path
        self._data = None

    @property
    def data(self) -> list[dict]:
        if self._data is None:
            self._data = []
            with open(self.path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    self._data.append(row)
        return self._data

    def get_categories(self) -> list[str]:
        """Get unique categories"""
        return list(set(row["category"] for row in self.data))

    def get_sub_scenarios(self, category: str) -> list[dict]:
        """Get sub-scenarios for a category with descriptions"""
        return [
            {"sub_scenario": row["sub_scenario"], "description": row["description"]}
            for row in self.data
            if row["category"] == category
        ]

    def get_scenario_details(self, category: str, sub_scenario: str) -> dict | None:
        """Get full details for a specific scenario"""
        for row in self.data:
            if row["category"] == category and row["sub_scenario"] == sub_scenario:
                return row
        return None


class StoryBuilder:
    """Build BQ stories from scratch through guided brainstorming"""

    # Static STAR questions - same for all scenarios
    CORE_QUESTIONS = [
        "What was the situation or context?",
        "What was your specific role or responsibility?",
        "What actions did YOU take?",
        "What was the outcome or result?",
    ]

    def __init__(self):
        self.analyzer = InterviewAnalyzer()
        self.taxonomy = TaxonomyLoader()

        # State
        self.category = None
        self.sub_scenario = None
        self.scenario_details = None
        self.user_responses = []
        self.draft_story = None

    def get_categories(self) -> list[str]:
        """Get available BQ categories"""
        return self.taxonomy.get_categories()

    def get_sub_scenarios(self, category: str) -> list[dict]:
        """Get sub-scenarios for selected category"""
        return self.taxonomy.get_sub_scenarios(category)

    def select_scenario(self, category: str, sub_scenario: str) -> dict | None:
        """Select a scenario and store details"""
        self.category = category
        self.sub_scenario = sub_scenario
        self.scenario_details = self.taxonomy.get_scenario_details(category, sub_scenario)
        return self.scenario_details

    def get_core_questions(self) -> list[str]:
        """Return static STAR questions"""
        return self.CORE_QUESTIONS

    def add_response(self, question: str, answer: str):
        """Add a user's response to a question"""
        self.user_responses.append({"q": question, "a": answer})

    async def generate_draft(self) -> str:
        """Generate initial STAR draft from user responses"""
        if not self.user_responses:
            raise ValueError("No responses collected")

        # Use the typical question from taxonomy
        question = self.scenario_details.get("typical_question",
            f"Tell me about a time you dealt with {self.sub_scenario.replace('_', ' ')}")

        prompt = StoryBuilderPrompts.generate_draft(
            category=self.category,
            sub_scenario=self.sub_scenario,
            question=question,
            user_responses=self.user_responses
        )
        result = await self.analyzer.customized_analyze(prompt, stream=True)
        self.draft_story = await StreamProcessor.get_text(result)
        return self.draft_story

    def get_question(self) -> str:
        """Get the BQ question for this scenario"""
        if self.scenario_details:
            return self.scenario_details.get("typical_question", "")
        return ""

    def get_draft_for_improver(self) -> dict:
        """Get draft in format ready for StoryImprover"""
        return {
            "question": self.get_question(),
            "answer": self.draft_story,
            "category": self.category,
            "sub_scenario": self.sub_scenario,
            "level": self.level
        }
