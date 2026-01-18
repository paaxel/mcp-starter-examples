import os

import uvicorn
from fastmcp import FastMCP

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

if __name__ == "__main__":
    uvicorn.run(mcp.http_app(), host=HOST, port=PORT)