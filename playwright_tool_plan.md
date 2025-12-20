# Implementation Plan: Web-Based Playwright Script Generation Tool
## **Using Free/Trial Cloud LLM APIs**

---

## Prerequisites

### Development Environment Setup

#### Required Software
1. **Docker Desktop** (v24.0+) - For containerized development
2. **Node.js & npm** (v18+) - For MCP servers and frontend
3. **Python** (v3.11+) - For AI agent backend
4. **Git** - For version control
5. **VS Code** (recommended) - With Docker, Python, ESLint extensions

#### **API Keys & Free Tier Options**

**Option 1: Anthropic Claude (RECOMMENDED)**
- **Free Trial**: $5 free credits on signup
- **No credit card required initially**
- Sign up at: console.anthropic.com
- **Model**: Claude 3.5 Haiku ($0.80/$4.00 per million tokens)
- **$5 gets you**: ~400-600 POM generations (excellent for initial development)
- **Trial period**: Credits don't expire, use at your pace

**Option 2: OpenAI GPT**
- **Free Trial**: $5 free credits (expires after 3 months)
- Sign up at: platform.openai.com
- **Model**: GPT-4o-mini ($0.15/$0.60 per million tokens)
- **$5 gets you**: ~800-1000 generations

**Option 3: Google Gemini**
- **Free Tier**: 1500 requests/day on Gemini 1.5 Flash
- **Completely free** (no credit card needed)
- Sign up at: ai.google.dev
- **Best for**: Extended free development period

**Option 4: Groq (FASTEST & FREE)**
- **Free Tier**: 30 requests/minute, unlimited usage
- **Models**: Llama 3.1 70B, Mixtral (all free)
- Sign up at: console.groq.com
- **Best for**: Fast iterations during development

---

## **Recommended Strategy for Free Development**

### **Phase-Based LLM Usage**

**Week 1-2 (Initial Development)**: 
- Use **Groq (Free, unlimited)** - No cost concerns, fast responses
- Focus on: Architecture setup, MCP integration, basic workflows

**Week 3-4 (Refinement)**:
- Switch to **Anthropic Claude** ($5 free credits) - Better code quality
- Focus on: POM generation quality, complex workflows

**Week 5+ (Production Ready)**:
- Use **Google Gemini Free Tier** - 1500 req/day is plenty for 3-5 users
- Or budget for paid Claude/OpenAI ($10-20/month for small team)

### **Cost-Free Development Timeline**
You can complete entire 5-week development **spending $0**:
- Weeks 1-2: Groq (free)
- Weeks 3-4: Anthropic free credits
- Week 5+: Gemini free tier or OpenAI free credits

---

## Revised Technology Stack (Free LLM Focus)

| Component | Technology | Free Option |
|-----------|-----------|-------------|
| **Agent Framework** | Claude Agent SDK | ✅ Free (SDK is open source) |
| **LLM - Development** | Groq API (Llama 3.1) | ✅ Free unlimited |
| **LLM - Quality Testing** | Claude 3.5 Haiku | ✅ $5 free credits |
| **LLM - Production** | Gemini 1.5 Flash | ✅ 1500 req/day free |
| **Backend** | Python + Node.js | ✅ Free |
| **Frontend** | Next.js / React | ✅ Free |
| **MCP Servers** | Official MCP servers | ✅ Free |
| **Docker** | Docker Desktop | ✅ Free for individuals |

---

## Phase 1: Foundation Setup (Week 1)
**LLM: Groq API (Free)**

### Day 1-2: Project Scaffolding & Environment

**Objective**: Set up project structure and verify free API access

#### Key Tasks:
1. **Sign up for Groq API**
   - Visit console.groq.com
   - Create account (no credit card needed)
   - Copy API key
   - Test connection with simple curl command

2. **Initialize Project Structure**
   - Create git repository
   - Set up directory structure (frontend, agent-backend, mcp-gateway)
   - Create .env files with API keys
   - Add .env to .gitignore

3. **Docker Configuration**
   - Write docker-compose.yml with 3 services
   - Create Dockerfiles for each service
   - Test: `docker-compose up` starts all containers

4. **Environment Variables Setup**
   ```
   .env file structure:
   - GROQ_API_KEY=your-key-here
   - LLM_PROVIDER=groq
   - MODEL_NAME=llama-3.1-70b-versatile
   ```

**Deliverable**: All containers running, Groq API accessible

---

### Day 3-4: Agent Backend with Groq

**Objective**: Get Python agent calling Groq API successfully

#### Key Tasks:
1. **Install Python Dependencies**
   - anthropic SDK (for agent framework)
   - groq SDK (for LLM calls)
   - fastapi, uvicorn (for API server)
   - python-dotenv (for config)

