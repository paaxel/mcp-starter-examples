from fastmcp import Context, FastMCP
from fastmcp.server.elicitation import (
    AcceptedElicitation,
    DeclinedElicitation,
    CancelledElicitation,
)
from app.services.note_service import NoteService
from app.security.auth import has_role


def register_routes(mcp: FastMCP):
    """
    Register all MCP routes (tools, resources, prompts) with the FastMCP instance.

    Args:
        mcp: FastMCP instance
    """

    @mcp.tool(
        description="Store a note in the personal note system",
        auth=has_role("mcp_write")
    )
    def store_note(note: str) -> tuple:
        """
        Store a new note in the personal note system.

        Args:
            note (str): The note to store.

        Returns:
            (bool, str): True and success message if stored, False and error message otherwise.
        """
        return NoteService.store_note(note)

    @mcp.resource(
        "notes://all",
        description="Return all notes stored in personal note system",
        auth=has_role("mcp_read")
    )
    def get_all_notes() -> str:
        """
        Retrieve all stored notes from the notes file.

        Returns:
            String containing all notes with their timestamps
        """
        return NoteService.get_all_notes()

    @mcp.prompt(
        name="Analyze notes",
        description="Analyze notes and return them as a classified list based on urgency and deadlines",
        auth=has_role("mcp_read")
    )
    def classify_notes_prompt() -> str:
        """
        Generate a prompt with the goal of classifying them by category.

        This prompt instructs the AI to:
        1. Access the notes resource
        2. Analyze the content for classification indicators
        3. Return a classified list

        Returns:
            String containing the prompt instructions
        """
        return NoteService.get_classification_prompt()

    @mcp.tool(
        description="Analyze notes and return them as a classified list based on urgency and deadlines",
        auth=has_role("mcp_read")
    )
    async def classify_stored_notes(ctx: Context) -> str:
        """
        Classifies stored notes into categories: URGENT, WITH DEADLINES, MEETING, PERSONAL, OTHER
        """
        try:
            notes_content = NoteService.read_notes_content()
        except Exception as e:
            return str(e)

        if not notes_content or notes_content.strip() == '':
            return "Your notes are empty."

        message = NoteService.build_classification_message(notes_content)

        sampling_result = await ctx.sample(
            messages=message,
            max_tokens=1000,
            temperature=0.2
        )

        return sampling_result.text

    @mcp.tool(
        description="Delete all stored notes in the personal note system",
        auth=has_role("mcp_delete")
    )
    async def delete_all_notes(ctx: Context) -> dict:
        """
        Delete all notes after user confirmation.

        Args:
            ctx: MCP context for elicitation

        Returns:
            Dictionary with status and message
        """
        result = await ctx.elicit(
            "Are you sure you want to delete ALL notes?",
            response_type=bool,
        )

        if result.action == "accept":
            confirmed = result.data

            if confirmed is True:
                return NoteService.delete_all_notes()
            elif confirmed is False:
                return {
                    "status": "cancelled",
                    "message": "Deletion not confirmed by user.",
                }

        if result.action == "decline":
            return {
                "status": "cancelled",
                "message": "Deletion declined by user.",
            }

        elif result.action == "cancel":
            return {
                "status": "cancelled",
                "message": "Deletion cancelled by user.",
            }
        else:
            return {
                "status": "error",
                "message": "Invalid confirmation response.",
            }

    @mcp.tool(
        description="Delete notes, stored in the personal note system, that contains specific text",
        auth=has_role("mcp_delete")
    )
    async def delete_note(contained_text: str, ctx: Context) -> dict:
        """
        Delete all notes that contain the given text.

        Args:
            contained_text: Text to search for in notes to delete
            ctx: MCP context for elicitation

        Returns:
            Dictionary with status and message
        """
        # Ask for confirmation
        result = await ctx.elicit(
            message=f"Are you sure you want to delete all notes containing: '{contained_text}'?",
            response_type=bool,
        )

        match result:
            case AcceptedElicitation():
                confirmed = result.data

                if confirmed is True:
                    return NoteService.delete_notes_containing(contained_text)
                else:
                    return {
                        "status": "cancelled",
                        "message": "Deletion declined by user.",
                    }

            case DeclinedElicitation():
                return {
                    "status": "cancelled",
                    "message": "Deletion declined by user.",
                }

            case CancelledElicitation():
                return {
                    "status": "cancelled",
                    "message": "Deletion cancelled by user.",
                }