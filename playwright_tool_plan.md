# Implementation Plan: Web-Based Playwright Script Generation Tool
## **Updated with Architectural Decisions**

---

## Key Architectural Decisions Made

### **1. Application Deployment**
- ✅ **Application runs locally on Windows** (No Docker for app components)
- ✅ **Docker ONLY for Playwright script execution** (isolated sandbox)
- Reason: Faster development, simpler debugging, true isolation where needed

### **2. Agent Framework**
- ✅ **LangGraph (with LangChain)** - NOT Claude Agent SDK
- Reason: Model-agnostic, supports Groq/Claude/GPT/Gemini, advanced orchestration

### **3. LLM Strategy**
- ✅ **Phase 1-2**: Groq (Free, unlimited) - llama-3.3-70b-versatile
- ✅ **Phase 3-4**: Claude 3.5 Haiku (Optional, $5 credits)
- ✅ **Production**: Configurable (Groq/Claude/Gemini via env variable)

### **4. Execution Isolation**
- ✅ **Phase 1-2**: Python venv (fast development)
- ✅ **Phase 3+**: Docker containers (production isolation)
- ✅ **Implementation**: Hybrid with config switch (EXECUTION_MODE=venv/docker)

---

## Technology Stack (Final)

| Component | Technology | Notes |
|-----------|-----------|-------|
| **Agent Framework** | LangGraph + LangChain | Orchestration with cycles, model-agnostic |
| **LLM** | Groq (llama-3.3-70b-versatile) | Free unlimited, configurable to others |
| **Backend** | Python 3.12 + FastAPI | Local execution, venv isolation |
| **Frontend** | Next.js 15 / React 19 | Local Node.js server |
| **MCP Gateway** | Node.js 20 + MCP SDK | Local server, manual integration |
| **Script Execution** | Python venv → Docker (later) | Hybrid approach |
| **Deployment** | Local development | No containers for app |

---

## Updated Phase 1: Foundation Setup (Week 1)

### ✅ **Completed Tasks:**

1. **Project Structure Created**
   - Root: `C:\Desktop\web-playwright`
   - Folders: agent-backend, frontend, mcp-gateway, workspace
   - Git initialized, .gitignore configured

2. **Environment Setup**
   - Python 3.12.1 venv created in agent-backend
   - Groq API key configured (.env file)
   - Model: llama-3.3-70b-versatile

3. **Dependencies Installed**
   - **Python**: groq, langchain 1.2.0, langgraph 1.0.5, langchain-groq 1.1.1, fastapi, uvicorn
   - **Removed**: anthropic, websockets (not needed)
   - **Node.js**: Frontend and MCP gateway packages installed

4. **Basic Tests Passed**
   - ✅ Groq API connection verified
   - ✅ LangGraph + Groq integration tested
   - ✅ Simple agent graph working

---

### 🔄 **Remaining Phase 1 Tasks:**

#### **Day 3-4: Build LangGraph Agent (Current Step)**

**Objective**: Create production-ready agent with state management and tool preparation

**Tasks:**

1. **Rewrite `src/agent.py` with LangGraph**
   - Define AgentState (messages, context, tool_results)
   - Create planning node (decides which tools to use)
   - Create execution node (calls tools)
   - Create code generation node (creates POM files)
   - Add conditional edges for orchestration
   - Implement conversation history management

2. **Update `src/config.py`**
   - Add LangGraph-specific configs
   - Tool registry structure (for future MCP tools)
   - Graph execution settings

3. **Update `src/api.py`**
   - Adapt endpoints for LangGraph streaming
   - Add endpoint to view graph state
   - Add endpoint to reset agent state
   - Handle tool call responses

4. **Create Agent Test Suite**
   - Test multi-step reasoning
   - Test state persistence
   - Test conversation context
   - Test error handling

**Deliverable**: Production-ready LangGraph agent responding to complex prompts

---

#### **Day 5-7: MCP Integration Preparation**

**Objective**: Prepare tool calling infrastructure for Playwright and Filesystem MCPs

**Tasks:**

