# Web-Based Playwright POM Generator - Complete Implementation Plan

## Project Overview

A web-based IDE where users can generate, edit, and execute Playwright Page Object Model (POM) scripts through AI-assisted browser automation.

## Core Requirements

### User Interface
- Monaco Editor for code editing
- File tree browser (view/edit/delete/create)
- Conversation interface for prompting the agent
- Execution results viewer

### Agent Capabilities
1. **Live Browser Automation**: Navigate real websites using Playwright MCP
2. **DOM Inspection**: Extract REAL locators from live browser DOM (not inferred)
3. **Action Validation**: Perform test actions (click, input, select) to verify functionality
4. **Intelligent Code Generation**: Generate Playwright POM with actual locators
5. **Context-Aware Editing**: Update existing files while preserving user changes
6. **File Management**: Create/read/update files via Filesystem MCP

### Execution
- Run generated scripts in isolated environment (venv or Docker)
- Display results, logs, and screenshots

---

## Technology Stack

| Component | Technology | Status |
|-----------|-----------|--------|
| **Agent Framework** | LangGraph + LangChain | ✅ Implemented |
| **LLM** | Groq (llama-3.3-70b-versatile) | ✅ Implemented |
| **Backend API** | Python FastAPI | ✅ Implemented |
| **MCP Gateway** | Node.js + Express | ✅ Implemented |
| **Filesystem MCP** | Custom wrapper | ✅ Implemented |
| **Playwright MCP** | Microsoft @playwright/mcp | ⏳ In Progress |
| **Frontend** | Next.js 15 + React 19 | ❌ Not Started |
| **Code Editor** | Monaco Editor | ❌ Not Started |
| **Execution Engine** | Python venv (Phase 1) → Docker (Phase 2) | ❌ Not Started |

---

## Current Implementation Status

### ✅ Completed Components

#### 1. **LangGraph Agent** (`agent-backend/src/agent/`)
- **Files**: `agent.py`, `nodes.py`, `graph.py`, `state.py`
- **Features**:
  - Multi-node orchestration (planner, code_generator, finalizer)
  - State management with conversation history
  - Comprehensive logging at every step
  - LLM call tracking with token usage
  
#### 2. **Filesystem MCP** (`agent-backend/src/tools/filesystem_mcp.py`, `mcp-gateway/`)
- **Backend**: Python async client with logging
- **Gateway**: Node.js server with REST endpoints
- **Operations**: read, write, list, mkdir, delete
- **Status**: ✅ Fully functional and tested

#### 3. **Project Infrastructure**
- Workspace: `workspace/projects/` (file storage)
- Configuration: Environment-based (`.env`)
- Logging: Custom logger with node/LLM/tool call tracking
- Prompts: External prompt files in `src/prompts/`

---

## ❌ Missing Components (Critical for Goal)

### 1. **Playwright MCP Integration**
**Current State**: Playwright library installed, no integration with agent

**What's Missing**:
- Official `@playwright/mcp` not integrated
- No browser automation in agent graph
- Agent cannot navigate live websites
- Agent cannot extract real DOM locators

### 2. **Browser Automation Nodes**
**Current Agent Flow**: User Prompt → Planner → Code Generator → Finalizer

**Required Agent Flow**:
```
User Prompt 
  → Planner (determine if need live inspection)
  → Navigator (launch browser, navigate to URL)
  → Inspector (extract real DOM elements & locators)
  → Action Validator (test click/fill actions work)
  → Code Generator (use REAL locators)
  → File Writer (save via Filesystem MCP)
  → Finalizer (return response + file path)
```

### 3. **Context-Aware File Editing**
**Current**: Agent can only CREATE new files

**Required**:
- Read existing files before regenerating
- Parse existing POM structure
- Identify user manual edits (via `edits_history.json`)
- Merge new changes with existing code
- Preserve user customizations

### 4. **Frontend (Web IDE)**
**Status**: Not started

