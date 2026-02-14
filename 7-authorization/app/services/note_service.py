"""Business logic for note management operations."""
import os
from typing import Tuple
from app.config import Config


class NoteService:
    """Service class for managing notes."""

    @staticmethod
    def store_note(note: str) -> Tuple[bool, str]:
        """
        Store a new note in the personal note system.

        Args:
            note: The note to store.

        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            os.makedirs(os.path.dirname(Config.FILE_PATH), exist_ok=True)
            with open(Config.FILE_PATH, "a", encoding="utf-8") as f:
                f.write(note + "\n")
            return True, "Note stored successfully."
        except Exception as e:
            return False, f"Error storing note: {str(e)}"

    @staticmethod
    def get_all_notes() -> str:
        """
        Retrieve all stored notes from the notes file.

        Returns:
            String containing all notes with their timestamps
        """
        try:
            if not os.path.exists(Config.FILE_PATH):
                return "No notes found. The notes file doesn't exist yet."

            with open(Config.FILE_PATH, 'r', encoding='utf-8') as f:
                content = f.read()

            if not content.strip():
                return "No notes found. The notes file is empty."

            return f"All Stored Notes:\n\n{content}"
        except Exception as e:
            return f"Error retrieving notes: {str(e)}"

    @staticmethod
    def read_notes_content() -> str:
        """
        Read the raw content of notes file.

        Returns:
            String containing the notes content or empty string if file doesn't exist
        """
        try:
            if os.path.exists(Config.FILE_PATH):
                with open(Config.FILE_PATH, 'r', encoding='utf-8') as f:
                    return f.read()
        except Exception as e:
            raise Exception(f"Error retrieving notes: {str(e)}")

        return ""

    @staticmethod
    def delete_all_notes() -> dict:
        """
        Delete all notes from the file.

        Returns:
            Dictionary with status and message
        """
        try:
            if os.path.exists(Config.FILE_PATH):
                with open(Config.FILE_PATH, "w", encoding="utf-8"):
                    pass

            return {
                "status": "success",
                "message": "All notes have been deleted.",
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to delete notes: {str(e)}",
            }

    @staticmethod
    def delete_notes_containing(contained_text: str) -> dict:
        """
        Delete all notes that contain the given text.

        Args:
            contained_text: Text to search for in notes

        Returns:
            Dictionary with status, deleted count, and message
        """
        try:
            if not os.path.exists(Config.FILE_PATH):
                return {
                    "status": "success",
                    "message": "No notes file found. Nothing to delete.",
                }

            with open(Config.FILE_PATH, "r", encoding="utf-8") as f:
                lines = f.readlines()

            # Keep only lines that DO NOT contain the text
            remaining_lines = [
                line for line in lines if contained_text not in line
            ]

            deleted_count = len(lines) - len(remaining_lines)

            with open(Config.FILE_PATH, "w", encoding="utf-8") as f:
                f.writelines(remaining_lines)

            return {
                "status": "success",
                "deleted": deleted_count,
                "message": f"Deleted {deleted_count} note(s) containing '{contained_text}'.",
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to delete notes: {str(e)}",
            }

    @staticmethod
    def get_classification_prompt() -> str:
        """
        Get the prompt for classifying notes.

        Returns:
            String containing the classification prompt
        """
        return """Considering the notes present in the resource, classify them in specific classes:

            1. URGENT - contains "urgent", "asap", "critical", "emergency"
            2. WITH DEADLINES - mentions dates or "today", "tomorrow", "week", "month"
            3. MEETING - contains "meeting", "call", "review", "report"
            4. PERSONAL - personal tasks and reminders
            5. OTHER - everything else

            Show each priority level as a section with bullet points.
            """

    @staticmethod
    def build_classification_message(notes_content: str) -> str:
        """
        Build the classification message with notes content.

        Args:
            notes_content: The content of the notes to classify

        Returns:
            Formatted message for AI classification
        """
        return f"""Considering the notes present in the resource, classify them in specific classes:

            1. URGENT - contains "urgent", "asap", "critical", "emergency"
            2. WITH DEADLINES - mentions dates or "today", "tomorrow", "week", "month"
            3. MEETING - contains "meeting", "call", "review", "report"
            4. PERSONAL - personal tasks and reminders
            5. OTHER - everything else

            Show each priority level as a section with bullet points.
            ------------
            DATA TO PROCESS:\n{notes_content}
        """