1. **Create Tool Wrapper System**
   - Abstract layer to convert MCP tools → LangGraph tools
   - Tool registry for dynamic tool loading
   - Tool result parsing and validation

2. **Install MCP Servers (Node.js)**
   - `@modelcontextprotocol/server-filesystem` in mcp-gateway
   - Playwright MCP server
   - Test servers independently

3. **MCP Gateway Service**
   - HTTP endpoints to proxy tool calls
   - Route: POST /mcp/call-tool
   - Handle stdio communication with MCP servers

4. **Connect Agent to MCP Gateway**
   - LangGraph tool nodes call MCP gateway
   - Parse MCP responses
   - Handle errors and retries

5. **Integration Testing**
   - Agent calls filesystem MCP: write/read files
   - Agent calls Playwright MCP: navigate, extract elements
   - Verify end-to-end tool execution

**Deliverable**: Agent can call MCP tools via LangGraph orchestration

---

## Phase 2: Core Functionality (Week 2)

### **Day 8-10: UI & First POM Generation**

**Objective**: Complete end-to-end workflow from UI to generated POM file

**Tasks:**

1. **Build Next.js Frontend**
   - Prompt input interface
   - Real-time agent status display (which node is executing)
   - Code viewer with syntax highlighting
   - Token usage and cost tracking

2. **Frontend-Backend Integration**
   - WebSocket connection for streaming
   - Display agent reasoning steps
   - Show tool calls in progress

3. **First Complete Workflow**
   - User: "Generate POM for login page at example.com"
   - Agent graph: plan → navigate (Playwright MCP) → extract elements → generate code → save file (Filesystem MCP)
   - UI: Display generated POM and save location

**Deliverable**: Working demo - prompt to POM file generation

---

### **Day 11-12: POM Quality Enhancement**

**Objective**: Improve generated POM quality through better prompts and validation

**Tasks:**

1. **Enhanced System Prompts**
   - POM best practices instructions
   - Locator selection strategy
   - Code quality guidelines

2. **Multi-Step Element Analysis**
   - Identify all interactive elements
   - Extract multiple locator strategies per element
   - Rank by stability

3. **Advanced Code Generation**
   - Type hints, docstrings
   - Async/sync methods
   - Wait conditions
   - Error handling

4. **Validation Node in Graph**
   - Check generated code syntax
   - Verify imports
   - Suggest improvements

**Deliverable**: Production-quality POM files

---

### **Day 13-14: File Management & Session Persistence**

**Objective**: Project and session management

**Tasks:**

1. **File Browser UI**
   - Tree view of workspace
   - File preview with syntax highlighting
   - Download, rename, delete operations

2. **Session Management**
   - Save LangGraph state to disk
   - Resume previous conversations
   - Project isolation

3. **Multi-Project Support**
   - Create/switch projects
   - Isolated workspaces per project
   - Export project as ZIP

**Deliverable**: Complete file and project management

---

## Phase 3: Script Execution & Advanced Features (Week 3-4)

### **Week 3: Execution Engine**

**Objective**: Add script execution with isolation

**Tasks:**

1. **Build Execution Layer**
   - Create `EXECUTION_MODE` config (venv/docker)
   - Phase 3: Use venv for speed
   - Implement subprocess execution
   - Capture stdout/stderr/screenshots

2. **Execution Results Display**
   - Show test pass/fail status
   - Display logs in UI
   - Show screenshots from test runs

3. **Test Generation**
   - Generate pytest files using POMs
   - Add fixtures and assertions
   - Create test data

**Deliverable**: Execute generated scripts and show results

---

### **Week 4: Production Preparation**

**Objective**: Production-ready features

**Tasks:**

1. **Add Docker Execution Mode**
   - Create Dockerfile for Playwright execution environment
   - Python script to spawn Docker containers dynamically
   - Switch via `EXECUTION_MODE=docker`

2. **Multi-LLM Support**
   - Add support for Claude API (langchain-anthropic)
   - Add support for Gemini (langchain-google-genai)
   - Config-based switching: LLM_PROVIDER=groq/claude/gemini