2. **Create Agent Configuration System**
   - Config class that reads LLM_PROVIDER from env
   - Support switching between Groq/Claude/OpenAI
   - Validate API keys on startup

3. **Implement Basic Agent**
   - Initialize Groq client
   - Send test prompt
   - Receive and parse response
   - Handle errors gracefully

4. **Create REST API**
   - FastAPI endpoint: POST /api/generate
   - Accepts user prompt
   - Returns LLM response + token usage
   - Add CORS for frontend access

5. **Test End-to-End**
   - Start agent-backend container
   - Send test request via curl/Postman
   - Verify response from Groq

**Deliverable**: Agent backend responding to prompts via Groq API

---

### Day 5-7: MCP Server Integration

**Objective**: Connect Filesystem and Playwright MCP servers to agent

#### Key Tasks:
1. **Set Up MCP Gateway (Node.js)**
   - Install MCP SDK packages
   - Install filesystem MCP server
   - Create server startup script

2. **Configure Filesystem MCP**
   - Set allowed directories (workspace folder)
   - Define permissions (read/write/edit)
   - Test basic file operations

3. **Install Playwright MCP**
   - Install Playwright with browsers
   - Configure browser automation settings
   - Test navigation to sample page

4. **Bridge Agent to MCP**
   - Create MCP gateway HTTP endpoints
   - Update Python agent to call MCP gateway
   - Implement tool calling workflow

5. **Integration Testing**
   - Agent calls: "write file test.py"
   - Verify file appears in workspace
   - Agent calls: "navigate to google.com"
   - Verify browser action completes

**Deliverable**: Agent can control files and browser via MCP

---

## Phase 2: Core Functionality (Week 2)
**LLM: Still Groq (Free) - Focus on functionality**

### Day 8-10: UI & First Working Demo

**Objective**: Build web interface and complete end-to-end POM generation

#### Key Tasks:
1. **Create Next.js Frontend**
   - Initialize Next.js project with TypeScript
   - Install UI dependencies (Tailwind, icons)
   - Set up API connection to backend

2. **Build Core UI Components**
   - Prompt input textarea (large, centered)
   - Generate button with loading state
   - Result display area (code viewer with syntax highlighting)
   - Token usage display

3. **Implement Frontend-Backend Communication**
   - POST request to agent API
   - Show loading spinner during generation
   - Display response in formatted code block
   - Handle errors with user-friendly messages

4. **Create First Agent Workflow**
   - User enters: "Generate POM for login page at example.com"
   - Agent uses Playwright MCP to navigate
   - Agent inspects page elements
   - Agent generates Python POM class
   - Agent writes file via Filesystem MCP
   - Frontend displays generated code

5. **Test Complete Flow**
   - Enter various prompts
   - Verify POM files are generated
   - Check file structure is correct
   - Validate code quality

**Deliverable**: Working demo - prompt to POM file in one click

---

### Day 11-12: POM Generation Quality

**Objective**: Improve quality of generated Page Object Models

#### Key Tasks:
1. **Enhance Agent Prompts**
   - Add system prompt for POM best practices
   - Include examples of good POM structure
   - Define locator selection strategy (data-testid > CSS > XPath)

2. **Implement Multi-Step Analysis**
   - Agent navigates to page
   - Agent identifies all interactive elements
   - Agent extracts stable locators
   - Agent organizes into logical groups

3. **Generate Complete POM Structure**
   - Python class with proper imports
   - Docstrings for each method
   - Type hints for parameters
   - Both sync and async versions

4. **Add File Organization**
   - Create pages/ directory
   - Generate __init__.py files
   - Create conftest.py with fixtures
   - Organize related POMs in subfolders

5. **Quality Validation**
   - Test generated POMs on multiple sites
   - Check locator uniqueness
   - Verify code follows Python conventions
   - Ensure imports are correct

**Deliverable**: Production-quality POM files generated automatically

---

### Day 13-14: File Management & Sessions

**Objective**: Allow users to manage files and save their work

#### Key Tasks:
1. **Build File Browser UI**
   - Tree view of workspace
   - Show all generated files
   - Click to preview file contents
   - Syntax highlighting for Python code

2. **Add File Operations**
   - Download individual files
   - Copy code to clipboard
   - Delete files
   - Rename files
   - Create new folders

3. **Implement Session Persistence**
   - Save conversation history to database/JSON
   - Allow resuming previous sessions
   - Show list of recent projects
   - Restore context on session load

4. **Project Management**
   - Create new project
   - Switch between projects
   - Each project has isolated workspace
   - Export project as ZIP

