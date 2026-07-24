"""Echo Prayer MCP Server - A prayer companion with guided prayers and semantic search"""
import os
import logging
import sys
import uvicorn
from fastmcp import FastMCP
from src.tools import (
    one_minute_prayer,
    guided_prayer_generator,
    pray_together,
    generate_prayer_request,
    get_available_categories,
    get_prayer_by_id,
    get_prayers_by_category
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
        
        Prayer Tools (Readonly Database):
        - One-minute prayers for quick spiritual connection
        - Guided prayer generator with semantic search
        - Pray together with encouragement, condolences, and advice
        - Generate prayer requests based on topics
        - Browse available prayer categories
        - Get specific prayers by ID
        - Get prayers by category
        
        The server uses semantic search powered by sentence transformers to find 
        relevant prayers based on natural language queries. All prayer data comes 
        from a curated database of guided prayers with embeddings for intelligent matching.
        
        No authentication required - all tools are available for immediate use.
    """
)

# Prayer Tools (Readonly Database)

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

@mcp.tool()
async def get_prayer_by_id_tool(prayer_id: int):
    """Get a specific prayer by its ID.
    
    Args:
        prayer_id: The ID of the prayer to retrieve
    
    Returns the prayer details if found.
    """
    return await get_prayer_by_id(prayer_id)

@mcp.tool()
async def get_prayers_by_category_tool(feed_title: str, limit: int = 10):
    """Get prayers from a specific category.
    
    Args:
        feed_title: The category/feed title to filter by
        limit: Maximum number of prayers to return (default: 10)
    
    Returns list of prayers from the specified category.
    """
    return await get_prayers_by_category(feed_title, limit)

# Add health check endpoint
@mcp.custom_route("/health", methods=["GET"])
async def health_check(request):
    return {"status": "healthy", "service": "echo-prayer-mcp-server"}

# Create ASGI app from MCP server
app = mcp.http_app(transport="streamable-http")

if __name__ == "__main__":
    # Use uvicorn to run the FastMCP app
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))