**Required Components**:
- File tree browser (left sidebar)
- Monaco Editor (main area)
- Prompt/chat interface (top or bottom)
- Execution results panel
- File operations UI (create/delete/rename)

### 5. **Execution Engine**
**Status**: Not started

**Required**:
- Spawn Python venv for script execution
- Mount workspace files
- Capture stdout/stderr/screenshots
- Return results to frontend
- Later: Docker container support

---

## Detailed Implementation Plan

---

## **Phase 1: Core Agent with Live Browser Automation** (Current Phase)

### Objective
Connect agent to live browser automation using Playwright MCP with real DOM inspection.

---

### **Step 43: Playwright MCP Integration**

**Task**: Evaluate official `@playwright/mcp` tools

#### Official MCP Tools
- Install `@playwright/mcp` package
- Test available tools via CLI: `npx @playwright/mcp@latest --help`
- Document tool list (navigate, click, fill, screenshot, etc.)
- Test stdio communication protocol

#### Decision Criteria
- **Use Official MCP**: All provided tools (navigate, inspect DOM, click, fill, Extract_DOM, get accessibility tree) are accessible to the agent

**Expected Outcome**: Clear path forward for Playwright integration

---

### **Step 44: Playwright MCP Gateway Setup**

**Task**: Add Playwright MCP server integration to MCP Gateway

#### Files to Create/Modify
- `mcp-gateway/src/playwright_mcp.js` (handler class)
- `mcp-gateway/src/server.js` (add routes)

**Deliverable**: MCP Gateway with Playwright endpoints working

---

### **Step 45: Python Playwright MCP Client**

**Task**: Create Python client to call Playwright MCP Gateway

#### File to Create
`agent-backend/src/tools/playwright_mcp.py`


**Deliverable**: Python client with comprehensive logging

---

### **Step 46: Update Agent State for Browser Context**

**Task**: Extend AgentState to track browser operations

#### File to Modify
`agent-backend/src/agent/state.py`

#### New State Fields
```python
class AgentState(TypedDict):
    # ... existing fields ...
    
    # Browser context
    target_url: Optional[str]           # URL to inspect
    browser_launched: bool              # Browser session state
    inspected_elements: List[Element]   # Real DOM elements found
    validated_actions: Dict[str, bool]  # {action: success}
    screenshots: List[str]              # Base64 screenshots
```

**Deliverable**: Updated state definition

---

### **Step 47: Create Browser Automation Nodes**

**Task**: Add new nodes to agent graph for live browser interaction

#### File to Modify
`agent-backend/src/agent/nodes.py`

#### New Nodes to Implement

##### **Node 1: Navigator**
```python
def navigator_node(self, state: AgentState) -> AgentState:
    """
    Launch browser and navigate to target URL
    
    Flow:
    1. Extract URL from user prompt or state
    2. Launch browser via Playwright MCP
    3. Navigate to URL
    4. Update state with navigation success
    """
```

##### **Node 2: Inspector**
```python
def inspector_node(self, state: AgentState) -> AgentState:
    """
    Inspect page and extract real DOM elements
    
    Flow:
    1. Call Playwright MCP inspect_elements()
    2. Get all interactive elements (inputs, buttons, links, etc.)
    3. Extract real locators (CSS, XPath, test-id)
    4. Store in state.inspected_elements
    """
```

##### **Node 3: Action Validator**
```python
def action_validator_node(self, state: AgentState) -> AgentState:
    """
    Test that identified elements are interactable
    
    Flow:
    1. For each element found by inspector
    2. Attempt action (click button, fill input, etc.)
    3. Record success/failure
    4. Take screenshot if action fails
    5. Update state.validated_actions
    """
```

##### **Node 4: Code Generator (Enhanced)**
```python
def code_generator_node(self, state: AgentState) -> AgentState:
    """
    Generate POM using REAL locators from inspector
    
    Flow:
    1. Use state.inspected_elements (not inferred locators)
    2. Generate POM class with actual selectors
    3. Include only validated actions
    4. Add wait conditions based on validation results
    """
```

