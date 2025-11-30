"""
Interactive CLI for Interview Practice
Supports self-introduction and behavioral question practice with AI feedback
"""

import argparse
import asyncio
import json
import sys
import webbrowser
from pathlib import Path

from prompt_toolkit import PromptSession
from prompt_toolkit.history import InMemoryHistory

from interview_analyzer import InterviewAnalyzer
from prompts import BQQuestions, BQAnswer, get_introduction_prompt, SystemMessage
from storage import LocalStorage
from utils import Colors, FeedbackParser
from advance.story_builder import StoryBuilder

# Add missing color codes
Colors.CYAN = '\033[96m'
Colors.DIM = '\033[2m'


def strip_star_prefixes(text: str) -> str:
    """Remove STAR prefixes like **Situation:** for cleaner evaluation"""
    import re
    # Remove markdown bold STAR prefixes
    text = re.sub(r'\*\*(Situation|Task|Action|Result):\*\*\s*', '', text)
    # Also handle non-bold versions
    text = re.sub(r'(Situation|Task|Action|Result):\s*', '', text)
    return text.strip()


class QuestionBank:
    """Load and manage questions from questions.json"""

    def __init__(self, path: str = "promptbase/bq/questions.json"):
        self.path = Path(path)
        self.questions = self._load()

    def _load(self) -> dict:
        if not self.path.exists():
            return {}
        with open(self.path, "r") as f:
            return json.load(f)

    def get_categories(self) -> list:
        return list(self.questions.keys())

    def get_questions(self, category: str) -> list:
        return self.questions.get(category, [])


