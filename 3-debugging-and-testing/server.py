import os
from http.client import HTTPException

import uvicorn
from fastmcp import FastMCP
from starlette.middleware.cors import CORSMiddleware

HOST = os.getenv("MCP_HOST", "127.0.0.1")
PORT = int(os.getenv("MCP_PORT", "8000"))
FILE_PATH = 'c:/PersonalNoteManagerStorage/notes.txt'

mcp = FastMCP(name="PersonalNoteManager")

@mcp.tool(description="Store a note in the personal note system")
def store_note(note: str) -> (bool, str):
    """
    Store a new note in the personal note system.

    Args:
        note (str): The note to store.

    Returns:
        (bool, str): True and success message if stored, False and error message otherwise.
    """
    try:
        os.makedirs(os.path.dirname(FILE_PATH), exist_ok=True)
        with open(FILE_PATH, "a", encoding="utf-8") as f:
            f.write(note + "\n")
        return True, "Note stored successfully."
    except Exception as e:
        return False, f"Error storing note: {str(e)}"


@mcp.resource("notes://all", description="Return all notes stored in personal note system")
def get_all_notes() -> str:
    """
    Retrieve all stored notes from the notes file.

    Returns:
        String containing all notes with their timestamps
    """
    try:
        if not os.path.exists(FILE_PATH):
            return "No notes found. The notes file doesn't exist yet."

        with open(FILE_PATH, 'r', encoding='utf-8') as f:
            content = f.read()

        if not content.strip():
            return "No notes found. The notes file is empty."

        return f"All Stored Notes:\n\n{content}"
    except Exception as e:
        return f"Error retrieving notes: {str(e)}"


@mcp.prompt(name="Analyze notes", description="Analyze notes and return them as a classified list based on urgency and deadlines")
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
    return """Considering the notes present in the resource, classify them in specific classes:

            1. URGENT - contains "urgent", "asap", "critical", "emergency"
            2. WITH DEADLINES - mentions dates or "today", "tomorrow", "week", "month"
            3. MEETING - contains "meeting", "call", "review", "report"
            4. PERSONAL - personal tasks and reminders
            5. OTHER - everything else
            
            Show each priority level as a section with bullet points.
            """




class OriginValidationMiddleware:
    def __init__(self, app, allowed_origins):
        self.app = app
        self.allowed_origins = set(allowed_origins)

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            headers = dict(scope["headers"])
            origin = headers.get(b"origin", b"").decode("utf-8").lower()

            # Reject if Origin present but not allowed (DNS rebinding protection)
            if origin and origin not in self.allowed_origins:
                raise HTTPException(403, "Invalid Origin")

        await self.app(scope, receive, send)


if __name__ == "__main__":
    app = mcp.http_app(stateless_http=True)

    ALLOWED_ORIGINS = [
        "http://localhost:6274"
    ]

    # Custom Origin validation FIRST (before CORS)
    # Executed at each request on the backend side
    app.add_middleware(OriginValidationMiddleware, allowed_origins=ALLOWED_ORIGINS)

    # Then CORS for legitimate requests
    app.add_middleware(
        CORSMiddleware,
        allow_origins=ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"]
    )

    uvicorn.run(app, host=HOST, port=PORT)