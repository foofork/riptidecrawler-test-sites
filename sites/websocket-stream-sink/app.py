"""
websocket-stream-sink - WebSocket Streaming Server (Phase 3)
Port: 5013

Features:
- WebSocket echo server for crawl requests
- Streams back NDJSON results in real-time
- Supports backpressure (client pause/resume)
- Final stats event on completion
- Simulates crawling with progress updates
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import HTMLResponse, StreamingResponse
import asyncio
import json
from typing import Dict, List
import time
from datetime import datetime

app = FastAPI(title="WebSocket Stream Sink")

# Simulated crawl data for different sites
CRAWL_SIMULATIONS = {
    "example.com": {
        "pages": 10,
        "delay": 0.2,
        "success_rate": 0.9
    },
    "test-site.local": {
        "pages": 25,
        "delay": 0.15,
        "success_rate": 0.95
    },
    "large-site.com": {
        "pages": 50,
        "delay": 0.1,
        "success_rate": 0.85
    }
}

async def simulate_crawl(url: str, websocket: WebSocket):
    """Simulate crawling a website and stream results via WebSocket."""

    # Get simulation config or use default
    config = CRAWL_SIMULATIONS.get(url, {
        "pages": 15,
        "delay": 0.2,
        "success_rate": 0.9
    })

    stats = {
        "url": url,
        "started_at": datetime.utcnow().isoformat(),
        "total_pages": config["pages"],
        "pages_crawled": 0,
        "pages_success": 0,
        "pages_failed": 0,
        "bytes_transferred": 0
    }

    # Send initial status
    await websocket.send_json({
        "type": "start",
        "url": url,
        "total_pages": config["pages"],
        "timestamp": stats["started_at"]
    })

    # Simulate crawling each page
    for page_num in range(1, config["pages"] + 1):
        # Check for backpressure control messages
        try:
            # Non-blocking check for control messages
            control_msg = await asyncio.wait_for(
                websocket.receive_text(),
                timeout=0.01
            )
            control = json.loads(control_msg)

            if control.get("action") == "pause":
                # Wait for resume signal
                await websocket.send_json({
                    "type": "paused",
                    "page": page_num,
                    "timestamp": datetime.utcnow().isoformat()
                })

                while True:
                    resume_msg = await websocket.receive_text()
                    resume = json.loads(resume_msg)
                    if resume.get("action") == "resume":
                        await websocket.send_json({
                            "type": "resumed",
                            "page": page_num,
                            "timestamp": datetime.utcnow().isoformat()
                        })
                        break
        except asyncio.TimeoutError:
            # No control message, continue crawling
            pass
        except json.JSONDecodeError:
            # Invalid control message, ignore
            pass

        # Simulate page crawl
        await asyncio.sleep(config["delay"])

        # Determine if page crawl was successful
        import random
        success = random.random() < config["success_rate"]

        stats["pages_crawled"] += 1
        if success:
            stats["pages_success"] += 1
            page_size = random.randint(2000, 50000)
            stats["bytes_transferred"] += page_size

            # Send NDJSON result
            result = {
                "type": "page",
                "url": f"{url}/page-{page_num}",
                "status": 200,
                "size": page_size,
                "title": f"Page {page_num} - {url}",
                "timestamp": datetime.utcnow().isoformat(),
                "page_num": page_num,
                "total_pages": config["pages"]
            }
        else:
            stats["pages_failed"] += 1

            # Send error result
            result = {
                "type": "page",
                "url": f"{url}/page-{page_num}",
                "status": 404,
                "error": "Page not found",
                "timestamp": datetime.utcnow().isoformat(),
                "page_num": page_num,
                "total_pages": config["pages"]
            }

        # Send as NDJSON (newline-delimited JSON)
        await websocket.send_text(json.dumps(result) + "\n")

        # Send progress update every 5 pages
        if page_num % 5 == 0:
            progress = {
                "type": "progress",
                "pages_crawled": stats["pages_crawled"],
                "pages_success": stats["pages_success"],
                "pages_failed": stats["pages_failed"],
                "percent_complete": (page_num / config["pages"]) * 100,
                "timestamp": datetime.utcnow().isoformat()
            }
            await websocket.send_json(progress)

    # Send final stats
    stats["completed_at"] = datetime.utcnow().isoformat()
    stats["duration_seconds"] = (
        datetime.fromisoformat(stats["completed_at"]) -
        datetime.fromisoformat(stats["started_at"])
    ).total_seconds()

    await websocket.send_json({
        "type": "complete",
        "stats": stats,
        "timestamp": stats["completed_at"]
    })

@app.websocket("/ws/crawl")
async def websocket_crawl(websocket: WebSocket):
    """WebSocket endpoint for crawl requests."""
    await websocket.accept()

    try:
        # Wait for initial crawl request
        data = await websocket.receive_text()
        request = json.loads(data)

        if request.get("action") != "crawl":
            await websocket.send_json({
                "type": "error",
                "message": "First message must be a crawl request with 'action': 'crawl'"
            })
            return

        url = request.get("url")
        if not url:
            await websocket.send_json({
                "type": "error",
                "message": "URL is required"
            })
            return

        # Start crawl simulation
        await simulate_crawl(url, websocket)

    except WebSocketDisconnect:
        print("Client disconnected")
    except Exception as e:
        try:
            await websocket.send_json({
                "type": "error",
                "message": str(e),
                "timestamp": datetime.utcnow().isoformat()
            })
        except:
            pass

@app.get("/", response_class=HTMLResponse)
async def home():
    """Simple HTML client for testing WebSocket functionality."""
    return """
