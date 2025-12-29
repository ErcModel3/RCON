# Minecraft Remote Console — MVP Design Document

## Overview

A lightweight web application providing real-time remote console access to two Minecraft servers via RCON. Users authenticate with a shared password, connect to a server, send commands, and see responses in a terminal-style interface.

---

## Architectural Constraints

| Constraint | Decision |
|------------|----------|
| Deployment | Same host as Minecraft servers |
| Console data source | RCON only (no log file tailing) |
| User sessions | Isolated (each user sees only their own commands) |
| Command filtering | None (all commands permitted) |
| Session history | Ephemeral (fresh console on each connection) |
| Connection errors | Display error, disable input until resolved |

---

## Tech Stack

### Backend

| Component | Technology | Rationale |
|-----------|------------|-----------|
| Web framework | Flask 3.x | Lightweight, beginner-friendly, excellent documentation |
| Real-time transport | Flask-SocketIO 5.x | Abstracts WebSocket complexity, handles reconnection, integrates cleanly with Flask |
| Async worker | gevent or eventlet | Required by Flask-SocketIO for WebSocket support |
| RCON client | mcrcon | Simple, well-maintained Python RCON library |
| Configuration | python-dotenv | Load environment variables from .env file |
| Password hashing | Werkzeug (built into Flask) | Secure password verification without extra dependencies |

### Frontend

| Component | Technology | Rationale |
|-----------|------------|-----------|
| Templating | Jinja2 (Flask built-in) | Server-rendered HTML, no build step required |
| Real-time client | Socket.IO JS client (CDN) | Matches Flask-SocketIO, handles reconnection automatically |
| Styling | Vanilla CSS | No framework needed for terminal aesthetic |
| JavaScript | Vanilla ES6 | No build step, easy for beginners to understand |

### Infrastructure

| Component | Technology | Rationale |
|-----------|------------|-----------|
| Process manager | systemd | Already on Linux hosts, production-ready |
| WSGI server | gunicorn with gevent worker | Required for Socket.IO in production |
| Reverse proxy | nginx (optional) | TLS termination if exposed beyond localhost |

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                              Browser                                │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │                    Single Page Application                    │  │
│  │  ┌─────────────────────────────────────────────────────────┐  │  │
│  │  │  [Vanilla ▼]                              [Connected]   │  │  │
│  │  ├─────────────────────────────────────────────────────────┤  │  │
│  │  │                                                         │  │  │
│  │  │  > /list                                                │  │  │
│  │  │  There are 3/20 players online: Alex, Steve, Notch      │  │  │
│  │  │  > /time set day                                        │  │  │
│  │  │  Set the time to 1000                                   │  │  │
│  │  │  > _                                                    │  │  │
│  │  │                                                         │  │  │
│  │  ├─────────────────────────────────────────────────────────┤  │  │
│  │  │  [____________________________________] [Send]          │  │  │
│  │  └─────────────────────────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
                                   │
                                   │ Socket.IO (WebSocket + HTTP fallback)
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         Flask Application                           │
│                                                                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────────┐  │
│  │   Routes    │  │   SocketIO  │  │      RCON Manager           │  │
│  │             │  │   Handlers  │  │                             │  │
│  │ GET /       │  │             │  │  ┌───────────────────────┐  │  │
│  │ GET /login  │  │ connect     │  │  │ Vanilla Connection    │  │  │
│  │ POST /login │◄─┤ disconnect  │◄─┤  │ - health check        │  │  │
│  │ POST /logout│  │ command     │  │  │ - execute(cmd) → resp │  │  │
│  │             │  │ switch      │  │  └───────────────────────┘  │  │
│  └─────────────┘  └─────────────┘  │  ┌───────────────────────┐  │  │
│                                    │  │ Modded Connection     │  │  │
│                                    │  │ - health check        │  │  │
│                                    │  │ - execute(cmd) → resp │  │  │
│                                    │  └───────────────────────┘  │  │
│                                    └─────────────────────────────┘  │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │                      Configuration                          │    │
│  │  Loaded from .env: server details, password hash, secrets   │    │
│  └─────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────┘
                                   │
                    ┌──────────────┴──────────────┐
                    │                             │
                    ▼                             ▼
          ┌─────────────────┐           ┌─────────────────┐
          │  Vanilla Server │           │  Modded Server  │
          │                 │           │                 │
          │  RCON: 25575    │           │  RCON: 25576    │
          └─────────────────┘           └─────────────────┘