**Deliverable**: Four new nodes with comprehensive logging

---

### **Step 48: Update Graph Builder**

**Task**: Rebuild agent graph with browser automation nodes

#### File to Modify
`agent-backend/src/agent/graph.py`

#### New Graph Flow
```
START
  ↓
Planner (determine if need browser inspection)
  ↓
Navigator (if URL provided) → Inspector → Action Validator
  ↓                                         ↓
Code Generator (uses real locators) ←───────┘
  ↓
File Writer (save via Filesystem MCP)
  ↓
Finalizer (prepare response)
  ↓
END
```

#### Conditional Routing Logic
```python
def route_after_planner(state):
    if state["target_url"]:
        return "navigator"  # Live inspection needed
    else:
        return "code_generator"  # Generate from description only

def route_after_validator(state):
    if state["validated_actions"]:
        return "code_generator"  # Generate with validated actions
    else:
        return "finalizer"  # Failed to validate, ask for clarification
```

**Deliverable**: Updated graph with browser nodes integrated

---

### **Step 49: Implement Context-Aware File Editing**

**Task**: Enable agent to UPDATE existing files (not just create)

#### Files to Create/Modify
- `agent-backend/src/tools/file_editor.py` (new)
- `agent-backend/src/agent/nodes.py` (modify code_generator_node)

#### File Editor Class
```python
class FileEditor:
    async def read_existing_pom(self, file_path: str) -> POMStructure
    async def parse_user_edits(self, original: str, current: str) -> List[Edit]
    async def merge_changes(self, existing_pom: POMStructure, new_elements: List[Element]) -> str
    async def generate_diff(self, old_code: str, new_code: str) -> str
```

#### Enhanced Code Generator Logic
```python
# In code_generator_node
if state["existing_files"].get(target_file):
    # File exists - UPDATE mode
    existing_code = await filesystem_mcp.read_file(target_file)
    user_edits = await file_editor.parse_user_edits(original, existing_code)
    
    # Generate merged code preserving user changes
    new_code = await file_editor.merge_changes(
        existing_pom=existing_code,
        new_elements=state["inspected_elements"],
        preserve_edits=user_edits
    )
else:
    # File doesn't exist - CREATE mode
    new_code = generate_fresh_pom(state["inspected_elements"])
```

**Deliverable**: Agent can intelligently update existing files

---

### **Step 50: End-to-End Agent Test**

**Task**: Test complete agent flow with live browser automation

#### Test Scenario
```python
# User prompt
"Generate a POM for the login page at https://example.com"

# Expected flow
1. Planner: Identifies URL, determines need for inspection
2. Navigator: Launches browser, navigates to example.com
3. Inspector: Extracts:
   - Input#username (locator: "#username")
   - Input#password (locator: "#password")
   - Button.login (locator: "button.login")
4. Validator: Tests all elements are interactable
5. Code Generator: Creates LoginPage with REAL locators
6. File Writer: Saves to workspace/projects/default/pages/login_page.py
7. Finalizer: Returns success + file path
```

#### Test Script
Create `agent-backend/test_live_browser_agent.py`

**Deliverable**: Agent successfully generates POM from live website

---

## **Phase 2: Frontend (Web IDE)** 

### Objective
Build web interface with Monaco Editor, file browser, and agent chat.

---

### **Step 51: Next.js Project Setup**

**Task**: Initialize frontend project

#### Commands
```bash
cd frontend
npx create-next-app@latest . --typescript --tailwind --app
npm install @monaco-editor/react lucide-react axios
```

#### Project Structure
```
frontend/
├── src/
│   ├── app/
│   │   ├── page.tsx              # Main IDE page
│   │   ├── layout.tsx
│   │   └── api/                  # API routes (optional)
│   ├── components/
│   │   ├── FileTree.tsx          # File browser
│   │   ├── MonacoEditor.tsx      # Code editor
│   │   ├── ChatInterface.tsx     # Agent conversation
│   │   ├── ExecutionPanel.tsx    # Results viewer
│   │   └── Toolbar.tsx           # Actions bar
│   └── lib/
│       ├── api.ts                # Backend API client
│       └── types.ts              # TypeScript types
```