**Deliverable**: Users can manage all generated files and projects

---

## Phase 3: Enhanced Features (Week 3-4)
**LLM: Switch to Claude 3.5 Haiku (Use $5 free credits)**

### Week 3: Advanced Agent Capabilities

**Why switch to Claude now?**
- Groq was perfect for building infrastructure
- Claude excels at complex code generation
- Better understanding of Playwright patterns
- More reliable multi-step reasoning
- $5 credits sufficient for this phase

#### Key Tasks:
1. **Update Agent Configuration**
   - Add Anthropic API key to .env
   - Switch LLM_PROVIDER to 'claude'
   - Test connection with free credits
   - Monitor credit usage via Anthropic console

2. **Multi-Page Workflow**
   - Agent navigates through multiple pages
   - Generates interconnected POMs
   - Creates complete test suite structure
   - Links POMs together logically

3. **Intelligent Element Selection**
   - Agent explains locator choices
   - Provides alternative locators
   - Ranks locators by stability
   - Validates uniqueness across page

4. **Advanced POM Features**
   - Wait conditions for dynamic elements
   - Error handling in methods
   - Reusable component extraction
   - Page state validation methods

5. **Agent Reasoning Transparency**
   - Show agent's thought process
   - Display step-by-step actions
   - Log tool calls and responses
   - Explain why certain decisions were made

**Deliverable**: Agent handles complex multi-page applications

---

### Week 4: Testing & Script Execution

#### Key Tasks:
1. **Implement Script Execution Engine**
   - Run generated Playwright scripts in Docker sandbox
   - Capture stdout/stderr logs
   - Take screenshots during execution
   - Report success/failure

2. **Generate Test Cases**
   - Create pytest test files using POMs
   - Add fixtures for browser setup
   - Include assertions for validation
   - Generate test data when needed

3. **Validation & Quality Checks**
   - Verify all locators work
   - Check for duplicate methods
   - Run pylint on generated code
   - Suggest improvements

4. **Export & Documentation**
   - Export complete project structure
   - Generate README with setup instructions
   - Create requirements.txt
   - Add usage examples

**Deliverable**: Executable test projects with documentation

---

## Phase 4: Production Preparation (Week 5)
**LLM: Switch to Gemini Free Tier (1500 req/day)**

### Why Gemini for Production?

- **Completely free**: 1500 requests/day forever
- **No credit card needed**: True free tier
- **Sufficient for 3-5 users**: ~300 requests/user/day
- **Good quality**: Gemini 1.5 Flash is solid for code gen
- **Cost-effective scaling**: Only pay if you exceed free tier

#### Key Tasks:

1. **Add Gemini API Support**
   - Install Google Generative AI SDK
   - Add Gemini to agent configuration
   - Test free tier limits
   - Implement rate limiting

2. **Multi-LLM Architecture**
   - Support all three LLMs (Groq, Claude, Gemini)
   - Allow switching via config
   - Track usage per LLM
   - Fallback mechanism if one fails

3. **Production Hardening**
   - Add user authentication (JWT)
   - Implement rate limiting per user
   - Add request logging
   - Monitor API usage

4. **Deployment Preparation**
   - Create deployment guide
   - Docker Compose for production
   - Environment variable documentation
   - Backup and restore procedures

5. **Cost Management Dashboard**
   - Show API usage statistics
   - Track requests per user
   - Display remaining free tier quota
   - Alerts when approaching limits

**Deliverable**: Production-ready application with free LLM tier

---

## Incremental Release Plan

### **Alpha (v0.1.0) - End of Week 2**
**Using: Groq (Free)**

**Features**:
- ✅ Basic prompt → POM generation
- ✅ Single page analysis
- ✅ File viewing in UI
- ✅ Docker-based setup

**Quality Bar**: Works for simple login pages

**Cost**: $0 (Groq free tier)

---

### **Beta (v0.2.0) - End of Week 3**
**Using: Claude 3.5 Haiku ($5 credits)**

**Features**:
- ✅ Multi-page workflows
- ✅ Advanced POM structure
- ✅ Session management
- ✅ File operations

**Quality Bar**: Production-quality POMs

**Cost**: ~$2-3 from free credits

---

### **Release Candidate (v0.3.0) - End of Week 4**
**Using: Claude (remaining credits)**

**Features**:
- ✅ Script execution
- ✅ Test generation
- ✅ Project export
- ✅ Validation tools

**Quality Bar**: Complete test projects

**Cost**: ~$1-2 from remaining credits

---

### **Production (v1.0.0) - Week 5+**
**Using: Gemini Free Tier**

