from fastmcp import Context, FastMCP
from fastmcp.server.dependencies import get_session
from fastmcp.server.sessions import SessionId
from mcp.types import (
    CreateMessageRequest,
    CreateMessageRequestParams,
    CreateMessageResult,
    ElicitRequest,
    ElicitRequestFormParams,
    InputRequiredResult,
    SamplingMessage,
    TextContent,
)

from app.services.note_service import NoteService


def confirm(key: str, message: str) -> InputRequiredResult:
    """Ask the user for a yes/no confirmation on the next round."""
    params = ElicitRequestFormParams(
        message=message,
        requested_schema={
            "type": "object",
            "properties": {"confirm": {"type": "boolean"}},
            "required": ["confirm"],
        },
    )
    return InputRequiredResult(
        result_type="input_required",
        input_requests={key: ElicitRequest(method="elicitation/create", params=params)},
    )


def not_confirmed(answer) -> dict | None:
    """Return a cancellation result unless the user explicitly confirmed."""
    if answer.action == "decline":
        return {"status": "cancelled", "message": "Deletion declined by user."}
    if answer.action == "cancel":
        return {"status": "cancelled", "message": "Deletion cancelled by user."}
    if answer.action != "accept" or not answer.content or answer.content.get("confirm") is not True:
        return {"status": "cancelled", "message": "Deletion not confirmed by user."}
    return None


def register_note_routes(mcp: FastMCP):
    """Register the note tools, resource and prompt."""

    @mcp.tool(description="Store a note in the session identified by session_id")
    async def store_note(note: str, session_id: SessionId) -> tuple:
        """
        Store a new note in the session.

        Args:
            note (str): The note to store.
            session_id: Id returned by create_session.

        Returns:
            (bool, str): True and success message if stored, False and error message otherwise.
        """
        session = await get_session(session_id)
        return await NoteService.store_note(session, note)

    @mcp.tool(description="Return all notes stored in the session identified by session_id")
    async def get_all_notes(session_id: SessionId) -> str:
        """
        Retrieve all notes of the session.

        Returns:
            String containing all notes
        """
        session = await get_session(session_id)
        return await NoteService.get_all_notes(session)

    @mcp.prompt(
        name="Analyze notes",
        description="Analyze notes and return them as a classified list based on urgency and deadlines",
    )
    def classify_notes_prompt() -> str:
        """
        Generate a prompt with the goal of classifying them by category.

        Returns:
            String containing the prompt instructions
        """
        return NoteService.get_classification_prompt()

    @mcp.tool(
        description="Analyze notes and return them as a classified list based on urgency and deadlines",
    )
    async def classify_stored_notes(session_id: SessionId, ctx: Context) -> str | InputRequiredResult:
        """
        Classifies stored notes into categories: URGENT, WITH DEADLINES, MEETING, PERSONAL, OTHER.

        The model is borrowed from the caller: the first round asks the client to
        run a completion, the second round returns its answer.
        """
        try:
            session = await get_session(session_id)
            notes_content = await NoteService.read_notes_content(session)
        except Exception as e:
            return str(e)

        if not notes_content or notes_content.strip() == '':
            return "Your notes are empty."

        responses = ctx.input_responses
        if responses is None:
            message = NoteService.build_classification_message(notes_content)
            return InputRequiredResult(
                result_type="input_required",
                input_requests={
                    "classification": CreateMessageRequest(
                        method="sampling/createMessage",
                        params=CreateMessageRequestParams(
                            messages=[
                                SamplingMessage(
                                    role="user",
                                    content=TextContent(type="text", text=message),
                                )
                            ],
                            max_tokens=1000,
                            temperature=0.2,
                        ),
                    )
                },
            )

        answer = responses["classification"]
        if isinstance(answer, CreateMessageResult) and isinstance(answer.content, TextContent):
            return answer.content.text
        return "The client returned no classification."

    @mcp.tool(description="Delete all stored notes in the personal note system")
    async def delete_all_notes(session_id: SessionId, ctx: Context) -> dict | InputRequiredResult:
        """
        Delete all notes after user confirmation.

        Returns:
            Dictionary with status and message, or an input request asking for confirmation
        """
        responses = ctx.input_responses
        if responses is None:
            return confirm("confirm", "Are you sure you want to delete ALL notes?")

        cancelled = not_confirmed(responses["confirm"])
        if cancelled is not None:
            return cancelled
        session = await get_session(session_id)
        return await NoteService.delete_all_notes(session)

    @mcp.tool(description="Delete notes, stored in the personal note system, that contains specific text")
    async def delete_note(contained_text: str, session_id: SessionId, ctx: Context) -> dict | InputRequiredResult:
        """
        Delete all notes that contain the given text, after user confirmation.

        Args:
            contained_text: Text to search for in notes to delete
            ctx: MCP context used to read the confirmation answer

        Returns:
            Dictionary with status and message, or an input request asking for confirmation
        """
        responses = ctx.input_responses
        if responses is None:
            return confirm(
                "confirm",
                f"Are you sure you want to delete all notes containing: '{contained_text}'?",
            )

        cancelled = not_confirmed(responses["confirm"])
        if cancelled is not None:
            return cancelled
        session = await get_session(session_id)
        return await NoteService.delete_notes_containing(session, contained_text)
