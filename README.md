# MCP Server Template

A template for creating Model Context Protocol (MCP) servers in Python, deployable via Railway. This template provides a basic structure that you can customize by swapping out the functions in `src/tools.py` and updating references in `server.py`.

## Getting Started

### 1. Clone and Setup

```bash
git clone <your-repo-url>
cd mcp-server-template
uv sync  # or pip install -e .
```

### 2. Customize Your Tools

Replace the example functions in `src/tools.py` with your own MCP tools:

```python
# Replace this:
async def template_function(input: dict):
    """Generate a template function - a template function for any platform."""
    return await utility_function()

# With your own functions:
async def my_custom_tool(input: dict):
    """Description of what your tool does."""
    # Your implementation here
    pass
```

### 3. Update Server Configuration

Update `server.py` to register your new tools and customize the server name/instructions:

```python
# Change the server name and instructions
mcp = FastMCP(
    name="My-Custom-MCP",  # Change this
    instructions="""
        Description of what your MCP server does.
    """
)

# Update the tool registration
@mcp.tool()
async def my_custom_tool(input: dict):  # Update function name
    """Tool description and documentation."""
    return await my_custom_function(input)  # Update function call
```

### 4. Update Project Metadata

Update `pyproject.toml` with your project details:

```toml
[project]
name = "my-mcp-server"  # Change this
description = "Description of your MCP server"  # Change this
```

## Build

Install dependencies with `uv` (preferred) or `pip`:

```bash
uv sync

# or

pip install -e .
```

## Run (Uvicorn Deployment)

Start the API server with Uvicorn:

```bash
uvicorn server:app --host 0.0.0.0 --port 8000
```

And then, if testing via MCP inspector, connect with a proxy via streamable-http at:
```
http://0.0.0.0:8000/mcp
```

## Deploy to Railway

This template includes Railway configuration for easy deployment (Python-only, no Node.js required):

1. **Set up environment variables**: Copy `env.example` to `.env` and add your API keys:
   ```bash
   cp env.example .env
   # Edit .env with your API keys
   ```

2. **Initialize Git repository** (if not already done):
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   ```

3. **Push to GitHub**: Create a new repository on GitHub and push your code:
   ```bash
   git remote add origin https://github.com/yourusername/your-repo-name.git
   git push -u origin main
   ```

4. **Deploy on Railway**:
   - Sign in to [Railway](https://railway.app/) and create a new project
   - Choose "Deploy from GitHub repo" and select your repository
   - Railway will automatically detect your Python application and deploy it

The `railway.json` configuration includes:
- Automatic dependency installation via `uv sync --frozen` using `pyproject.toml`
- Uvicorn server startup via `uv run` on Railway's assigned port
- Health check endpoint monitoring at `/health`
- Automatic restarts on failure (up to 10 retries)

Your MCP server will be available at the Railway-provided URL, and you can connect MCP clients using the Railway domain + `/mcp` endpoint.