```

---

## Component Design

### 1. Flask Routes (HTTP)

| Route | Method | Auth Required | Purpose |
|-------|--------|---------------|---------|
| `/` | GET | Yes | Serve main console page |
| `/login` | GET | No | Serve login form |
| `/login` | POST | No | Validate password, create session |
| `/logout` | POST | Yes | Clear session, redirect to login |
| `/health` | GET | No | Application health check |

### 2. Socket.IO Events

**Client → Server**

| Event | Payload | Description |
|-------|---------|-------------|
| `connect` | (automatic) | Client establishes WebSocket connection |
| `switch_server` | `{server_id: "vanilla"}` | Client wants to use a different server |
| `command` | `{command: "/list"}` | Client sends command to current server |

**Server → Client**

| Event | Payload | Description |
|-------|---------|-------------|
| `connected` | `{server_id: "vanilla", server_name: "Vanilla SMP", status: "ok"}` | Confirms connection, provides initial state |
| `server_status` | `{server_id: "vanilla", status: "ok" \| "error", message?: "..."}` | Server health update after switch or error |
| `command_echo` | `{command: "/list"}` | Echo back the command (for display) |
| `command_response` | `{response: "There are 3/20 players..."}` | RCON response |
| `error` | `{message: "RCON connection failed", recoverable: true}` | Error notification |

### 3. RCON Manager

Responsibilities:
- Maintain RCON connection state per server
- Execute commands and return responses
- Provide health check capability
- Handle connection failures gracefully

Behaviour:
- Connections are established lazily (on first command or health check)
- Failed connections are retried on next command attempt
- Each command opens a fresh RCON connection (simpler than pooling for MVP)

### 4. Session State

Each WebSocket connection (Socket.IO session) tracks:

```python
{
    "user_authenticated": True,
    "current_server": "vanilla"  # or "modded"
}
```

No database — state lives in memory, tied to the WebSocket connection lifetime.

---

## Data Flow: Sending a Command

```
1. User types "/list" and clicks Send
                    │
                    ▼
2. Browser emits Socket.IO event
   Event: "command"
   Payload: {command: "/list"}
                    │
                    ▼
3. Flask-SocketIO handler receives event
   - Validates user is authenticated (session check)
   - Looks up user's current server from session
   - Emits "command_echo" back to client immediately
                    │
                    ▼
4. RCON Manager executes command
   - Opens TCP connection to server's RCON port
   - Sends RCON command packet
   - Receives response packet
   - Closes connection
                    │
                    ▼
5. Handler emits response to client
   Event: "command_response"
   Payload: {response: "There are 3/20 players online: Alex, Steve, Notch"}
                    │
                    ▼
6. Browser appends response to console display
```

---

## Data Flow: Connection Failure

```
1. User sends command (or switches server)
                    │
                    ▼
2. RCON Manager attempts connection
   - TCP connection refused / timeout / auth failure
                    │
                    ▼
3. Handler catches exception
   - Emits "server_status" with status: "error"
   - Emits "error" with message details
                    │
                    ▼
4. Browser receives error
   - Displays error banner
   - Disables command input
   - Shows retry button (triggers health check)
