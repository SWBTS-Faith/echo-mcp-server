"""Tools for the Template Agent"""
import os
import logging
import sys
import uvicorn
from starlette.responses import JSONResponse
from fastmcp import FastMCP
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.tools import template_function

# Enhanced logging configuration (cloud-compatible, no file logging)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s:%(funcName)s:%(lineno)d - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("venture.server")

# Add error logger for critical issues
error_logger = logging.getLogger("venture.server.errors")
error_logger.setLevel(logging.ERROR)
error_handler = logging.StreamHandler(sys.stderr)
error_handler.setFormatter(logging.Formatter(
    "%(asctime)s [%(levelname)s] %(name)s:%(funcName)s:%(lineno)d - %(message)s\n%(exc_info)s"
))
error_logger.addHandler(error_handler)

# Create the MCP server instance
mcp = FastMCP(
    name="Template-MCP",
    instructions="""
        This server provides a template of tools for any platform.
    """
)

@mcp.tool()
async def template_function_tool(input: dict):
    """Generate a template function - a template function for any platform.

    Creates a template function for any platform.

    Enhanced with Perplexity AI research to provide more informed, relevant template functions with
    optional URL references to helpful resources and insights.

    Args:
        input: Information about the user including background and preferences.

    Returns:
        Dict 
    """
    return await template_function(input)

@mcp.custom_route("/health", methods=["GET"])
async def health_check(request):
    return JSONResponse({"status": "healthy", "service": "template-mcp-server"})

# Create ASGI app from MCP server
mcp_app = mcp.http_app(transport="streamable-http")

# Create a main FastAPI app that includes both MCP routes and root health endpoint
app = FastAPI(title="Template MCP Server", lifespan=mcp_app.lifespan)

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

# # Root health endpoint for Railway
@app.get("/health")
async def root_health_check():
    return {"status": "healthy", "service": "template-mcp-server"}

if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))