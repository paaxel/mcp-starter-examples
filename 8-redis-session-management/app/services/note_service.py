"""Business logic for note management. Notes are scoped to a session created with create_session."""
from typing import Tuple

from fastmcp.server.sessions import Session

NOTES_STATE_KEY = "notes"


class NoteService:
    """Service class for managing notes. Notes are kept in the state of the given session."""

    @staticmethod
    async def read_notes(session: Session) -> list[str]:
        """Return the notes of the session in insertion order."""
        return list(await session.get(NOTES_STATE_KEY) or [])

    @staticmethod
    async def write_notes(session: Session, notes: list[str]) -> None:
        """Replace the notes of the session."""
        await session.set(NOTES_STATE_KEY, notes)

    @staticmethod
    async def store_note(session: Session, note: str) -> Tuple[bool, str]:
        """
        Store a new note in the session.

        Args:
            note: The note to store.

        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            notes = await NoteService.read_notes(session)
            notes.append(note)
            await NoteService.write_notes(session, notes)
            return True, "Note stored successfully."
        except Exception as e:
            return False, f"Error storing note: {str(e)}"

    @staticmethod
    async def get_all_notes(session: Session) -> str:
        """
        Retrieve all notes of the session.

        Returns:
            String containing all notes
        """
        try:
            notes = await NoteService.read_notes(session)
            if not notes:
                return "No notes found. The notes are empty."

            return "All Stored Notes:\n\n" + "\n".join(notes)
        except Exception as e:
            return f"Error retrieving notes: {str(e)}"

    @staticmethod
    async def read_notes_content(session: Session) -> str:
        """
        Read all notes of the session as a single text block.

        Returns:
            String containing the notes, one per line, or empty string if there are none
        """
        try:
            return "\n".join(await NoteService.read_notes(session))
        except Exception as e:
            raise Exception(f"Error retrieving notes: {str(e)}")

    @staticmethod
    async def delete_all_notes(session: Session) -> dict:
        """
        Delete all notes of the session.

        Returns:
            Dictionary with status and message
        """
        try:
            await NoteService.write_notes(session, [])

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
    async def delete_notes_containing(session: Session, contained_text: str) -> dict:
        """
        Delete all notes of the session that contain the given text.

        Args:
            contained_text: Text to search for in notes

        Returns:
            Dictionary with status, deleted count, and message
        """
        try:
            notes = await NoteService.read_notes(session)
            remaining = [note for note in notes if contained_text not in note]
            deleted_count = len(notes) - len(remaining)

            await NoteService.write_notes(session, remaining)

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