```

---

## Project Structure

```
mc-console/
├── app/
│   ├── __init__.py           # Flask app factory, SocketIO init
│   ├── config.py             # Configuration loading from environment
│   ├── routes.py             # HTTP route handlers
│   ├── events.py             # Socket.IO event handlers
│   ├── rcon_manager.py       # RCON connection and command execution
│   ├── auth.py               # Authentication helpers
│   ├── templates/
│   │   ├── base.html         # Base template with common structure
│   │   ├── login.html        # Login page
│   │   └── console.html      # Main console interface
│   └── static/
│       ├── css/
│       │   └── terminal.css  # Terminal styling
│       └── js/
│           └── console.js    # Socket.IO client logic
├── .env                      # Environment configuration (git-ignored)
├── .env.example              # Example configuration (committed)
├── requirements.txt          # Python dependencies
├── run.py                    # Development server entry point
└── README.md                 # Setup and usage instructions
```

---

## Configuration Schema

```env
# .env

# Flask
SECRET_KEY=your-random-secret-key-here

# Authentication
CONSOLE_PASSWORD_HASH=pbkdf2:sha256:600000$...

# Vanilla Server
VANILLA_NAME=Vanilla SMP
VANILLA_RCON_HOST=127.0.0.1
VANILLA_RCON_PORT=25575
VANILLA_RCON_PASSWORD=your-vanilla-rcon-password

# Modded Server
MODDED_NAME=Modded ATM9
MODDED_RCON_HOST=127.0.0.1
MODDED_RCON_PORT=25576
MODDED_RCON_PASSWORD=your-modded-rcon-password
```

---

## Security Considerations

| Concern | Mitigation |
|---------|------------|
| Password storage | Stored as hash using Werkzeug's PBKDF2 |
| Session hijacking | Flask signed cookies, SECRET_KEY must be strong |
| RCON password exposure | Never sent to frontend, only used server-side |
| XSS in console output | Escape all output before rendering in browser |
| CSRF | Socket.IO connections validated against session |
| Network exposure | Bind to 127.0.0.1 by default; use nginx + TLS if exposing |

---

## Dependencies

```
# requirements.txt

flask>=3.0.0
flask-socketio>=5.3.0
python-dotenv>=1.0.0
mcrcon>=0.7.0
gevent>=24.0.0
gevent-websocket>=0.10.1
```

---

## Development vs Production

| Aspect | Development | Production |
|--------|-------------|------------|
| Server | `flask run` or `python run.py` | gunicorn with gevent worker |
| Binding | `127.0.0.1:5000` | Unix socket or `127.0.0.1:5000` behind nginx |
| Debug mode | Enabled | Disabled |
| TLS | None | nginx handles termination |
| Process management | Manual | systemd service |

### Production Command

```bash
gunicorn --worker-class geventwebsocket.gunicorn.workers.GeventWebSocketWorker \
         --workers 1 \
         --bind 127.0.0.1:5000 \
         "app:create_app()"
```

---

## Future Enhancements (Post-MVP)

| Feature | Complexity | Value |
|---------|------------|-------|
| Log file tailing | Medium | Full console visibility |
| Shared view mode | Low | Team collaboration |
| Command history (in-memory) | Low | Better UX |
| User accounts + roles | Medium | Access control |
| Command audit logging | Medium | Accountability |
| Go RCON service | High | Learning opportunity, better concurrency |
| Multiple server support (dynamic) | Medium | Scalability |
| Container deployment | Medium | Portability |

---

## Task Breakdown for Team

| Task | Estimated Effort | Dependencies |
|------|------------------|--------------|
| Project scaffolding + config loading | 1-2 hours | None |
| RCON manager module | 2-3 hours | None |
| HTTP routes (login, logout, index) | 2-3 hours | Scaffolding |
| Socket.IO event handlers | 3-4 hours | RCON manager |
| Login page template | 1-2 hours | Routes |
| Console page template + CSS | 3-4 hours | None |
| Console JavaScript (Socket.IO client) | 3-4 hours | Events, template |
| Integration testing | 2-3 hours | All above |
| Documentation + setup guide | 1-2 hours | All above |

Parallelisation options:
- RCON manager can be built independently
- Templates and CSS can be built without backend
- Integration happens once pieces are ready