<!DOCTYPE html>
<html>
<head>
    <title>WebSocket Stream Sink</title>
    <style>
        body {
            font-family: 'Courier New', monospace;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: #1e1e1e;
            color: #d4d4d4;
        }
        .container {
            background: #2d2d2d;
            border-radius: 8px;
            padding: 30px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        }
        h1 {
            color: #4ec9b0;
            border-bottom: 2px solid #4ec9b0;
            padding-bottom: 10px;
        }
        .controls {
            margin: 20px 0;
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }
        input {
            flex: 1;
            min-width: 300px;
            padding: 10px;
            background: #3c3c3c;
            border: 1px solid #555;
            color: #d4d4d4;
            border-radius: 4px;
            font-family: 'Courier New', monospace;
        }
        button {
            padding: 10px 20px;
            background: #007acc;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-weight: bold;
            transition: background 0.3s;
        }
        button:hover {
            background: #005a9e;
        }
        button:disabled {
            background: #555;
            cursor: not-allowed;
        }
        button.pause {
            background: #ce9178;
        }
        button.pause:hover {
            background: #a5714e;
        }
        #output {
            background: #1e1e1e;
            border: 1px solid #555;
            border-radius: 4px;
            padding: 15px;
            height: 500px;
            overflow-y: auto;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
            margin-top: 20px;
        }
        .message {
            margin: 5px 0;
            padding: 5px;
            border-left: 3px solid #4ec9b0;
            padding-left: 10px;
        }
        .message.start {
            border-left-color: #4ec9b0;
            color: #4ec9b0;
        }
        .message.page {
            border-left-color: #569cd6;
            color: #569cd6;
        }
        .message.progress {
            border-left-color: #dcdcaa;
            color: #dcdcaa;
        }
        .message.complete {
            border-left-color: #b5cea8;
            color: #b5cea8;
            font-weight: bold;
        }
        .message.error {
            border-left-color: #f48771;
            color: #f48771;
        }
        .stats {
            background: #2d2d2d;
            padding: 15px;
            border-radius: 4px;
            margin-top: 20px;
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
        }
        .stat {
            text-align: center;
        }
        .stat-value {
            font-size: 2em;
            font-weight: bold;
            color: #4ec9b0;
        }
        .stat-label {
            font-size: 0.9em;
            color: #858585;
            margin-top: 5px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🌊 WebSocket Stream Sink</h1>
        <p>Real-time crawl streaming with backpressure control</p>

        <div class="controls">
            <input type="text" id="urlInput" placeholder="Enter URL to crawl (e.g., example.com)" value="example.com">
            <button id="connectBtn" onclick="connect()">Connect & Crawl</button>
            <button id="pauseBtn" onclick="togglePause()" disabled class="pause">Pause</button>
            <button id="disconnectBtn" onclick="disconnect()" disabled>Disconnect</button>
        </div>

        <div class="stats">
            <div class="stat">
                <div class="stat-value" id="totalPages">0</div>
                <div class="stat-label">Total Pages</div>
            </div>
            <div class="stat">
                <div class="stat-value" id="crawledPages">0</div>
                <div class="stat-label">Crawled</div>
            </div>
            <div class="stat">
                <div class="stat-value" id="successPages">0</div>
                <div class="stat-label">Success</div>
            </div>
            <div class="stat">
                <div class="stat-value" id="failedPages">0</div>
                <div class="stat-label">Failed</div>
            </div>
            <div class="stat">
                <div class="stat-value" id="progress">0%</div>
                <div class="stat-label">Progress</div>
            </div>
        </div>

        <div id="output"></div>
    </div>

    <script>
        let ws = null;
        let isPaused = false;

        function addMessage(text, type = 'info') {
            const output = document.getElementById('output');
            const msg = document.createElement('div');
            msg.className = `message ${type}`;
            msg.textContent = text;
            output.appendChild(msg);
            output.scrollTop = output.scrollHeight;
        }

        function updateStats(data) {
            if (data.total_pages) {
                document.getElementById('totalPages').textContent = data.total_pages;
            }
            if (data.pages_crawled !== undefined) {
                document.getElementById('crawledPages').textContent = data.pages_crawled;
            }
            if (data.pages_success !== undefined) {
                document.getElementById('successPages').textContent = data.pages_success;
            }
            if (data.pages_failed !== undefined) {
                document.getElementById('failedPages').textContent = data.pages_failed;
            }
            if (data.percent_complete !== undefined) {
                document.getElementById('progress').textContent = data.percent_complete.toFixed(1) + '%';
            }
        }

        function connect() {
            const url = document.getElementById('urlInput').value;
            if (!url) {
                alert('Please enter a URL');
                return;
            }

            const wsUrl = `ws://${window.location.host}/ws/crawl`;
            ws = new WebSocket(wsUrl);

            ws.onopen = () => {
                addMessage('🟢 Connected to WebSocket', 'start');
                document.getElementById('connectBtn').disabled = true;
                document.getElementById('pauseBtn').disabled = false;
                document.getElementById('disconnectBtn').disabled = false;

                // Send crawl request
                ws.send(JSON.stringify({
                    action: 'crawl',
                    url: url
                }));
                addMessage(`📡 Crawl request sent for: ${url}`, 'start');
            };

            ws.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);

                    switch(data.type) {
                        case 'start':
                            addMessage(`🚀 Crawl started: ${data.total_pages} pages`, 'start');
                            updateStats(data);
                            break;
                        case 'page':
                            if (data.status === 200) {
                                addMessage(`✓ ${data.url} [${data.size} bytes]`, 'page');
                            } else {
                                addMessage(`✗ ${data.url} [${data.error}]`, 'error');
                            }
                            break;
                        case 'progress':
                            addMessage(`📊 Progress: ${data.percent_complete.toFixed(1)}% (${data.pages_success} success, ${data.pages_failed} failed)`, 'progress');
                            updateStats(data);
                            break;
                        case 'complete':
                            addMessage(`✅ Crawl complete! Duration: ${data.stats.duration_seconds.toFixed(2)}s, Data: ${(data.stats.bytes_transferred / 1024).toFixed(2)} KB`, 'complete');
                            updateStats(data.stats);
                            document.getElementById('pauseBtn').disabled = true;
                            break;
                        case 'paused':
                            addMessage('⏸️ Crawl paused', 'progress');
                            break;
                        case 'resumed':
                            addMessage('▶️ Crawl resumed', 'progress');
                            break;
                        case 'error':
                            addMessage(`❌ Error: ${data.message}`, 'error');
                            break;
                    }
                } catch (e) {
                    addMessage(`Raw: ${event.data}`, 'page');
                }
            };

            ws.onclose = () => {
                addMessage('🔴 Disconnected', 'error');
                document.getElementById('connectBtn').disabled = false;
                document.getElementById('pauseBtn').disabled = true;
                document.getElementById('disconnectBtn').disabled = true;
            };

            ws.onerror = (error) => {
                addMessage('❌ WebSocket error', 'error');
            };
        }

        function togglePause() {
            if (!ws) return;

            isPaused = !isPaused;
            const btn = document.getElementById('pauseBtn');

            if (isPaused) {
                ws.send(JSON.stringify({ action: 'pause' }));
                btn.textContent = 'Resume';
            } else {
                ws.send(JSON.stringify({ action: 'resume' }));
                btn.textContent = 'Pause';
            }
        }

        function disconnect() {
            if (ws) {
                ws.close();
                ws = null;
            }
        }
    </script>