**Features**:
- ✅ All features stable
- ✅ Multi-user support
- ✅ Authentication
- ✅ Production deployment

**Quality Bar**: Enterprise-ready

**Cost**: $0 (Gemini 1500 req/day free)

---

## Cost Summary: Total Spend $0

### **Complete 5-Week Development Budget**

| Week | LLM | Cost | Usage |
|------|-----|------|-------|
| **1-2** | Groq | **$0** | Unlimited free tier |
| **3** | Claude | **$0** | $5 free credits (use $2-3) |
| **4** | Claude | **$0** | Remaining $2-3 credits |
| **5+** | Gemini | **$0** | 1500 req/day free forever |

**Total Development Cost**: **$0**

**Post-Launch (3-5 users)**: 
- Continue with Gemini free tier: **$0/month**
- If exceed 1500 req/day: Switch to paid tier (~$5-10/month)

---

## Free Tier Limits & Management

### **Groq (Weeks 1-2)**
- **Limit**: 30 requests/minute
- **Strategy**: Perfect for iterative development
- **Monitoring**: Check console.groq.com dashboard

### **Claude (Weeks 3-4)**
- **Limit**: $5 credit (~400-600 generations)
- **Strategy**: Use only for quality testing, not debugging
- **Monitoring**: Watch console.anthropic.com credits

### **Gemini (Week 5+)**
- **Limit**: 1500 requests/day
- **Strategy**: Production deployment for small teams
- **Monitoring**: Google AI Studio dashboard

### **Rate Limiting Strategy**
- Add request counter in application
- Show users remaining quota
- Implement cooldown periods if approaching limits
- Cache frequent responses when possible

---

## Success Metrics by Phase

### **Phase 1 (Week 1) - Infrastructure**
- ✅ All APIs connected (Groq working)
- ✅ MCP servers operational
- ✅ Zero setup issues for new developer
- ✅ Cost: $0

### **Phase 2 (Week 2) - Core Functionality**
- ✅ End-to-end POM generation working
- ✅ Generated code is syntactically correct
- ✅ File management functional
- ✅ Cost: $0

### **Phase 3 (Weeks 3-4) - Quality**
- ✅ POMs pass code review standards
- ✅ Complex multi-page apps supported
- ✅ Generated tests execute successfully
- ✅ Cost: $0 (using free credits)

### **Phase 4 (Week 5+) - Production**
- ✅ 3-5 users can use concurrently
- ✅ Stable on Gemini free tier
- ✅ Documentation complete
- ✅ Cost: $0/month ongoing

---

## Risk Mitigation

### **Free Tier Exhaustion**

**Risk**: Run out of free credits during development

**Mitigation**:
1. Track API usage daily
2. Use Groq for all debugging (unlimited)
3. Only use Claude for final testing
4. If Claude credits run out early, use OpenAI $5 credits
5. Gemini free tier should never run out (1500/day is huge)

### **API Rate Limits**

**Risk**: Hit rate limits during heavy testing

**Mitigation**:
1. Implement exponential backoff
2. Add request queuing system
3. Spread testing across multiple days
4. Use multiple free tier accounts if needed (dev/staging/prod)

### **Quality Issues with Free Models**

**Risk**: Free tier models produce lower quality code

**Mitigation**:
1. This is not a concern - all three options (Groq/Claude/Gemini) are high-quality
2. Groq runs Llama 3.1 70B (excellent code gen)
3. Claude 3.5 Haiku is very capable
4. Gemini 1.5 Flash is Google's production model
5. Can always upgrade to paid tiers later if needed

---

## Quick Start Checklist

**Before Day 1:**
- [ ] Create Groq account → Get API key (free, no card)
- [ ] Create Anthropic account → Get $5 credits (no card initially)
- [ ] Create Google AI account → Get Gemini key (free forever)
- [ ] Install Docker Desktop
- [ ] Install Node.js v18+
- [ ] Install Python 3.11+
- [ ] Install VS Code with Docker extension
- [ ] Create project folder
- [ ] Initialize git repository

**Budget Verification:**
- [ ] Groq: Verify "Free" tier active
- [ ] Claude: Confirm $5 credit balance
- [ ] Gemini: Verify 1500 req/day quota

---

## Next Steps

### **Immediate Actions (Day 0)**
1. Sign up for all three LLM services today
2. Save all API keys in password manager
3. Read Groq API documentation
4. Set up development environment
5. Create project folder structure

### **Day 1 Morning**
1. Initialize git repository
2. Create docker-compose.yml
3. Write .env with Groq API key
4. Test Groq connection with simple script
5. Start building agent-backend container

**You're ready to build with $0 budget! The entire tool can be developed and deployed without spending any money.**