**Deliverable**: Next.js project initialized

---

### **Step 52: File Tree Browser Component**

**Task**: Build file explorer sidebar

#### Component: `FileTree.tsx`

**Features**:
- Fetch files from `GET /api/files/list`
- Display folder/file icons
- Expand/collapse folders
- Click to open file in Monaco
- Right-click context menu (delete, rename)
- Create new file/folder buttons

#### API Integration
```typescript
const fetchFiles = async (path: string) => {
  const response = await axios.get('http://localhost:8000/api/files/list', {
    params: { path }
  });
  return response.data.files;
};
```

**Deliverable**: Working file tree browser

---

### **Step 53: Monaco Editor Integration**

**Task**: Embed code editor with syntax highlighting

#### Component: `MonacoEditor.tsx`

**Features**:
- Load file content from `GET /api/files/read?path=...`
- Auto-save on change via `POST /api/files/write`
- Python syntax highlighting
- Line numbers, minimap
- Keyboard shortcuts (Ctrl+S to save)

#### Implementation
```typescript
import Editor from '@monaco-editor/react';

<Editor
  height="100%"
  defaultLanguage="python"
  value={fileContent}
  onChange={handleEditorChange}
  options={{
    minimap: { enabled: true },
    fontSize: 14,
    automaticLayout: true
  }}
/>
```

**Deliverable**: Functional code editor with file operations

---

### **Step 54: Chat Interface Component**

**Task**: Build agent conversation UI

#### Component: `ChatInterface.tsx`

**Features**:
- Text input for user prompts
- "Generate" button
- Message history display
- Agent thinking status (which node is executing)
- Token usage display
- Real-time updates via WebSocket or SSE

#### API Integration
```typescript
const generatePOM = async (prompt: string) => {
  const response = await axios.post('http://localhost:8000/api/generate', {
    prompt,
    project_id: currentProject
  });
  return response.data;
};
```

**Deliverable**: Working chat interface with agent

---

### **Step 55: Backend API Endpoints for Frontend**

**Task**: Add file management endpoints to FastAPI

#### File to Modify
`agent-backend/src/api.py`

#### New Endpoints
```python
@app.get("/api/files/list")
async def list_files(path: str = "", project_id: str = "default"):
    # Call Filesystem MCP
    
@app.get("/api/files/read")
async def read_file(path: str):
    # Call Filesystem MCP
    
@app.post("/api/files/write")
async def write_file(path: str, content: str):
    # Call Filesystem MCP
    # Update edits_history.json
    
@app.post("/api/files/delete")
async def delete_file(path: str):
    # Call Filesystem MCP
    
@app.post("/api/generate")
async def generate_pom(prompt: str, project_id: str):
    # Call agent with context
    existing_files = await load_project_files(project_id)
    result = agent.process_request(prompt, project_id, existing_files)
    return result
```

**Deliverable**: Complete REST API for frontend

---

### **Step 56: Layout & Integration**

**Task**: Combine all components into IDE layout

#### Layout Structure
```
┌─────────────────────────────────────────────────┐
│  Toolbar (Project selector, Actions)            │
├──────────┬──────────────────────┬────────────────┤
│          │                      │                │
│  File    │   Monaco Editor      │  Chat          │
│  Tree    │   (Code View)        │  Interface     │
│          │                      │                │
│  (20%)   │      (60%)           │  (20%)         │
│          │                      │                │
├──────────┴──────────────────────┴────────────────┤
│  Execution Results / Terminal                    │
│  (Collapsible, 30% when expanded)                │
└──────────────────────────────────────────────────┘
```

#### Implementation
Use Tailwind CSS Grid or Flexbox for responsive layout

