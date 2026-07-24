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
# TODO: Update the name and instructions for your specific MCP server
mcp = FastMCP(
    name="My-MCP-Server",  # Change this to your server name
    instructions="""
        Replace this with instructions describing what your MCP server does.
        This will help AI clients understand how to use your tools effectively.
    """
)

# TODO: Replace this example tool with your own MCP tools
@mcp.tool()
async def example_tool(input: dict):
    """Example MCP tool - replace this with your own tool.

    This is a template tool that demonstrates how to create MCP tools.
    Replace this function with your own tools and update the function name,
    docstring, and implementation.

    Args:
        input: Input parameters for your tool.

    Returns:
        Tool result - customize this return type for your needs.
    """
    # TODO: Replace this call with your actual tool implementation
    return await example_function(input)

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