3. **Production Hardening**
   - Add authentication (simple JWT)
   - Rate limiting per user
   - Request logging and monitoring
   - Error handling and user feedback

4. **Documentation**
   - Setup guide
   - API documentation
   - User manual with examples

**Deliverable**: Production-ready application

---

## Phase 4: Deployment & Scaling (Week 5+)

### **Optional Production Features**

**Tasks:**

1. **Cloud Deployment**
   - Containerize app for cloud (if needed later)
   - Docker Compose for multi-user setup
   - Environment configuration

2. **Advanced Features**
   - Multi-page workflow support
   - Component extraction (reusable POMs)
   - Test suite generation
   - CI/CD integration helpers

3. **Optimization**
   - Caching frequent responses
   - Parallel tool execution
   - Graph optimization for speed

**Deliverable**: Scalable production system

---

## Success Metrics by Phase

### **Phase 1 (Week 1)**
- ✅ LangGraph agent responds to prompts
- ✅ MCP tools callable from agent
- ✅ Basic graph orchestration working
- ✅ Cost: $0 (Groq free)

### **Phase 2 (Week 2)**
- ✅ End-to-end POM generation functional
- ✅ Generated POMs are valid Python code
- ✅ File management working
- ✅ Cost: $0 (Groq free)

### **Phase 3 (Week 3-4)**
- ✅ Scripts execute successfully
- ✅ Docker isolation working
- ✅ Multi-LLM support functional
- ✅ Cost: $0-5 (optional Claude testing)

### **Phase 4 (Week 5+)**
- ✅ Multi-user capable
- ✅ Production-stable
- ✅ Complete documentation
- ✅ Cost: $0/month (Groq or Gemini free)

---

## Current Status: Phase 1, Day 3

### ✅ **Completed:**
- Project structure created
- Groq API connected
- LangGraph + Groq tested
- Dependencies installed

### 🔄 **Next Immediate Steps:**

1. **Rewrite `src/agent.py`** with LangGraph (production agent)
2. **Update `src/api.py`** for graph integration
3. **Test multi-step agent workflows**
4. **Prepare MCP tool integration**

### 📋 **Files Status:**

**Completed:**
- ✅ `agent-backend/requirements.txt` (latest versions)
- ✅ `agent-backend/.env` (Groq API key configured)
- ✅ `agent-backend/src/config.py` (basic config)
- ✅ `agent-backend/test_langgraph_groq.py` (connection test)
- ✅ `.gitignore` (includes venv/)

**To Create/Update:**
- 🔄 `agent-backend/src/agent.py` (needs LangGraph rewrite)
- 🔄 `agent-backend/src/api.py` (needs graph integration)
- ⏳ `mcp-gateway/src/server.js` (not started)
- ⏳ `frontend/` (not started)

---

## Quick Reference: Key Commands

### **Activate Python venv:**
```powershell
cd C:\Desktop\web-playwright\agent-backend
.\venv\Scripts\activate
```

### **Run API Server:**
```powershell
python src/api.py
```

### **Test Agent:**
```powershell
python test_langgraph_groq.py
```

### **Check Package Versions:**
```powershell
pip show langchain langgraph langchain-groq
```

---

## Cost Tracking

| Phase | LLM | Estimated Cost | Actual Cost |
|-------|-----|----------------|-------------|
| **Week 1-2** | Groq | $0 | $0 |
| **Week 3-4** | Groq | $0 | TBD |
| **Production** | Groq/Gemini | $0/month | TBD |

**Total Budget**: $0 for entire development

---

## Risk Mitigation Updates

### **Groq Rate Limits**
- Current: 30 req/min (plenty for single developer)
- Mitigation: Add exponential backoff if needed
- Monitor: console.groq.com dashboard

### **Model Deprecation**
- ✅ Already handled: llama-3.1-70b-versatile deprecated → switched to llama-3.3-70b-versatile
- Future: Config-based model selection makes switching easy

### **Complexity Management**
- ✅ Using LangGraph simplifies orchestration
- ✅ Avoided Docker complexity for app (only for execution)
- ✅ Incremental feature addition prevents scope creep

---