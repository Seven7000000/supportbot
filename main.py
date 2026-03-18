from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, Response
from pydantic import BaseModel
import requests
import os

app = FastAPI(title="SupportBot")

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
MODEL = "anthropic/claude-sonnet-4-20250514"


class ChatRequest(BaseModel):
    message: str
    history: list[dict] = []
    config: dict = {}


class ConfigRequest(BaseModel):
    business_name: str = "Our Company"
    personality: str = "friendly and helpful"
    knowledge_base: str = ""
    primary_color: str = "#6366f1"


# Default configuration
bot_config = {
    "business_name": "Our Company",
    "personality": "friendly and helpful",
    "knowledge_base": "",
    "primary_color": "#6366f1",
}


@app.post("/configure")
async def configure(req: ConfigRequest):
    global bot_config
    bot_config = req.model_dump()
    return {"status": "ok", "config": bot_config}


@app.get("/config")
async def get_config():
    return bot_config


@app.post("/chat")
async def chat(req: ChatRequest):
    if not req.message.strip():
        raise HTTPException(status_code=400, detail="Message is required")

    config = req.config if req.config else bot_config

    kb_section = ""
    if config.get("knowledge_base", "").strip():
        kb_section = f"\n\n--- KNOWLEDGE BASE ---\n{config['knowledge_base']}\n--- END KNOWLEDGE BASE ---\nUse this knowledge base to answer questions when relevant."

    system_prompt = (
        f"You are a customer support assistant for {config.get('business_name', 'Our Company')}. "
        f"Your personality is: {config.get('personality', 'friendly and helpful')}. "
        f"Be concise, helpful, and professional. If you don't know something specific about the business, "
        f"offer to connect the user with a human agent. Use short paragraphs. "
        f"Never make up specific policies, prices, or details unless they're in the knowledge base."
        f"{kb_section}"
    )

    messages = [{"role": "system", "content": system_prompt}]
    for msg in req.history[-20:]:
        messages.append({"role": msg["role"], "content": msg["content"]})
    messages.append({"role": "user", "content": req.message})

    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
            },
            json={"model": MODEL, "messages": messages, "max_tokens": 500},
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()
        answer = data["choices"][0]["message"]["content"]
        return {"reply": answer}
    except requests.exceptions.Timeout:
        raise HTTPException(status_code=504, detail="AI request timed out")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI error: {str(e)}")


