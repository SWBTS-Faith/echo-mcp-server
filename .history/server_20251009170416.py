"""Echo Prayer MCP Server - A prayer companion with guided prayers, sharing, and community features"""
import os
import logging
import sys
import uvicorn
from starlette.responses import JSONResponse
from fastmcp import FastMCP
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.tools import (
    one_minute_prayer,
    guided_prayer_generator,
    pray_together,
    generate_prayer_request,
    authenticate_user,
    create_user_account,
    share_prayer,
    get_group_prayers,
    list_user_shared_prayers,
    list_prayers_shared_with_user,
    get_available_categories
)

# Enhanced logging configuration (cloud-compatible, no file logging)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s:%(funcName)s:%(lineno)d - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("mcp.server")

# Add error logger for critical issues
error_logger = logging.getLogger("mcp.server.errors")
error_logger.setLevel(logging.ERROR)
error_handler = logging.StreamHandler(sys.stderr)
error_handler.setFormatter(logging.Formatter(
    "%(asctime)s [%(levelname)s] %(name)s:%(funcName)s:%(lineno)d - %(message)s\n%(exc_info)s"
))
error_logger.addHandler(error_handler)

# Create the MCP server instance
mcp = FastMCP(
    name="Echo-Prayer-MCP-Server",
    instructions="""
        Echo Prayer MCP Server provides a comprehensive prayer companion experience with:
        
        Basic Prayer Tools (No Authentication Required):
        - One-minute prayers for quick spiritual connection
        - Guided prayer generator with semantic search
        - Pray together with encouragement, condolences, and advice
        - Generate prayer requests based on topics
        - Browse available prayer categories
        
        Authenticated Prayer Sharing Features:
        - Share prayers privately with specific users or publicly with groups
        - Access prayers shared with you from groups
        - List all prayers you've shared with timestamps
        - List all prayers shared with you by others
        
        The server uses semantic search powered by sentence transformers to find 
        relevant prayers based on natural language queries. All prayer data comes 
        from a curated database of guided prayers with embeddings for intelligent matching.
        
        Authentication is required for sharing features. Use authenticate_user or 
        create_user_account to get started with authenticated features.
    """
)

# Basic Prayer Tools (No Authentication Required)

@mcp.tool()
async def one_minute_prayer_tool():
    """Generate a one-minute prayer for quick spiritual connection.
    
    Returns a random prayer from the database suitable for a quick prayer moment.
    Perfect for when you need immediate spiritual connection or guidance.
    """
    return await one_minute_prayer()

@mcp.tool()
async def guided_prayer_generator_tool(query: str, feed_title: str = None, limit: int = 3):
    """Generate guided prayers based on semantic search of the database.
    
    Args:
        query: Search query to find relevant prayers (e.g., "anxiety", "healing", "gratitude")
        feed_title: Optional filter by specific prayer category (e.g., "Abiding & Presence")
        limit: Maximum number of prayers to return (default: 3)
    
    Returns list of relevant prayers based on the search query using semantic similarity.
    """
    return await guided_prayer_generator(query, feed_title, limit)

@mcp.tool()
async def pray_together_tool(message_type: str = "encouragement"):
    """Provide encouragement, condolences, and advice for prayer support.
    
    Args:
        message_type: Type of message - "encouragement", "condolence", or "advice"
    
    Returns a supportive message with prayer guidance and suggestions.
    """
    return await pray_together(message_type)

@mcp.tool()
async def generate_prayer_request_tool(topic: str, details: str = None):
    """Generate a prayer request based on the topic and details provided.
    
    Args:
        topic: The main topic or situation for the prayer request (e.g., "healing", "job search")
        details: Optional additional details about the situation
    
    Returns a structured prayer request with suggested prayers from the database.
    """
    return await generate_prayer_request(topic, details)

@mcp.tool()
async def get_available_categories_tool():
    """Get all available prayer categories/feed titles.
    
    Returns a list of all prayer categories available in the database.
    Use this to see what prayer topics are available for filtering.
    """
    return await get_available_categories()

# Authentication Tools

@mcp.tool()
async def authenticate_user_tool(username: str, password: str):
    """Authenticate a user with username and password.
    
    Args:
        username: User's username
        password: User's password
    
    Returns authentication result with access token if successful.
    Required for accessing prayer sharing features.
    """
    return await authenticate_user(username, password)

@mcp.tool()
async def create_user_account_tool(username: str, password: str, email: str = None):
    """Create a new user account.
    
    Args:
        username: Desired username
        password: User's password
        email: Optional email address
    
    Returns account creation result.
    """
    return await create_user_account(username, password, email)

# Authenticated Prayer Sharing Tools

@mcp.tool()
async def share_prayer_tool(token: str, prayer_id: int, share_type: str, 
                          shared_with_user_id: int = None, 
                          shared_with_group: str = None):
    """Share a prayer with another user or group (requires authentication).
    
    Args:
        token: User's authentication token (from authenticate_user_tool)
        prayer_id: ID of the prayer to share (get from guided_prayer_generator_tool)
        share_type: "private" or "public"
        shared_with_user_id: ID of user to share with (for private shares)
        shared_with_group: Group name to share with (for public shares)
    
    Returns share operation result.
    """
    return await share_prayer(token, prayer_id, share_type, shared_with_user_id, shared_with_group)

@mcp.tool()
async def get_group_prayers_tool(token: str, group_name: str = None):
    """Access prayers from a certain group (requires authentication).
    
    Args:
        token: User's authentication token
        group_name: Optional specific group name to filter by
    
    Returns list of prayers shared with the user or in public groups.
    """
    return await get_group_prayers(token, group_name)

@mcp.tool()
async def list_user_shared_prayers_tool(token: str):
    """List all prayers that were shared by the user (requires authentication).
    
    Args:
        token: User's authentication token
    
    Returns list of prayers shared by the authenticated user with timestamps.
    """
    return await list_user_shared_prayers(token)

@mcp.tool()
async def list_prayers_shared_with_user_tool(token: str):
    """List all prayers that are shared to the user (requires authentication).
    
    Args:
        token: User's authentication token
    
    Returns list of prayers shared with the authenticated user by others.
    """
    return await list_prayers_shared_with_user(token)

@mcp.custom_route("/health", methods=["GET"])
async def health_check(request):
    # TODO: Update the service name in the response
    return JSONResponse({"status": "healthy", "service": "my-mcp-server"})

# Create ASGI app from MCP server
mcp_app = mcp.http_app(transport="streamable-http")

# Create a main FastAPI app that includes both MCP routes and root health endpoint
# TODO: Update the title to match your server name
app = FastAPI(title="My MCP Server", lifespan=mcp_app.lifespan)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# # Mount MCP routes under /mcp
app.mount("/", mcp_app)

# Root health endpoint for Railway
# TODO: Update the service name in the response
@app.get("/health")
async def root_health_check():
    return {"status": "healthy", "service": "my-mcp-server"}

if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))