class InterviewCLI:
    """Interactive CLI for interview practice"""

    def __init__(self):
        self.analyzer = InterviewAnalyzer()
        self.question_bank = QuestionBank()
        self.bq = BQQuestions()
        self.storage = LocalStorage()
        self.last_filtered_sessions = []
        # prompt_toolkit session for command history (up/down arrows)
        self.prompt_session = PromptSession(history=InMemoryHistory())

    def print_header(self, text: str):
        print(f"\n{text}\n")


    async def print_menu(self, title: str, options: list, show_commands: bool = False) -> int:
        """Display menu and get user choice. Returns -1 for quit, or option number."""
        print(f"\n{title}")
        for i, option in enumerate(options, 1):
            print(f"  {i}. {option}")
        if show_commands:
            print(f"\n{Colors.DIM}  ⎿ Tip: /q to exit, /history, /help{Colors.RESET}")

        while True:
            try:
                choice = (await self.prompt_session.prompt_async("\n> ")).strip()
            except (EOFError, KeyboardInterrupt):
                return -1

            if choice.lower() in ['q', '/q']:
                return -1
            if choice.startswith('/') and show_commands:
                cmd = choice[1:]  # Remove leading /
                show_menu = await self.handle_command(cmd)
                return -2 if show_menu else -3  # -2 = show menu, -3 = wait for input
            if choice.isdigit():
                num = int(choice)
                if 1 <= num <= len(options):
                    return num
            print("Please enter a number to select an option")

    async def handle_command(self, cmd: str) -> bool:
        """Handle slash commands. Returns True if should show menu, False otherwise."""
        cmd = cmd.strip().lower()

        if cmd == "history":
            print("\nView history:")
            print("  1. In terminal")
            print("  2. In browser (HTML)")
            choice = (await self.prompt_session.prompt_async("\n> ")).strip()
            if choice == "2":
                html_path = self.storage.storage_dir / "history.html"
                self.storage._generate_html(self.storage._load_history())
                webbrowser.open(f"file://{html_path}")
                print("Opened in browser.")
            else:
                sessions = self.storage.get_all_sessions()
                await self.show_history(sessions)
            return False
        elif cmd.startswith("history --category "):
            category = cmd.replace("history --category ", "")
            sessions = self.storage.get_sessions_by_category(category)
            await self.show_history(sessions)
            return False
        elif cmd.startswith("history --rating "):
            rating = cmd.replace("history --rating ", "")
            sessions = self.storage.get_sessions_by_rating(rating)
            await self.show_history(sessions)
            return False
        elif cmd.startswith("history --search "):
            query = cmd.replace("history --search ", "")
            sessions = self.storage.get_sessions_by_question(query)
            await self.show_history(sessions)
            return False
        elif cmd == "open all":
            if not self.last_filtered_sessions:
                print("No sessions to display. Run /history first.")
            else:
                for session in self.last_filtered_sessions:
                    await self.print_session(session, show_full=True)
                    print("\n" + "─" * 50 + "\n")
            return False
        elif cmd.startswith("open "):
            session_id = cmd.replace("open ", "")
            session = self.storage.get_session_by_id(session_id)
            if session:
                await self.print_session(session, show_full=True)
            else:
                print("Session not found.")
            return False
        elif cmd == "stats":
            self.show_stats()
            return False
        elif cmd == "help":
            print(f"\n{Colors.DIM}Commands:{Colors.RESET}")
            print("  /history                  Show all history")
            print("  /history --category X     Filter by category")
            print("  /history --rating X       Filter by rating")
            print("  /history --search X       Search by question")
            print("  /open <session_id>        View full session details")
            print("  /open all                 View all filtered sessions")
            print("  /stats                    Show practice statistics")
            print("  /question                 Show practice options")
            return False
        elif cmd == "question":
            return True  # Show menu
        else:
            print(f"Unknown command. Type /help for options.")
            return False

    async def get_multiline_input(self, prompt_text: str) -> str:
        print(f"\n{prompt_text}")
        print(f"{Colors.DIM}  ⎿ Tip: Enter twice to submit, /q to exit{Colors.RESET}\n")

        lines = []
        empty_count = 0

        while True:
            line = await self.prompt_session.prompt_async("")
            # Immediate commands - return as-is without needing double Enter
            if line.strip().lower() in ["/q", "/done", "/question", "/skip"]:
                return line.strip().lower()
            if line == "":
                empty_count += 1
                if empty_count >= 2:
                    break
                lines.append(line)
            else:
                empty_count = 0
                lines.append(line)

        return "\n".join(lines).strip()

    async def print_session(self, session: dict, show_full: bool = False):
        """Print a session summary or full details"""
        timestamp = session.get("timestamp", "")[:10]
        session_type = session.get("type", "unknown")
        question = session.get("question", "")[:50]
        rating = session.get("rating", "N/A")
        session_id = session.get("id", "")

        # Keep colors for ratings only
        if rating and rating != "N/A":
            if "No Hire" in rating or "No-Pass" in rating:
                rating_display = f"{Colors.RED}{rating}{Colors.RESET}"
            elif "Strong Hire" in rating or "Pass" in rating:
                rating_display = f"{Colors.GREEN}{rating}{Colors.RESET}"
            else:
                rating_display = f"{Colors.YELLOW}{rating}{Colors.RESET}"
        else:
            rating_display = rating

        print(f"[{session_id}] {timestamp} | {session_type:5} | {rating_display:20} | {question}...")

        if show_full:
            print(f"\nQuestion:")
            print(session.get("question", ""))

            # Show draft answer if exists (Story Builder flow)
            if session.get("draft_answer"):
                print(f"\nDraft Answer:")
                print(session.get("draft_answer", ""))
                print(f"\nImproved Answer:")
            else:
                print(f"\nAnswer:")
            print(session.get("answer", ""))

            # Check if session has follow-up evaluation
            if session.get("feedback_followup"):
                view_choice = (await self.prompt_session.prompt_async("\nView: 1. Original feedback  2. With follow-ups: ")).strip()
                if view_choice == "2":
                    if session.get("followup_qa"):
                        print(f"\nFollow-up Q&A:")
                        for i, (fq, fa) in enumerate(session["followup_qa"], 1):
                            print(f"\n  Q{i}: {fq}")
                            print(f"  A{i}: {fa}")
                    print(f"\nFeedback (with follow-ups):")
                    print(session.get("feedback_followup", ""))
                else:
                    print(f"\nFeedback:")
                    print(session.get("feedback", ""))
            else:
                print(f"\nFeedback:")
                print(session.get("feedback", ""))

            if session.get("red_flag_feedback"):
                print(f"\nRed Flag Analysis:")
                print(session.get("red_flag_feedback", ""))

    async def show_history(self, sessions: list):
        """Display a list of sessions"""
        if not sessions:
            print("No sessions found.")
            self.last_filtered_sessions = []
            return

        print(f"\nFound {len(sessions)} session(s):\n")
        for session in sessions:
            await self.print_session(session)

        self.last_filtered_sessions = sessions
        print(f"\n{Colors.DIM}  ⎿ Tip: /open <session_id> to view one, /open all to view all{Colors.RESET}")

    def show_stats(self):
        """Display practice statistics"""
        stats = self.storage.get_stats()

        self.print_header("Practice Statistics")

        if stats["total"] == 0:
            print("No practice sessions yet. Start practicing!")
            return

        print(f"Total sessions: {stats['total']}")
        print(f"  - Self-introductions: {stats.get('intro', 0)}")
        print(f"  - Behavioral questions: {stats.get('bq', 0)}")

        if stats.get("by_category"):
            print(f"\nBy Category:")
            for cat, count in stats["by_category"].items():
                print(f"  - {cat}: {count}")

        if stats.get("by_rating"):
            print(f"\nBy Rating:")
            for rating, count in stats["by_rating"].items():
                # Keep colors for ratings
                if "No Hire" in rating or "No-Pass" in rating:
                    color = Colors.RED
                elif "Strong Hire" in rating or "Pass" in rating:
                    color = Colors.GREEN
                else:
                    color = Colors.YELLOW
                print(f"  - {color}{rating}{Colors.RESET}: {count}")

    async def practice_self_intro(self):
        self.print_header(f"{Colors.BOLD}Self-Introduction Practice{Colors.RESET}")

        role = (await self.prompt_session.prompt_async("Enter job role (e.g., Software Engineer): ")).strip()
        if not role:
            role = "Software Engineer"

        company = (await self.prompt_session.prompt_async("Enter company (e.g., Meta): ")).strip()
        if not company:
            company = "Meta"

        introduction = await self.get_multiline_input("Enter your self-introduction:")

        if not introduction:
            print("No introduction provided. Returning to menu.")
            return

        BLUE = '\033[38;5;75m'
        print(f"\n{BLUE}Analyzing your introduction...{Colors.RESET}\n")

        result = await self.analyzer.analyze_introduction(
            introduction=introduction,
            role=role,
            company=company,
            stream=True
        )
        feedback = await Colors.stream_and_print(result)

        # Save session
        session_id = self.storage.save_session(
            session_type="intro",
            question="Self-Introduction",
            answer=introduction,
            feedback=feedback,
            role=role,
            company=company
        )
        print(f"\nSession saved (ID: {session_id})")

    async def practice_bq(self):
        self.print_header(f"{Colors.BOLD}Behavioral Question Practice{Colors.RESET}")

        # Select category
        categories = self.question_bank.get_categories()
        if not categories:
            print("No questions found in question bank.")
            return

        choice = await self.print_menu("Select a category:", categories)
        if choice < 1:
            return

        category = categories[choice - 1]

        # Select question
        questions = self.question_bank.get_questions(category)
        if not questions:
            print("No questions in this category.")
            return

        choice = await self.print_menu("Select a question:", questions)
        if choice < 1:
            return

        question = questions[choice - 1]

        # Select level
        levels = ["Junior-Mid", "Senior", "Staff"]
        choice = await self.print_menu("Select your level:", levels)
        if choice < 1:
            return

        level = levels[choice - 1]

        # Get answer
        print(f"\nQuestion:")
        print(f"{question}\n")

        answer = await self.get_multiline_input("Enter your answer:")

        if not answer:
            print("No answer provided. Returning to menu.")
            return

        # Select evaluation type
        eval_types = [
            "Full Interview Evaluation (with probing questions)",
            "Red Flag Detection Only",
            "Both (Full + Red Flags)"
        ]
        eval_choice = await self.print_menu("Select evaluation type:", eval_types)
        if eval_choice < 1:
            return

        BLUE = '\033[38;5;75m'
        print(f"\n{BLUE}Analyzing your answer...{Colors.RESET}\n")

        feedback = ""
        red_flag_feedback = ""

        if eval_choice in [1, 3]:
            self.print_header("Interview Evaluation")
            prompt = BQQuestions.real_interview(question, answer, level) + BQQuestions.bar_raiser(level)
            result = await self.analyzer.customized_analyze(prompt, stream=True)
            feedback = await Colors.stream_and_print(result)

        if eval_choice in [2, 3]:
            self.print_header("Red Flag Analysis")
            prompt = BQQuestions.red_flag(question, answer, level) + BQQuestions.bar_raiser(level)
            result = await self.analyzer.customized_analyze(prompt, stream=True)
            red_flag_feedback = await Colors.stream_and_print(result)

        # Follow-up questions flow
        feedback_followup = ""
        followup_qa = []
        original_answer = answer  # Save original answer before improvement

        if eval_choice in [1, 3] and feedback:
            # Extract probing questions from feedback
            probing_questions = FeedbackParser.extract_probing_questions(feedback)

            if probing_questions:
                print(f"\n{Colors.DIM}Found {len(probing_questions)} follow-up questions.{Colors.RESET}")
                followup_choice = (await self.prompt_session.prompt_async("\nWould you like to practice follow-up questions? (y/n): ")).strip().lower()

                if followup_choice == 'y':
                    # Extract original rating for calibration
                    original_rating = FeedbackParser.extract_rating(feedback) or "Unknown"

                    print(f"\n{Colors.DIM}  ⎿ Tip: Enter twice to skip question, /done to evaluate, /skip to skip all{Colors.RESET}\n")

                    skip_all = False
                    for i, fq in enumerate(probing_questions, 1):
                        print(f"\n{Colors.BOLD}Follow-up Question {i}/{len(probing_questions)}:{Colors.RESET}")
                        print(f"{fq}\n")

                        fa = await self.get_multiline_input("Your answer:")

                        if fa == '/done':
                            print("Ending follow-up questions.")
                            break
                        elif fa in ['/skip', '/question', '/q']:
                            print("Skipping follow-up questions.")
                            skip_all = True
                            break
                        elif not fa:
                            print("Skipped.")
                            continue
                        else:
                            followup_qa.append((fq, fa))

                    # Generate improved answer and re-evaluate if user answered any questions
                    if followup_qa and not skip_all:
                        BLUE = '\033[38;5;75m'

                        # Convert to dict format for improve_with_probing_answers
                        probing_qa_dicts = [{"q": fq, "a": fa} for fq, fa in followup_qa]

                        # Step 1: Rewrite the answer using user's probing answers
                        print(f"\n{BLUE}Rewriting your answer with the new details...{Colors.RESET}\n")
                        prompt = BQAnswer.improve_with_probing_answers(answer, feedback, probing_qa_dicts)
                        result = await self.analyzer.customized_analyze(prompt, stream=True)
                        improved_answer = await Colors.stream_and_print(result)

                        print(f"\n{Colors.BOLD}Improved Answer:{Colors.RESET}")
                        print("-" * 40)
                        print(improved_answer)
                        print("-" * 40)

                        # Step 2: Re-evaluate the improved answer
                        print(f"\n{BLUE}Re-evaluating improved answer...{Colors.RESET}\n")

                        self.print_header("Improved Answer Evaluation")
                        prompt = (
                            BQQuestions.real_interview(question, improved_answer, level, include_probing=False)
                            + BQQuestions.bar_raiser(level)
                            + BQQuestions.followup_calibration(original_rating)
                        )
                        result = await self.analyzer.customized_analyze(prompt, stream=True)
                        feedback_followup = await Colors.stream_and_print(result)

                        # Update answer to the improved version for saving
                        answer = improved_answer

        # Save session
        session_id = self.storage.save_session(
            session_type="bq",
            question=question,
            answer=answer,
            feedback=feedback or red_flag_feedback,
            category=category,
            level=level,
            red_flag_feedback=red_flag_feedback if eval_choice == 3 else None,
            feedback_followup=feedback_followup if feedback_followup else None,
            followup_qa=followup_qa if followup_qa else None,
            draft_answer=original_answer if original_answer != answer else None
        )
        print(f"\nSession saved (ID: {session_id})")

    def print_welcome(self):
        """Print welcome banner with ASCII art and tips"""
        BLUE = '\033[38;5;75m'
        LIGHT_GRAY = '\033[38;5;250m'
        RESET = '\033[0m'

        print()
        print(f"{BLUE} _____      _                  _                ______           {RESET}")
        print(f"{BLUE}|_   _|    | |                (_)               | ___ \\          {RESET}")
        print(f"{BLUE}  | | _ __ | |_ ___ _ ____   ___  _____      __ | |_/ /_ __ ___  {RESET}")
        print(f"{BLUE}  | || '_ \\| __/ _ \\ '__\\ \\ / / |/ _ \\ \\ /\\ / / | ___ \\ '__/ _ \\ {RESET}")
        print(f"{BLUE} _| || | | | ||  __/ |   \\ V /| |  __/\\ V  V /  | |_/ / | | (_) |{RESET}")
        print(f"{BLUE} \\___/_| |_|\\__\\___|_|    \\_/ |_|\\___| \\_/\\_/   \\____/|_|  \\___/ {RESET}")
        print()
        print(f"{LIGHT_GRAY}  Your AI buddy for crushing tech interviews{RESET}")
        print()
        print(f"{LIGHT_GRAY}  /question  Show practice menu{RESET}")
        print(f"{LIGHT_GRAY}  /history   View your history{RESET}")
        print(f"{LIGHT_GRAY}  /help      Show all commands{RESET}")
        print()
        print(f"{LIGHT_GRAY}  Local storage: ./history.json{RESET}")
        print()

    async def run(self):
        self.print_welcome()

        show_menu = True
        while True:
            options = [
                "Self-Introduction",
                "Behavioral Questions",
                "Build Story from Scratch"
            ]
            if show_menu:
                choice = await self.print_menu("What would you like to practice today?", options, show_commands=True)
            else:
                # Wait for command input without showing menu
                print(f"{Colors.DIM}  ⎿ Tap twice to go back to main menu{Colors.RESET}")
                empty_count = 0
                while True:
                    try:
                        line = await self.prompt_session.prompt_async("")
                    except (EOFError, KeyboardInterrupt):
                        choice = -1
                        break
                    if line.strip() == "":
                        empty_count += 1
                        if empty_count >= 2:
                            show_menu = True
                            break
                    elif line.strip().startswith("/"):
                        cmd = line.strip()[1:]  # Remove leading /
                        show_menu = await self.handle_command(cmd)
                        break
                    elif line.strip().lower() == "q":
                        choice = -1
                        break
                    else:
                        empty_count = 0
                continue

            if choice == -1:
                print("\nGood luck with your interviews!\n")
                break
            elif choice == -2:
                show_menu = True
                continue
            elif choice == -3:
                show_menu = False
                continue
            elif choice == 1:
                show_menu = True
                await self.practice_self_intro()
            elif choice == 2:
                show_menu = True
                await self.practice_bq()
            elif choice == 3:
                show_menu = True
                await self.build_story()

    async def build_story(self):
        """Build a BQ story from scratch, then hand off to Story Improver"""
        self.print_header(f"{Colors.BOLD}Build Story from Scratch{Colors.RESET}")

        builder = StoryBuilder()

        # Select category
        categories = sorted(builder.get_categories())
        choice = await self.print_menu("Select a category:", categories)
        if choice < 1:
            return
        category = categories[choice - 1]

        # Select sub-scenario
        sub_scenarios = builder.get_sub_scenarios(category)
        if not sub_scenarios:
            print("No sub-scenarios found.")
            return

        # Show sub-scenarios with descriptions
        print(f"\nSelect a scenario that sounds familiar to you:")
        for i, s in enumerate(sub_scenarios, 1):
            print(f"  {i}. {s['sub_scenario'].replace('_', ' ')}")
            print(f"     {Colors.DIM}{s['description']}{Colors.RESET}")

        while True:
            try:
                choice_str = (await self.prompt_session.prompt_async("\n> ")).strip()
            except (EOFError, KeyboardInterrupt):
                return
            if choice_str.lower() in ['q', '/q']:
                return
            if choice_str.isdigit():
                num = int(choice_str)
                if 1 <= num <= len(sub_scenarios):
                    break
            print("Please enter a number to select an option")

        selected = sub_scenarios[num - 1]
        builder.select_scenario(category, selected["sub_scenario"])

        # Get core STAR questions
        BLUE = '\033[38;5;75m'
        questions = builder.get_core_questions()

        print(f"Let's build your story. Answer these questions about your experience:")
        print(f"{Colors.DIM}  ⎿ Tip: Be specific - include names, numbers, timelines{Colors.RESET}\n")

        for i, q in enumerate(questions, 1):
            print(f"\n{Colors.BOLD}Q{i}: {q}{Colors.RESET}")
            answer = await self.get_multiline_input("")

            if answer in ['/q', '/skip']:
                print("Exiting story builder.")
                return
            if not answer:
                print("Skipped.")
                continue

            builder.add_response(q, answer)

        if not builder.user_responses:
            print("No responses provided. Returning to menu.")
            return

        # Generate draft
        print(f"\n{BLUE}Generating your initial story draft...{Colors.RESET}\n")
        draft = await builder.generate_draft()

        print(f"{Colors.BOLD}Your Draft Story:{Colors.RESET}")
        print("-" * 40)
        print(draft)
        print("-" * 40)

        # Ask if user wants to improve
        improve_choice = (await self.prompt_session.prompt_async(
            "\nWould you like to evaluate and improve this story? (y/n): "
        )).strip().lower()

        if improve_choice != 'y':
            # Save as-is
            session_id = self.storage.save_session(
                session_type="bq",
                question=builder.get_question(),
                answer=draft,
                feedback="(Draft - not evaluated)",
                category=category
            )
            print(f"\nDraft saved (ID: {session_id})")
            return

        # Hand off to Story Improver (existing BQ evaluation flow)
        question = builder.get_question()

        # Select level for evaluation
        levels = ["Junior-Mid", "Senior", "Staff"]
        choice = await self.print_menu("Select your level for evaluation:", levels)
        if choice < 1:
            return
        level = levels[choice - 1]

        print(f"\n{BLUE}Evaluating your story...{Colors.RESET}\n")

        # Strip STAR prefixes for evaluation (so LLM judges content, not formatting)
        draft_for_eval = strip_star_prefixes(draft)

        # Run full evaluation
        self.print_header("Interview Evaluation")
        prompt = self.bq.real_interview(question, draft_for_eval, level) + BQQuestions.bar_raiser(level)
        result = await self.analyzer.customized_analyze(prompt, stream=True)
        feedback = await Colors.stream_and_print(result)

        # Red flag check
        self.print_header("Red Flag Analysis")
        prompt = BQQuestions.red_flag(question, draft_for_eval, level) + BQQuestions.bar_raiser(level)
        result = await self.analyzer.customized_analyze(prompt, stream=True)
        red_flag_feedback = await Colors.stream_and_print(result)

        # Follow-up questions flow (same as practice_bq)
        feedback_followup = ""
        followup_qa = []
        original_draft = draft  # Save original draft before improvement

        probing_questions = FeedbackParser.extract_probing_questions(feedback)

        if probing_questions:
            print(f"\n{Colors.DIM}Found {len(probing_questions)} follow-up questions.{Colors.RESET}")
            followup_choice = (await self.prompt_session.prompt_async(
                "\nWould you like to answer follow-up questions to improve? (y/n): "
            )).strip().lower()

            if followup_choice == 'y':
                original_rating = FeedbackParser.extract_rating(feedback) or "Unknown"

                print(f"\n{Colors.DIM}  ⎿ Tip: Enter twice to skip, /done to evaluate{Colors.RESET}\n")

                for i, fq in enumerate(probing_questions, 1):
                    print(f"\n{Colors.BOLD}Follow-up {i}/{len(probing_questions)}:{Colors.RESET}")
                    print(f"{fq}\n")

                    fa = await self.get_multiline_input("Your answer:")

                    if fa == '/done':
                        break
                    elif fa in ['/skip', '/q']:
                        break
                    elif not fa:
                        continue
                    else:
                        followup_qa.append((fq, fa))

                if followup_qa:
                    # Convert to dict format for improve_with_probing_answers
                    probing_qa_dicts = [{"q": fq, "a": fa} for fq, fa in followup_qa]

                    # Step 1: Rewrite the answer using user's probing answers
                    print(f"\n{BLUE}Rewriting your story with the new details...{Colors.RESET}\n")
                    prompt = BQAnswer.improve_with_probing_answers(draft, feedback, probing_qa_dicts)
                    result = await self.analyzer.customized_analyze(prompt, stream=True)
                    improved_draft = await Colors.stream_and_print(result)

                    print(f"\n{Colors.BOLD}Improved Story:{Colors.RESET}")
                    print("-" * 40)
                    print(improved_draft)
                    print("-" * 40)

                    # Step 2: Re-evaluate the improved answer (strip STAR prefixes)
                    print(f"\n{BLUE}Re-evaluating improved story...{Colors.RESET}\n")

                    self.print_header("Improved Story Evaluation")
                    improved_for_eval = strip_star_prefixes(improved_draft)
                    prompt = (
                        BQQuestions.real_interview(question, improved_for_eval, level, include_probing=False)
                        + BQQuestions.bar_raiser(level)
                        + BQQuestions.followup_calibration(original_rating)
                    )
                    result = await self.analyzer.customized_analyze(prompt, stream=True)
                    feedback_followup = await Colors.stream_and_print(result)

                    # Update draft to the improved version for saving
                    draft = improved_draft

        # Save session
        session_id = self.storage.save_session(
            session_type="bq",
            question=question,
            answer=draft,
            feedback=feedback,
            category=category,
            level=level,
            red_flag_feedback=red_flag_feedback,
            feedback_followup=feedback_followup if feedback_followup else None,
            followup_qa=followup_qa if followup_qa else None,
            draft_answer=original_draft if original_draft != draft else None
        )
        print(f"\nSession saved (ID: {session_id})")


