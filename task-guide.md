# Minecraft Remote Console — Task Guide

A practical guide for getting started on each task, what to research, and how to know when you're done.

---

## Parallel Workstreams

The MVP can be developed across three independent tracks that come together at integration.

```
Week 1-2:

  Track A (Backend Core)          Track B (Frontend)           Track C (RCON)
  ──────────────────────          ─────────────────            ──────────────
  Project scaffolding             Console HTML/CSS             RCON manager
  Config loading                  Login page HTML/CSS          Protocol research
  HTTP routes                     Console JavaScript           
  Socket.IO handlers                                           

Week 2-3:

                    ┌─────────────────────────┐
                    │      Integration        │
                    │  Connect all pieces     │
                    │  End-to-end testing     │
                    └─────────────────────────┘
```

---

## Track A: Backend Core

### Task A1: Project Scaffolding + Config Loading

**Summary**: Set up the Flask project structure and environment configuration.

**Suggested assignee**: Anyone (good starter task)

**Prerequisites**: Python 3.10+ installed, basic command line familiarity

#### Research Required

| Topic | Resources | Time |
|-------|-----------|------|
| Flask application factory pattern | [Flask docs: Application Factories](https://flask.palletsprojects.com/en/3.0.x/patterns/appfactories/) | 30 min |
| python-dotenv usage | [python-dotenv README](https://github.com/theskumar/python-dotenv) | 15 min |
| Virtual environments | [Python venv docs](https://docs.python.org/3/library/venv.html) | 15 min |

#### How to Start

1. Create project directory and initialise git repo
2. Create virtual environment: `python -m venv venv`
3. Activate it: `source venv/bin/activate`
4. Install initial dependencies: `pip install flask python-dotenv`
5. Create the folder structure from the design doc
6. Write `app/__init__.py` with a `create_app()` factory function
7. Write `app/config.py` to load settings from environment
8. Create `.env.example` with placeholder values
9. Write `run.py` that calls `create_app()` and runs the dev server

#### Definition of Done

- [ ] Running `python run.py` starts Flask without errors
- [ ] Visiting `http://127.0.0.1:5000/` returns something (even a 404 is fine)
- [ ] Configuration values load from `.env` file
- [ ] `.env` is in `.gitignore`
- [ ] `.env.example` exists with all required keys (no real secrets)
- [ ] `requirements.txt` exists and is accurate
- [ ] Another team member can clone, create venv, install deps, and run the app

---

### Task A2: HTTP Routes (Login, Logout, Index)

**Summary**: Implement the authentication flow and page serving.

**Suggested assignee**: Backend-focused team member

**Prerequisites**: Task A1 complete, basic HTML forms knowledge

#### Research Required

| Topic | Resources | Time |
|-------|-----------|------|
| Flask routing | [Flask Quickstart: Routing](https://flask.palletsprojects.com/en/3.0.x/quickstart/#routing) | 20 min |
| Flask sessions | [Flask Quickstart: Sessions](https://flask.palletsprojects.com/en/3.0.x/quickstart/#sessions) | 20 min |
| Werkzeug password hashing | [Werkzeug security docs](https://werkzeug.palletsprojects.com/en/3.0.x/utils/#module-werkzeug.security) | 15 min |
| Flask redirects and errors | [Flask docs: Redirects and Errors](https://flask.palletsprojects.com/en/3.0.x/quickstart/#redirects-and-errors) | 15 min |

#### How to Start

1. Create `app/routes.py` with a Flask Blueprint
2. Implement `GET /login` — render login template
3. Implement `POST /login` — validate password against hash, set session, redirect
4. Implement `POST /logout` — clear session, redirect to login
5. Implement `GET /` — check session, render console or redirect to login
6. Register the blueprint in `app/__init__.py`
7. Create placeholder templates (can be minimal HTML, Track B will style them)

#### Definition of Done

- [ ] Unauthenticated user visiting `/` is redirected to `/login`
- [ ] Correct password on `/login` creates session and redirects to `/`
- [ ] Incorrect password shows an error message on login page
- [ ] Authenticated user visiting `/` sees the console template
- [ ] `/logout` clears session and redirects to `/login`
- [ ] Password is verified against hash (never stored in plain text)
- [ ] Routes work with placeholder templates (no styling required)

---

### Task A3: Socket.IO Event Handlers

**Summary**: Implement real-time WebSocket communication for commands.

**Suggested assignee**: Backend-focused team member

**Prerequisites**: Task A1 complete, Task C1 complete (or mockable)

#### Research Required

| Topic | Resources | Time |
|-------|-----------|------|
| Flask-SocketIO basics | [Flask-SocketIO docs](https://flask-socketio.readthedocs.io/en/latest/getting_started.html) | 45 min |
| Socket.IO rooms and sessions | [Flask-SocketIO rooms](https://flask-socketio.readthedocs.io/en/latest/getting_started.html#rooms) | 20 min |
| Handling connection/disconnection | [Flask-SocketIO events](https://flask-socketio.readthedocs.io/en/latest/getting_started.html#receiving-messages) | 20 min |
| gevent basics (why it's needed) | [Flask-SocketIO deployment](https://flask-socketio.readthedocs.io/en/latest/deployment.html) | 15 min |

#### How to Start

1. Add `flask-socketio` and `gevent` to requirements
2. Initialise SocketIO in `app/__init__.py`
3. Create `app/events.py` for event handlers
4. Implement `connect` event — verify session is authenticated, emit initial state
5. Implement `disconnect` event — cleanup if needed
6. Implement `switch_server` event — update session's current server, emit status
7. Implement `command` event — call RCON manager, emit echo and response
8. Handle RCON errors gracefully, emit error events

#### Mocking RCON for Development

Before Task C1 is done, create a mock:

```python
# Temporary mock in events.py
def mock_execute(server_id, command):
    return f"[MOCK] Executed '{command}' on {server_id}"
```

Replace with real RCON manager once Task C1 is complete.

#### Definition of Done

- [ ] WebSocket connection is established when console page loads
- [ ] Unauthenticated WebSocket connections are rejected
- [ ] `switch_server` event updates the user's current server
- [ ] `command` event returns a response (mock or real)
- [ ] `command_echo` is emitted immediately when command received
- [ ] RCON errors result in `error` event with message
- [ ] Server status is emitted after switch or error
- [ ] Multiple browser tabs work independently (isolated sessions)

---

## Track B: Frontend

### Task B1: Console HTML Template + CSS

**Summary**: Build the terminal-style interface.

**Suggested assignee**: Frontend-interested team member

**Prerequisites**: Basic HTML/CSS knowledge

#### Research Required

| Topic | Resources | Time |
|-------|-----------|------|
| Jinja2 templating | [Jinja2 Template Designer docs](https://jinja.palletsprojects.com/en/3.1.x/templates/) | 30 min |
| CSS Flexbox (for layout) | [CSS-Tricks Flexbox Guide](https://css-tricks.com/snippets/css/a-guide-to-flexbox/) | 30 min |
| Monospace fonts and terminal aesthetics | Look at existing terminals, iTerm2, VS Code terminal | 20 min |
| HTML form basics | [MDN: HTML Forms](https://developer.mozilla.org/en-US/docs/Learn/Forms) | 20 min |

#### How to Start

1. Create `app/templates/base.html` with common HTML structure
2. Create `app/templates/console.html` extending base
3. Design the layout:
   - Header bar with server selector dropdown and connection status indicator
   - Main area: scrolling output container
   - Footer bar: command input and send button
4. Create `app/static/css/terminal.css`
5. Style for terminal feel:
   - Dark background (`#1e1e1e` or similar)
   - Monospace font (`Consolas`, `Monaco`, `monospace`)
   - Light text (`#f0f0f0`)
   - Commands in one colour, responses in another
   - Error state styling (red border, disabled input appearance)

#### Visual Reference

```
┌─────────────────────────────────────────────────────────┐
│  [Vanilla SMP ▼]                    ● Connected         │  <- Header
├─────────────────────────────────────────────────────────┤
│                                                         │
│  > /list                                        [cmd]   │
│  There are 2/20 players online: Alex, Steve    [resp]   │
│  > /time query daytime                         [cmd]    │
│  The time is 6000                              [resp]   │
│                                                         │
│                                                         │  <- Scrollable
│                                                         │
│                                                         │
├─────────────────────────────────────────────────────────┤
│  [_______________________________________] [Send]       │  <- Input
└─────────────────────────────────────────────────────────┘
```

#### Definition of Done

- [ ] Console page has header, output area, and input bar
- [ ] Server selector dropdown is present (functionality comes later)
- [ ] Connection status indicator is present (updates via JS later)
- [ ] Output area scrolls when content overflows
- [ ] Input field spans available width with send button beside it
- [ ] Terminal aesthetic: dark background, monospace font, appropriate colours
- [ ] Error state has distinct visual styling (e.g., red banner, greyed input)
- [ ] Page is usable at different viewport widths (basic responsiveness)
- [ ] No JavaScript required yet — just static HTML/CSS

---

### Task B2: Login Page HTML/CSS

**Summary**: Build the login form page.

**Suggested assignee**: Frontend-interested team member (can parallel with B1)

**Prerequisites**: Basic HTML/CSS knowledge

#### Research Required

Same as Task B1, plus:

| Topic | Resources | Time |
|-------|-----------|------|
| Accessible form design | [MDN: Form Accessibility](https://developer.mozilla.org/en-US/docs/Learn/Forms/How_to_structure_a_web_form) | 20 min |

#### How to Start

1. Create `app/templates/login.html` extending base
2. Design a centred login card:
   - Title/logo area
   - Password input field
   - Submit button
   - Error message area (for invalid password feedback)
3. Style to complement the console theme (same colour palette)

#### Definition of Done

- [ ] Login page renders at `/login`
- [ ] Password field has `type="password"`
- [ ] Form submits via POST to `/login`
- [ ] Error message area exists (populated by Flask on failure)
- [ ] Styling matches console page theme
- [ ] Looks reasonable on mobile viewports
- [ ] Form has proper labels for accessibility

---

### Task B3: Console JavaScript (Socket.IO Client)

**Summary**: Implement the real-time frontend logic.

**Suggested assignee**: Frontend-interested team member

**Prerequisites**: Task B1 complete, basic JavaScript knowledge

#### Research Required

| Topic | Resources | Time |
|-------|-----------|------|
| Socket.IO client basics | [Socket.IO client docs](https://socket.io/docs/v4/client-initialization/) | 30 min |
| Socket.IO events | [Socket.IO emitting events](https://socket.io/docs/v4/emitting-events/) | 20 min |
| DOM manipulation (vanilla JS) | [MDN: Document API](https://developer.mozilla.org/en-US/docs/Web/API/Document) | 30 min |
| Event listeners | [MDN: addEventListener](https://developer.mozilla.org/en-US/docs/Web/API/EventTarget/addEventListener) | 20 min |

#### How to Start

1. Add Socket.IO client script to template (CDN link)
2. Create `app/static/js/console.js`
3. On page load:
   - Initialise Socket.IO connection
   - Set up event listeners for server events
   - Set up event listeners for UI interactions
4. Implement handlers:
   - `connected` — update status indicator, enable input
   - `server_status` — update status, enable/disable input based on status
   - `command_echo` — append command to output
   - `command_response` — append response to output
   - `error` — show error, disable input
5. Implement UI handlers:
   - Send button click — emit `command` event
   - Enter key in input — emit `command` event
   - Server dropdown change — emit `switch_server` event

#### Definition of Done

- [ ] Socket.IO connection is established on page load
- [ ] Connection status indicator updates based on connection state
- [ ] Typing a command and pressing Enter sends it
- [ ] Typing a command and clicking Send sends it
- [ ] Commands appear in output with distinct styling
- [ ] Responses appear in output with distinct styling
- [ ] Changing server dropdown emits `switch_server` event
- [ ] Errors display in UI and disable input
- [ ] Output area auto-scrolls to bottom on new content
- [ ] Input field clears after sending command

---

## Track C: RCON

### Task C1: RCON Manager Module

**Summary**: Implement the module that communicates with Minecraft servers.

**Suggested assignee**: Someone interested in networking/protocols

**Prerequisites**: Basic Python, understanding of TCP concepts helpful

#### Research Required

| Topic | Resources | Time |
|-------|-----------|------|
| RCON protocol | [Minecraft RCON wiki](https://wiki.vg/RCON) | 45 min |
| mcrcon library usage | [mcrcon PyPI](https://pypi.org/project/mcrcon/) | 15 min |
| Python exception handling | [Python docs: Exceptions](https://docs.python.org/3/tutorial/errors.html) | 20 min |
| Context managers | [Python docs: with statement](https://docs.python.org/3/reference/compound_stmts.html#with) | 15 min |

#### How to Start

1. Create `app/rcon_manager.py`
2. Define a class or module that:
   - Loads server configurations from app config
   - Provides `execute(server_id, command) -> str` method
   - Provides `health_check(server_id) -> bool` method
   - Handles connection errors gracefully
3. Decide on connection strategy:
   - **Simple (recommended for MVP)**: Open new connection per command, close after
   - **Advanced**: Connection pooling (not needed for MVP)
4. Write comprehensive error handling:
   - Connection refused (server down)
   - Authentication failed (wrong RCON password)
   - Timeout (server unresponsive)
   - Invalid server_id

#### Testing Without Full App

Create a standalone test script:

```python
# test_rcon.py (not part of app, just for testing)
from app.rcon_manager import execute, health_check

# Test against a running Minecraft server
print(health_check("vanilla"))
print(execute("vanilla", "/list"))
```

#### Definition of Done

- [ ] `execute(server_id, command)` sends command and returns response string
- [ ] `health_check(server_id)` returns True if server is reachable
- [ ] Invalid `server_id` raises appropriate exception
- [ ] Connection failure raises appropriate exception with useful message
- [ ] Auth failure raises appropriate exception with useful message
- [ ] Timeout is handled (doesn't hang forever)
- [ ] Works correctly with both configured servers
- [ ] Standalone test script demonstrates functionality

---

## Integration

### Task I1: Connect All Pieces

**Summary**: Wire up backend, frontend, and RCON manager.

**Suggested assignee**: Whole team together

**Prerequisites**: All Track A, B, C tasks complete

#### How to Start

1. Replace RCON mock in events.py with real rcon_manager calls
2. Ensure config flows correctly from .env through to RCON manager
3. Test full flow: login → connect → send command → see response
4. Test error scenarios: stop Minecraft server, try to send command
5. Test server switching

#### Definition of Done

- [ ] User can log in with correct password
- [ ] User is redirected away from login if already authenticated
- [ ] Console page loads and WebSocket connects
- [ ] Commands sent to Vanilla server work
- [ ] Commands sent to Modded server work
- [ ] Switching servers works correctly
- [ ] Server down scenario shows error, disables input
- [ ] Wrong RCON password scenario is handled gracefully
- [ ] Logout works and prevents further access

---

### Task I2: End-to-End Testing + Documentation

**Summary**: Verify everything works together and document setup.

**Suggested assignee**: Whole team

**Prerequisites**: Task I1 complete

#### How to Start

1. Write a test checklist (see below)
2. Have each team member run through the checklist
3. Document any bugs found, fix them
4. Write README.md with:
   - Project description
   - Prerequisites
   - Setup instructions
   - Configuration guide
   - Running in development
   - Running in production (basic)

#### Test Checklist

```markdown
## Fresh Setup Test
- [ ] Clone repo on fresh machine
- [ ] Create venv and install deps
- [ ] Copy .env.example to .env and fill in values
- [ ] Run app, verify it starts

## Authentication Tests
- [ ] Cannot access / without logging in
- [ ] Wrong password shows error
- [ ] Correct password grants access
- [ ] Logout removes access
- [ ] Session persists across page refresh

## Console Tests (Server Running)
- [ ] WebSocket connects on page load
- [ ] Status shows "Connected"
- [ ] Can send /list command
- [ ] Command appears in console
- [ ] Response appears in console
- [ ] Can switch servers
- [ ] Commands go to correct server after switch

## Error Handling Tests (Server Stopped)
- [ ] Status shows error state
- [ ] Input is disabled
- [ ] Error message is displayed
- [ ] Starting server and retrying works

## Edge Cases
- [ ] Empty command (should it send or ignore?)
- [ ] Very long command
- [ ] Very long response
- [ ] Rapid command submission
- [ ] Multiple tabs open simultaneously
```

#### Definition of Done

- [ ] All test checklist items pass
- [ ] README exists with complete setup instructions
- [ ] Another person can set up the project using only the README
- [ ] Known issues are documented (if any)

---

## Quick Reference: Who Can Work on What in Parallel

| Phase | Person A | Person B | Person C |
|-------|----------|----------|----------|
| Week 1 | A1: Scaffolding | B1: Console HTML/CSS | C1: RCON Manager |
| Week 1 | A2: Routes | B2: Login HTML/CSS | C1: continued |
| Week 2 | A3: Socket.IO | B3: Console JS | Help where needed |
| Week 2-3 | I1: Integration (all together) | | |
| Week 3 | I2: Testing + Docs (all together) | | |

---

## Tips for the Team

**Daily check-ins**: Even 10 minutes to share what you're stuck on helps.

**Use branches**: Each task gets a branch, merge to main when done.

**Don't wait for perfection**: Get something working, then improve it.

**Test early**: Don't wait until integration to see if your code runs.

**Ask questions**: If research isn't making sense, ask a teammate or search for tutorials.

**Document as you go**: Comments in code, notes in README — future you will thank present you.