**Deliverable**: Fully functional web IDE

---

## **Phase 3: Execution Engine**

### Objective
Execute generated scripts in isolated environment and display results.

---

### **Step 57: Python venv Executor**

**Task**: Create script execution engine using Python venv

#### File to Create
`agent-backend/src/execution/venv_executor.py`

#### Implementation
```python
class VenvExecutor:
    def __init__(self, workspace_root: str):
        self.workspace_root = workspace_root
    
    async def execute_script(
        self,
        project_id: str,
        script_path: str,
        test_args: dict = {}
    ) -> ExecutionResult:
        """
        Execute Playwright script in isolated venv
        
        Steps:
        1. Create temporary venv
        2. Install playwright + pytest
        3. Copy project files to venv
        4. Run script with pytest
        5. Capture stdout, stderr, screenshots
        6. Return results
        7. Cleanup venv
        """
```

**Deliverable**: Script execution in venv working

---

### **Step 58: Execution API Endpoint**

**Task**: Add script execution endpoint

#### Endpoint
```python
@app.post("/api/execute")
async def execute_script(
    project_id: str,
    script_path: str,
    browser: str = "chromium",
    headless: bool = True
):
    executor = VenvExecutor(workspace_root)
    result = await executor.execute_script(project_id, script_path)
    
    return {
        "success": result.exit_code == 0,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "screenshots": result.screenshots,
        "duration": result.duration
    }
```

**Deliverable**: Execution endpoint working

---

### **Step 59: Execution Panel Component**

**Task**: Display execution results in frontend

#### Component: `ExecutionPanel.tsx`

**Features**:
- "Run" button in toolbar
- Show stdout/stderr in terminal-like UI
- Display screenshots inline
- Show pass/fail status
- Execution duration

**Deliverable**: Complete execution flow in UI

---

### **Step 60: Docker Executor (Optional)**

**Task**: Add Docker-based execution for better isolation

#### File to Create
`agent-backend/src/execution/docker_executor.py`

#### Implementation
- Create Dockerfile for Playwright execution environment
- Mount project files as volume
- Run pytest in container
- Same result structure as venv executor

**Deliverable**: Docker execution option available

---

## Testing Strategy

### Unit Tests
- Each MCP tool (filesystem, playwright)
- Each agent node independently
- File editor merge logic

### Integration Tests
- Agent end-to-end with live browser
- Frontend → Backend → MCP flow
- File operations through UI

### E2E Tests
- Complete user workflow:
  1. User enters prompt
  2. Agent inspects live site
  3. POM generated and saved
  4. User edits POM in Monaco
  5. User runs script
  6. Results displayed

---

## Success Criteria

### Phase 1 Complete When:
- ✅ Agent can navigate to live websites
- ✅ Agent extracts real DOM locators
- ✅ Agent validates actions work
- ✅ Generated POM uses actual locators
- ✅ Agent can update existing files

### Phase 2 Complete When:
- ✅ Monaco Editor loads and saves files
- ✅ File tree shows project structure
- ✅ Chat interface communicates with agent
- ✅ Users can create/edit/delete files

### Phase 3 Complete When:
- ✅ Scripts execute in isolated environment
- ✅ Results display in UI
- ✅ Screenshots captured and shown
- ✅ Logs viewable in terminal panel

---

## Current Blockers

### Critical Path Items:
1. **Playwright MCP Integration** - Must decide on official MCP vs wrapper
2. **Browser Automation Nodes** - Core agent functionality depends on this
3. **Real Locator Extraction** - Entire value proposition depends on this

### Non-Blocking Items:
- Frontend (can build after agent works)
- Execution engine (can test manually first)
- Docker support (venv sufficient initially)

---

## Next Immediate Steps

### Step 43: Research & Decision
1. Install `@playwright/mcp` package
2. Test available tools: `npx @playwright/mcp@latest --help`
3. Document tool capabilities
4. Decision: Official MCP or wrapper?

---