@app.get("/widget.js")
async def widget_script():
    """Embeddable widget script"""
    script = """
(function() {
    const BACKEND = window.SUPPORTBOT_URL || window.location.origin;
    const CONFIG = window.SUPPORTBOT_CONFIG || {};

    const style = document.createElement('style');
    style.textContent = `
        #sb-widget-btn { position: fixed; bottom: 24px; right: 24px; width: 56px; height: 56px; border-radius: 50%; background: ${CONFIG.primary_color || '#6366f1'}; border: none; cursor: pointer; box-shadow: 0 4px 20px rgba(0,0,0,0.3); display: flex; align-items: center; justify-content: center; z-index: 99999; transition: transform 0.2s; }
        #sb-widget-btn:hover { transform: scale(1.1); }
        #sb-widget-btn svg { width: 24px; height: 24px; fill: white; }
        #sb-widget-panel { position: fixed; bottom: 96px; right: 24px; width: 380px; max-width: calc(100vw - 48px); height: 520px; max-height: calc(100vh - 120px); background: #1a1a2e; border: 1px solid #2d2d44; border-radius: 16px; box-shadow: 0 8px 40px rgba(0,0,0,0.5); z-index: 99999; display: none; flex-direction: column; overflow: hidden; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; }
        #sb-widget-panel.open { display: flex; }
        #sb-header { padding: 16px; background: ${CONFIG.primary_color || '#6366f1'}; color: white; }
        #sb-header h3 { margin: 0; font-size: 15px; font-weight: 600; }
        #sb-header p { margin: 4px 0 0; font-size: 12px; opacity: 0.85; }
        #sb-messages { flex: 1; overflow-y: auto; padding: 16px; display: flex; flex-direction: column; gap: 12px; }
        #sb-messages::-webkit-scrollbar { width: 4px; }
        #sb-messages::-webkit-scrollbar-thumb { background: #444; border-radius: 2px; }
        .sb-msg { max-width: 85%; padding: 10px 14px; border-radius: 12px; font-size: 13px; line-height: 1.5; color: #e0e0e0; word-wrap: break-word; }
        .sb-msg.bot { background: #252540; align-self: flex-start; border-bottom-left-radius: 4px; }
        .sb-msg.user { background: ${CONFIG.primary_color || '#6366f1'}; color: white; align-self: flex-end; border-bottom-right-radius: 4px; }
        .sb-msg.typing { opacity: 0.6; }
        #sb-input-area { padding: 12px; border-top: 1px solid #2d2d44; display: flex; gap: 8px; }
        #sb-input { flex: 1; background: #12121a; border: 1px solid #2d2d44; border-radius: 8px; padding: 10px 12px; color: #e0e0e0; font-size: 13px; outline: none; }
        #sb-input:focus { border-color: ${CONFIG.primary_color || '#6366f1'}; }
        #sb-send { background: ${CONFIG.primary_color || '#6366f1'}; border: none; border-radius: 8px; width: 40px; cursor: pointer; display: flex; align-items: center; justify-content: center; }
        #sb-send svg { width: 18px; height: 18px; fill: white; }
    `;
    document.head.appendChild(style);

    // Button
    const btn = document.createElement('button');
    btn.id = 'sb-widget-btn';
    btn.innerHTML = '<svg viewBox="0 0 24 24"><path d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm0 14H6l-2 2V4h16v12z"/></svg>';
    document.body.appendChild(btn);

    // Panel
    const panel = document.createElement('div');
    panel.id = 'sb-widget-panel';
    panel.innerHTML = `
        <div id="sb-header">
            <h3>${CONFIG.business_name || 'Support'}</h3>
            <p>Ask us anything</p>
        </div>
        <div id="sb-messages">
            <div class="sb-msg bot">Hi! How can I help you today?</div>
        </div>
        <div id="sb-input-area">
            <input id="sb-input" placeholder="Type a message..." />
            <button id="sb-send"><svg viewBox="0 0 24 24"><path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/></svg></button>
        </div>`;
    document.body.appendChild(panel);

    let isOpen = false;
    let history = [];

    btn.onclick = () => {
        isOpen = !isOpen;
        panel.classList.toggle('open', isOpen);
    };

    const input = document.getElementById('sb-input');
    const sendBtn = document.getElementById('sb-send');
    const messages = document.getElementById('sb-messages');

    function addMsg(text, cls) {
        const d = document.createElement('div');
        d.className = 'sb-msg ' + cls;
        d.textContent = text;
        messages.appendChild(d);
        messages.scrollTop = messages.scrollHeight;
        return d;
    }

    async function send() {
        const text = input.value.trim();
        if (!text) return;
        input.value = '';
        addMsg(text, 'user');
        const typing = addMsg('Typing...', 'bot typing');

        try {
            const res = await fetch(BACKEND + '/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: text, history, config: CONFIG })
            });
            const data = await res.json();
            typing.remove();
            if (data.reply) {
                addMsg(data.reply, 'bot');
                history.push({ role: 'user', content: text });
                history.push({ role: 'assistant', content: data.reply });
            } else {
                addMsg('Sorry, something went wrong.', 'bot');
            }
        } catch(e) {
            typing.remove();
            addMsg('Connection error. Please try again.', 'bot');
        }
    }

    sendBtn.onclick = send;
    input.onkeydown = (e) => { if (e.key === 'Enter') send(); };
})();
""".strip()
    return Response(content=script, media_type="application/javascript")


app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def root():
    return FileResponse("static/index.html")