def parse_args():
    parser = argparse.ArgumentParser(description="Interview Practice CLI")
    parser.add_argument("--history", action="store_true", help="Show all practice history")
    parser.add_argument("--stats", action="store_true", help="Show practice statistics")
    parser.add_argument("--category", type=str, help="Filter history by category")
    parser.add_argument("--rating", type=str, help="Filter history by rating")
    parser.add_argument("--last", type=int, help="Show last N sessions")
    parser.add_argument("--search", type=str, help="Search sessions by question")
    parser.add_argument("--id", type=str, help="Show specific session by ID")
    return parser.parse_args()


async def main():
    args = parse_args()
    cli = InterviewCLI()

    # Handle command-line history queries
    if args.history:
        sessions = cli.storage.get_all_sessions()
        await cli.show_history(sessions)
    elif args.stats:
        cli.show_stats()
    elif args.category:
        sessions = cli.storage.get_sessions_by_category(args.category)
        await cli.show_history(sessions)
    elif args.rating:
        sessions = cli.storage.get_sessions_by_rating(args.rating)
        await cli.show_history(sessions)
    elif args.last:
        sessions = cli.storage.get_last_n_sessions(args.last)
        await cli.show_history(sessions)
    elif args.search:
        sessions = cli.storage.get_sessions_by_question(args.search)
        await cli.show_history(sessions)
    elif args.id:
        session = cli.storage.get_session_by_id(args.id)
        if session:
            await cli.print_session(session, show_full=True)
        else:
            print("Session not found.")
    else:
        # Interactive mode
        await cli.run()


if __name__ == "__main__":
    asyncio.run(main())
