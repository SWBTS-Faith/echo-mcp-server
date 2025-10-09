# Echo Prayer MCP Server

A prayer companion MCP server that provides guided prayers and semantic search capabilities with a readonly database.

## Features

### Prayer Tools (No Authentication Required)

- **One Minute Prayer**: Get a random prayer for quick spiritual connection
- **Guided Prayer Generator**: Find relevant prayers using semantic search
- **Pray Together**: Receive encouragement, condolences, and advice
- **Generate Prayer Request**: Create structured prayer requests based on topics
- **Browse Categories**: View all available prayer categories
- **Get Prayer by ID**: Retrieve a specific prayer by its ID
- **Get Prayers by Category**: View prayers from a specific category

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

**Note:** The server uses minimal dependencies for faster deployment:
- `fastmcp` - MCP server framework
- `uvicorn` - ASGI server
- `sentence-transformers` - Semantic search
- `numpy` - Required by sentence-transformers

2. Ensure the prayer database exists:
```bash
cd data/scripts
python create_database.py
```

3. Run the server:
```bash
python server.py
```

## Usage

### Basic Prayer Tools

#### One Minute Prayer
```python
# Get a random prayer for quick spiritual connection
result = await one_minute_prayer_tool()
```

#### Guided Prayer Generator
```python
# Search for prayers related to anxiety
result = await guided_prayer_generator_tool("anxiety", limit=3)

# Filter by specific category
result = await guided_prayer_generator_tool("healing", feed_title="Abiding & Presence")
```

#### Pray Together
```python
# Get encouragement
result = await pray_together_tool("encouragement")

# Get condolence message
result = await pray_together_tool("condolence")

# Get advice
result = await pray_together_tool("advice")
```

#### Generate Prayer Request
```python
# Create a prayer request for healing
result = await generate_prayer_request_tool("healing", "recovering from surgery")
```

#### Browse Categories
```python
# Get all available prayer categories
result = await get_available_categories_tool()
```

#### Get Prayer by ID
```python
# Get a specific prayer by its ID
result = await get_prayer_by_id_tool(prayer_id=1)
```

#### Get Prayers by Category
```python
# Get prayers from a specific category
result = await get_prayers_by_category_tool("Abiding & Presence", limit=5)
```

## Database Structure

The server uses a readonly SQLite database:

### Guided Prayers Database (`data/db/guided_prayers.db`)
- **guided_prayers** table with columns:
  - `id`: Primary key
  - `feed_title`: Prayer category
  - `prayer_title`: Prayer title
  - `prayer_description`: Prayer content
  - `prayer_steps`: Formatted prayer steps
  - `description_embedding`: Semantic embedding for search

## Semantic Search

The server uses the `all-MiniLM-L6-v2` sentence transformer model to generate embeddings for prayer descriptions, enabling intelligent semantic search. Users can find relevant prayers using natural language queries.

## Local Testing with MCP Clients

For local testing with MCP clients, use the provided `.mcp.json` configuration file:

```json
{
  "mcpServers": {
    "echo-prayer": {
      "command": "python",
      "args": ["server.py"],
      "cwd": "/Users/john/repos/echo-mcp-server",
      "env": {
        "PORT": "8000"
      },
      "description": "Echo Prayer MCP Server - A prayer companion with guided prayers and semantic search",
      "capabilities": {
        "tools": true,
        "resources": false,
        "prompts": false
      }
    }
  }
}
```

### Using with Claude Desktop

1. Copy the `.mcp.json` file to your Claude Desktop configuration directory:
   - **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

2. Restart Claude Desktop

3. The Echo Prayer MCP Server will be available as a tool in Claude Desktop

### Using with Other MCP Clients

The server exposes the following MCP tools:
- `one_minute_prayer_tool`
- `guided_prayer_generator_tool`
- `pray_together_tool`
- `generate_prayer_request_tool`
- `get_available_categories_tool`
- `get_prayer_by_id_tool`
- `get_prayers_by_category_tool`

## API Endpoints

- `GET /health`: Health check endpoint
- MCP tools are available through the FastMCP framework

## Environment Variables

- `PORT`: Server port (default: 8000)

## Deploy to Railway

This server includes Railway configuration for easy deployment:

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

Your MCP server will be available at the Railway-provided URL, and you can connect MCP clients using the Railway domain + `/mcp` endpoint.