</body>
</html>
"""

@app.get("/events")
async def sse_events():
    """Server-Sent Events (SSE) endpoint for real-time updates."""
    async def event_generator():
        """Generate SSE events."""
        # Send initial connection event
        yield f"data: {json.dumps({'type': 'connected', 'timestamp': datetime.utcnow().isoformat()})}\n\n"

        # Send periodic updates
        for i in range(10):
            await asyncio.sleep(0.5)
            event_data = {
                "type": "update",
                "id": i + 1,
                "message": f"Event {i + 1}",
                "timestamp": datetime.utcnow().isoformat()
            }
            yield f"data: {json.dumps(event_data)}\n\n"

        # Send completion event
        yield f"data: {json.dumps({'type': 'complete', 'timestamp': datetime.utcnow().isoformat()})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"  # Disable buffering in nginx
        }
    )

@app.get("/ws")
async def websocket_info(request: Request):
    """
    WebSocket endpoint info - Returns appropriate status for upgrade requests.

    When Upgrade header is present, returns 426 Upgrade Required.
    Otherwise returns info about WebSocket endpoints.
    """
    # Check if this is a WebSocket upgrade request
    upgrade_header = request.headers.get("upgrade", "").lower()
    connection_header = request.headers.get("connection", "").lower()

    if "websocket" in upgrade_header and "upgrade" in connection_header:
        # Return 426 to indicate WebSocket upgrade is required
        # (Cannot use 101 with FastAPI's regular endpoint, need @app.websocket)
        return HTMLResponse(
            content="WebSocket endpoint - use /ws/crawl for WebSocket connection",
            status_code=426,
            headers={
                "Upgrade": "websocket",
                "Connection": "Upgrade"
            }
        )

    # Regular HTTP request - return info
    return {
        "message": "WebSocket endpoint",
        "endpoints": {
            "/ws/crawl": "WebSocket crawl streaming endpoint"
        },
        "upgrade_to": "websocket"
    }

@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "websocket-stream-sink",
        "port": 5013,
        "features": [
            "WebSocket echo server",
            "NDJSON streaming",
            "Backpressure support",
            "Real-time progress updates",
            "Server-Sent Events (SSE)"
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5013)
