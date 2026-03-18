# SupportBot

AI-powered customer support chatbot with a configurable knowledge base and an embeddable widget you can drop into any website with one script tag.

![SupportBot Screenshot](static/screenshot.png)
<!-- Replace with actual screenshot -->

## Features

- **Embeddable Widget** -- Add AI support to any website with a single `<script>` tag
- **Custom Knowledge Base** -- Feed it your FAQs, docs, or product info for grounded answers
- **Configurable Personality** -- Set the bot's tone, business name, and branding color
- **Conversation History** -- Maintains context across messages (up to 20 turns)
- **Human Handoff** -- Automatically suggests connecting to a human when uncertain
- **No Hallucination** -- Won't make up policies, prices, or details not in the knowledge base
- **Dark Mode UI** -- Polished chat interface with customizable accent colors

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | FastAPI (Python) |
| AI Model | Claude Sonnet 4 via OpenRouter |
| Widget | Vanilla JavaScript (no dependencies) |
| Frontend | HTML + TailwindCSS (CDN) |

## Quick Start

### Prerequisites

- Python 3.10+
- OpenRouter API key ([get one here](https://openrouter.ai/keys))

### Installation

```bash
# Clone the repository
git clone https://github.com/Seven7000000/supportbot.git
cd supportbot

# Install dependencies
pip install -r requirements.txt

# Set your API key
export OPENROUTER_API_KEY="your-key-here"

# Run the server
uvicorn main:app --port 8003 --reload
```

Open [http://localhost:8003](http://localhost:8003) in your browser.

### Embed on Any Website

Add this to any HTML page:

```html
<script>
  window.SUPPORTBOT_URL = "https://your-server.com";
  window.SUPPORTBOT_CONFIG = {
    business_name: "Your Company",
    primary_color: "#6366f1",
    personality: "friendly and helpful",
    knowledge_base: "Your FAQ content here..."
  };
</script>
<script src="https://your-server.com/widget.js"></script>
```

## API Reference

### `POST /configure`

Set the bot's configuration.

**Request:**
```json
{
  "business_name": "Acme Corp",
  "personality": "friendly and professional",
  "knowledge_base": "We offer 3 plans: Starter ($9/mo), Pro ($29/mo)...",
  "primary_color": "#6366f1"
}
```

### `GET /config`

Retrieve the current bot configuration.

### `POST /chat`

Send a message and get a response.

**Request:**
```json
{
  "message": "What plans do you offer?",
  "history": [],
  "config": {}
}
```

**Response:**
```json
{
  "reply": "We offer three plans: Starter at $9/month..."
}
```

### `GET /widget.js`

Returns the embeddable JavaScript widget. Automatically uses the configuration set via `window.SUPPORTBOT_CONFIG`.

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENROUTER_API_KEY` | Yes | Your OpenRouter API key |

## Project Structure

```
supportbot/
  main.py             # FastAPI application + widget.js endpoint
  requirements.txt    # Python dependencies
  static/
    index.html         # Configuration dashboard
```

## License

MIT
