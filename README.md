# Personal AI Assistant with Tool Orchestration

## Table of Contents
1. [Product Overview](#product-overview)
2. [Product Requirements](#product-requirements)
3. [Technical Architecture](#technical-architecture)
4. [AI Backend Deep Dive](#ai-backend-deep-dive)
5. [Implementation Details](#implementation-details)
6. [Deployment Strategy](#deployment-strategy)
7. [Cost Optimization](#cost-optimization)

## Product Overview

A sophisticated personal AI assistant that orchestrates multiple tools through an agentic framework, showcasing production-ready AI/ML engineering with a focus on Google Suite integration, real-time user interaction, and cost-effective LLM usage.

## Product Requirements

### Core Features

#### 1. Multi-Account Google Integration
- **Multiple Account Support**: Connect and manage multiple Gmail and Calendar accounts
- **Full CRUD Operations**: Read, create, update, and delete capabilities with approval workflow
- **Unified Interface**: Single dashboard to manage all connected accounts
- **OAuth 2.0 Authentication**: Secure account linking with token refresh

#### 2. Intelligent Task Execution
- **Natural Language Processing**: Understand complex, multi-step requests
- **Workflow Orchestration**: Execute sophisticated multi-step workflows
- **Action Preview System**: Show users exactly what will happen before execution
- **Real-time Status Updates**: Live progress tracking with WebSocket updates

#### 3. Smart Context Management
- **Persistent Memory**: Maintain conversation context across sessions
- **Cross-Account Intelligence**: Correlate information across different accounts
- **Temporal Understanding**: Process relative time references ("last week", "tomorrow")
- **Learning System**: Improve responses based on user preferences and patterns

### Key User Workflows

1. **Email Management**
   - "Summarize all emails about Project X and draft a response"
   - "Find all unread emails from my manager across all accounts"
   - "Archive all promotional emails older than 30 days"

2. **Meeting Coordination**
   - "Schedule a meeting with everyone who emailed about the budget review"
   - "Find a free slot next week for a 2-hour workshop with the engineering team"
   - "Reschedule all tomorrow's meetings to next week"

3. **Daily Planning**
   - "What should I focus on today based on my emails and calendar?"
   - "Create a priority list from my unread emails"
   - "Block time for deep work based on my meeting schedule"

4. **Cross-Account Tasks**
   - "Move all meetings from personal calendar to work calendar next week"
   - "Forward all emails about Project Alpha from personal to work email"
   - "Sync availability across all my calendars"

## Technical Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend (React)                         │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────────────┐    │
│  │ Chat UI     │  │ Action       │  │ Account Manager    │    │
│  │ + Agent     │  │ Approval UI  │  │ + OAuth Flow       │    │
│  │ Thinking    │  │              │  │                    │    │
│  └─────────────┘  └──────────────┘  └────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
                                │
                    WebSocket + REST API
                                │
┌─────────────────────────────────────────────────────────────────┐
│                    Backend (FastAPI + Async)                     │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────────────┐    │
│  │ Session Mgr │  │ Auth Service │  │ Action Queue       │    │
│  │             │  │ + OAuth      │  │ + Approval System  │    │
│  └─────────────┘  └──────────────┘  └────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
                                │
┌─────────────────────────────────────────────────────────────────┐
│                         AI Backend                               │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │                    Orchestration Layer                    │  │
│  │  ┌─────────────┐  ┌──────────────┐  ┌──────────────┐   │  │
│  │  │ LangGraph   │  │ CrewAI       │  │ MCP Manager  │   │  │
│  │  │ Supervisor  │  │ Crews        │  │              │   │  │
│  │  └─────────────┘  └──────────────┘  └──────────────┘   │  │
│  └─────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │                      Agent Layer                         │  │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌──────────┐  │  │
│  │  │ Email   │  │Calendar │  │Planner  │  │Analyzer  │  │  │
│  │  │ Agent   │  │ Agent   │  │ Agent   │  │ Agent    │  │  │
│  │  └─────────┘  └─────────┘  └─────────┘  └──────────┘  │  │
│  └─────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │                      MCP Servers                         │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │  │
│  │  │ Gmail MCP    │  │ Calendar MCP │  │ Memory MCP   │  │  │
│  │  │ Server       │  │ Server       │  │ Server       │  │  │
│  │  └──────────────┘  └──────────────┘  └──────────────┘  │  │
│  └─────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │                   Infrastructure                         │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────┐ │  │
│  │  │ Qdrant   │  │ Redis    │  │ Postgres │  │ Ollama │ │  │
│  │  │ Vector   │  │ Cache    │  │ Storage  │  │ LLM    │ │  │
│  │  └──────────┘  └──────────┘  └──────────┘  └────────┘ │  │
│  └─────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### Component Breakdown

#### Frontend Layer
- **React 18+** with TypeScript
- **Tailwind CSS** for styling
- **Socket.io Client** for real-time updates
- **React Query** for API state management
- **Zustand** for global state

#### Backend Layer
- **FastAPI** with full async support
- **Pydantic** for data validation
- **SQLAlchemy** with async sessions
- **Alembic** for migrations
- **Celery** for background tasks

#### AI Backend Layer
- **LangGraph** for stateful orchestration
- **CrewAI** for multi-agent coordination
- **MCP SDK** for tool abstraction
- **Ollama** for local LLM inference
- **LangChain** for additional utilities

## AI Backend Deep Dive

### 1. Orchestration Layer

#### LangGraph Supervisor

The supervisor acts as the central coordinator for all AI operations:

```python
class AssistantSupervisor:
    """Main orchestrator for the AI assistant"""

    def __init__(self):
        self.graph = StateGraph(ConversationState)
        self.crews = CrewRegistry()
        self.mcp_manager = MCPManager()

    async def process_request(self, user_input: str, context: Context) -> Response:
        # 1. Intent Classification
        intent = await self.classify_intent(user_input)

        # 2. Route to appropriate crew
        crew = self.crews.get_crew(intent.domain)

        # 3. Generate execution plan
        plan = await crew.create_plan(user_input, context)

        # 4. Execute with state tracking
        async for state in self.execute_plan(plan):
            yield state
```

#### CrewAI Integration

Specialized crews handle domain-specific tasks:

```python
# Email Management Crew
class EmailCrew(Crew):
    agents = [
        Agent(
            role="Email Analyst",
            goal="Understand email context and extract key information",
            tools=[EmailSearchTool(), EmailReadTool()],
            llm=ollama_llm
        ),
        Agent(
            role="Email Writer",
            goal="Draft professional responses based on context",
            tools=[EmailDraftTool(), TemplateLibraryTool()],
            llm=ollama_llm
        ),
        Agent(
            role="Email Organizer",
            goal="Categorize and manage email workflows",
            tools=[LabelTool(), FilterTool(), ArchiveTool()],
            llm=ollama_llm
        )
    ]

# Calendar Management Crew
class CalendarCrew(Crew):
    agents = [
        Agent(
            role="Schedule Analyst",
            goal="Analyze calendars and find optimal meeting times",
            tools=[CalendarSearchTool(), ConflictCheckerTool()],
            llm=ollama_llm
        ),
        Agent(
            role="Meeting Coordinator",
            goal="Handle meeting logistics and invitations",
            tools=[EventCreatorTool(), InviteSenderTool()],
            llm=ollama_llm
        ),
        Agent(
            role="Time Optimizer",
            goal="Suggest schedule improvements",
            tools=[PatternAnalyzerTool(), OptimizationTool()],
            llm=ollama_llm
        )
    ]

# Planning and Analysis Crew
class PlanningCrew(Crew):
    agents = [
        Agent(
            role="Task Extractor",
            goal="Identify actionable items from communications",
            tools=[NLPExtractorTool(), PriorityAnalyzerTool()],
            llm=ollama_llm
        ),
        Agent(
            role="Workflow Designer",
            goal="Create efficient multi-step execution plans",
            tools=[WorkflowBuilderTool(), DependencyAnalyzerTool()],
            llm=ollama_llm
        )
    ]
```

#### MCP Manager

Handles dynamic MCP server management:

```python
class MCPManager:
    def __init__(self):
        self.servers = {}
        self.connection_pool = AsyncConnectionPool()

    async def register_server(self, server_config: MCPServerConfig):
        """Dynamically register MCP servers"""
        server = await MCPServer.create(server_config)
        self.servers[server_config.name] = server

    async def execute_tool(self, tool_name: str, params: dict) -> Any:
        """Route tool execution to appropriate MCP server"""
        server = self.find_server_for_tool(tool_name)
        return await server.execute(tool_name, params)
```

### 2. Agent Layer Architecture

Base agent pattern for consistency:

```python
class BaseAgent:
    """Base class for all agents"""

    def __init__(self, role: str, tools: List[Tool], memory: VectorMemory):
        self.role = role
        self.tools = tools
        self.memory = memory
        self.llm = OllamaLLM(model="llama3.2")

    async def plan(self, task: Task, context: Context) -> Plan:
        """Create execution plan for the task"""
        # Retrieve relevant memories
        memories = await self.memory.search(task.description)

        # Generate plan using LLM
        prompt = self.build_planning_prompt(task, context, memories)
        plan = await self.llm.generate(prompt)

        return self.parse_plan(plan)

    async def execute(self, plan: Plan) -> AsyncIterator[ActionResult]:
        """Execute plan with approval checks"""
        for step in plan.steps:
            if step.requires_approval:
                approval = await self.request_approval(step)
                if not approval:
                    continue

            result = await self.execute_step(step)
            await self.memory.store(step, result)
            yield result

    async def reflect(self, results: List[ActionResult]) -> Insights:
        """Learn from execution results"""
        return await self.analyze_performance(results)
```

### 3. MCP Server Implementation

#### Gmail MCP Server

```python
class GmailMCPServer:
    """MCP server for Gmail operations"""

    def __init__(self):
        self.tools = {
            "search_emails": self.search_emails,
            "read_email": self.read_email,
            "send_email": self.send_email,
            "create_draft": self.create_draft,
            "modify_labels": self.modify_labels
        }

    async def search_emails(
        self,
        query: str,
        account_id: str,
        date_range: Optional[DateRange] = None
    ) -> List[EmailSummary]:
        """Search emails with advanced query syntax"""
        service = await self.get_gmail_service(account_id)

        # Build Gmail query
        gmail_query = self.build_query(query, date_range)

        # Execute search
        results = await service.users().messages().list(
            userId='me',
            q=gmail_query
        ).execute()

        return await self.process_results(results)

    async def send_email(
        self,
        draft: EmailDraft,
        account_id: str
    ) -> EmailResult:
        """Send email (requires approval)"""
        # This will be intercepted by approval system
        return await self.execute_with_approval(
            self._send_email_impl,
            draft,
            account_id
        )
```

#### Calendar MCP Server

```python
class CalendarMCPServer:
    """MCP server for Calendar operations"""

    def __init__(self):
        self.tools = {
            "get_events": self.get_events,
            "find_free_slots": self.find_free_slots,
            "create_event": self.create_event,
            "update_event": self.update_event,
            "check_conflicts": self.check_conflicts
        }

    async def find_free_slots(
        self,
        attendees: List[str],
        duration: int,
        constraints: ScheduleConstraints
    ) -> List[TimeSlot]:
        """Find available time slots across multiple calendars"""
        # Get calendars for all attendees
        calendars = await self.get_calendars_for_attendees(attendees)

        # Find busy times
        busy_times = await self.get_busy_times(calendars, constraints.date_range)

        # Calculate free slots
        free_slots = self.calculate_free_slots(
            busy_times,
            duration,
            constraints
        )

        return self.rank_slots_by_preference(free_slots)
```

#### Memory MCP Server

```python
class MemoryMCPServer:
    """MCP server for memory operations"""

    def __init__(self, vector_db: Qdrant):
        self.vector_db = vector_db
        self.tools = {
            "store_context": self.store_context,
            "retrieve_context": self.retrieve_context,
            "update_preferences": self.update_preferences,
            "get_patterns": self.get_patterns
        }

    async def store_context(
        self,
        conversation_id: str,
        context: ConversationContext
    ) -> None:
        """Store conversation context with embeddings"""
        # Generate embeddings
        embeddings = await self.generate_embeddings(context.summary)

        # Store in vector DB
        await self.vector_db.upsert(
            collection_name="conversations",
            points=[{
                "id": conversation_id,
                "vector": embeddings,
                "payload": context.dict()
            }]
        )
```

### 4. Workflow Execution Engine

The core engine that orchestrates everything:

```python
class WorkflowEngine:
    """Main workflow execution engine"""

    def __init__(self):
        self.supervisor = AssistantSupervisor()
        self.approval_queue = ApprovalQueue()
        self.notification_service = NotificationService()

    async def execute_workflow(
        self,
        natural_query: str,
        user_context: UserContext
    ) -> WorkflowResult:
        """Execute a complete workflow from natural language input"""

        # Phase 1: Understanding
        await self.notify("🤔 Understanding your request...")
        intent = await self.supervisor.understand_query(natural_query)

        # Phase 2: Planning
        await self.notify("📋 Creating execution plan...")
        plan = await self.supervisor.create_plan(intent, user_context)

        # Show plan to user
        await self.show_plan(plan)

        # Phase 3: Approval (if needed)
        if plan.requires_approval:
            await self.notify("⏳ Waiting for your approval...")
            approval = await self.approval_queue.request(plan)
            if not approval:
                return WorkflowResult(status="cancelled")

        # Phase 4: Execution
        results = []
        async for action in self.supervisor.execute_plan(plan):
            await self.notify(f"⚡ Executing: {action.description}")

            if action.requires_approval:
                action_approval = await self.approval_queue.request(action)
                if not action_approval:
                    continue

            result = await action.execute()
            results.append(result)
            await self.notify(f"✅ Completed: {result.summary}")

        # Phase 5: Learning
        await self.supervisor.learn_from_execution(plan, results)

        return WorkflowResult(
            status="completed",
            results=results,
            insights=await self.generate_insights(results)
        )
```

### 5. Memory and Context System

Sophisticated memory management:

```python
class MemorySystem:
    """Multi-tier memory system"""

    def __init__(self):
        self.short_term = RedisMemory()      # Current session
        self.long_term = QdrantMemory()      # Historical context
        self.episodic = PostgreSQLMemory()   # Specific interactions
        self.semantic = EmbeddingMemory()    # Concept relationships

    async def build_context(self, query: str, user_id: str) -> Context:
        """Build comprehensive context for query"""

        # Get recent interactions
        recent = await self.short_term.get_recent(user_id, limit=10)

        # Search relevant historical context
        relevant = await self.long_term.search(
            query=query,
            user_id=user_id,
            limit=20
        )

        # Find behavioral patterns
        patterns = await self.episodic.get_patterns(
            user_id=user_id,
            pattern_types=["preferences", "schedules", "contacts"]
        )

        # Get semantic relationships
        concepts = await self.semantic.find_related_concepts(query)

        # Merge all context sources
        return ContextBuilder.merge(
            recent=recent,
            relevant=relevant,
            patterns=patterns,
            concepts=concepts
        )

    async def learn_from_interaction(
        self,
        interaction: Interaction,
        feedback: Optional[Feedback] = None
    ) -> None:
        """Update all memory tiers based on interaction"""

        # Update short-term memory
        await self.short_term.add(interaction)

        # Extract and store embeddings
        embeddings = await self.generate_embeddings(interaction)
        await self.long_term.store(embeddings)

        # Update episodic memory
        await self.episodic.record_episode(interaction, feedback)

        # Update semantic relationships
        await self.semantic.update_relationships(interaction)
```

## Implementation Details

### API Design

#### REST Endpoints

```python
# Account Management
POST   /api/accounts/connect         # Connect new Google account
DELETE /api/accounts/{account_id}    # Disconnect account
GET    /api/accounts                 # List connected accounts

# Conversation
POST   /api/chat                     # Send message
GET    /api/chat/history             # Get conversation history
WS     /ws/chat                      # WebSocket for real-time

# Approvals
GET    /api/approvals/pending        # Get pending approvals
POST   /api/approvals/{id}/approve   # Approve action
POST   /api/approvals/{id}/reject    # Reject action

# Settings
GET    /api/settings                 # Get user settings
PATCH  /api/settings                 # Update settings
```

#### WebSocket Events

```python
# Server -> Client
{
    "type": "agent_thinking",
    "data": {
        "agent": "Email Analyst",
        "thought": "Searching for emails about Project X..."
    }
}

{
    "type": "approval_required",
    "data": {
        "id": "approval_123",
        "action": "send_email",
        "details": {...}
    }
}

{
    "type": "execution_update",
    "data": {
        "step": 3,
        "total": 5,
        "description": "Creating calendar event..."
    }
}

# Client -> Server
{
    "type": "approve_action",
    "data": {
        "approval_id": "approval_123",
        "approved": true
    }
}
```

### Database Schema

```sql
-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    settings JSONB DEFAULT '{}'
);

-- Connected accounts
CREATE TABLE connected_accounts (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    provider VARCHAR(50) NOT NULL,
    account_email VARCHAR(255) NOT NULL,
    access_token TEXT,
    refresh_token TEXT,
    expires_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Conversations
CREATE TABLE conversations (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    started_at TIMESTAMP DEFAULT NOW(),
    ended_at TIMESTAMP,
    summary TEXT
);

-- Messages
CREATE TABLE messages (
    id UUID PRIMARY KEY,
    conversation_id UUID REFERENCES conversations(id),
    role VARCHAR(50) NOT NULL,
    content TEXT NOT NULL,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW()
);

-- Action approvals
CREATE TABLE action_approvals (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    action_type VARCHAR(100) NOT NULL,
    action_details JSONB NOT NULL,
    status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT NOW(),
    resolved_at TIMESTAMP
);

-- Execution logs
CREATE TABLE execution_logs (
    id UUID PRIMARY KEY,
    conversation_id UUID REFERENCES conversations(id),
    plan JSONB NOT NULL,
    results JSONB,
    started_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP
);
```

### Security Considerations

1. **OAuth Token Management**
   - Encrypted storage of tokens
   - Automatic refresh before expiration
   - Secure token transmission

2. **Action Approval System**
   - All state-changing operations require explicit approval
   - Timeout for pending approvals
   - Audit trail for all actions

3. **Data Isolation**
   - Strict user data separation
   - No cross-user data access
   - Account-level permissions

4. **API Security**
   - JWT-based authentication
   - Rate limiting per user
   - Input validation and sanitization

## Deployment Strategy

### Local Development

```yaml
# docker-compose.yml
version: '3.8'

services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: assistant
      POSTGRES_USER: assistant
      POSTGRES_PASSWORD: local_password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  qdrant:
    image: qdrant/qdrant
    ports:
      - "6333:6333"
    volumes:
      - qdrant_data:/qdrant/storage

  ollama:
    image: ollama/ollama
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]

  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://assistant:local_password@postgres/assistant
      - REDIS_URL=redis://redis:6379
      - QDRANT_URL=http://qdrant:6333
      - OLLAMA_URL=http://ollama:11434
    depends_on:
      - postgres
      - redis
      - qdrant
      - ollama

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - REACT_APP_API_URL=http://localhost:8000
    depends_on:
      - backend

volumes:
  postgres_data:
  qdrant_data:
  ollama_data:
```

### Production Deployment (Single EC2)

```bash
# EC2 Instance Setup Script
#!/bin/bash

# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker and Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker ubuntu

# Install NVIDIA drivers (if GPU instance)
sudo apt install -y nvidia-driver-470

# Clone repository
git clone https://github.com/yourusername/ai-assistant.git
cd ai-assistant

# Set up environment variables
cp .env.example .env
# Edit .env with production values

# Pull and start services
docker-compose -f docker-compose.prod.yml pull
docker-compose -f docker-compose.prod.yml up -d

# Set up SSL with Certbot
sudo snap install --classic certbot
sudo certbot --nginx -d yourdomain.com

# Set up monitoring
docker run -d \
  --name=grafana \
  -p 3001:3000 \
  grafana/grafana

# Set up automatic backups
echo "0 2 * * * /home/ubuntu/backup.sh" | crontab -
```

### Scaling Path

1. **Phase 1: Single EC2 (Current)**
   - All services on one instance
   - Suitable for up to 100 concurrent users

2. **Phase 2: Service Separation**
   - Database on RDS
   - Redis on ElastiCache
   - Application on EC2/ECS

3. **Phase 3: Microservices**
   - Separate MCP servers
   - Queue-based architecture
   - Auto-scaling groups

## Cost Optimization

### LLM Usage Strategy

1. **Local Models (Ollama)**
   - Primary: Llama 3.2 (3B) for general tasks
   - Secondary: Phi-3 for lightweight operations
   - Code: CodeLlama for code-related tasks

2. **Cloud LLM Usage**
   - Only for complex multi-step reasoning
   - Cached responses for common queries
   - Batch processing when possible

### Resource Optimization

```python
class CostOptimizer:
    """Minimize API and compute costs"""

    def __init__(self):
        self.cache = RedisCache()
        self.usage_tracker = UsageTracker()

    async def optimize_llm_call(self, prompt: str, context: dict) -> str:
        # Check cache first
        cached = await self.cache.get(prompt)
        if cached:
            return cached

        # Determine optimal model
        model = self.select_model(prompt, context)

        # Execute with monitoring
        start_time = time.time()
        response = await model.generate(prompt)
        cost = self.calculate_cost(model, time.time() - start_time)

        # Track usage
        await self.usage_tracker.record(model, cost)

        # Cache if appropriate
        if cost > 0.01:  # Cache expensive calls
            await self.cache.set(prompt, response)

        return response
```

### Monitoring and Alerts

```python
# Cost monitoring configuration
COST_ALERTS = {
    "daily_limit": 10.0,      # $10/day
    "hourly_spike": 2.0,      # $2/hour
    "per_user_daily": 0.50,   # $0.50/user/day
}

# Performance monitoring
PERFORMANCE_METRICS = {
    "api_response_time": 200,  # ms
    "workflow_completion": 5000,  # ms
    "approval_timeout": 30000,  # ms
}
```

## Next Steps

1. **Week 1-2: Core Infrastructure**
   - Set up Docker environment
   - Implement basic FastAPI backend
   - Create initial database schema

2. **Week 3-4: MCP Integration**
   - Build Gmail MCP server
   - Build Calendar MCP server
   - Implement approval system

3. **Week 5-6: AI Components**
   - Set up CrewAI agents
   - Implement LangGraph supervisor
   - Create memory system

4. **Week 7-8: Frontend & Polish**
   - Build React frontend
   - Implement real-time updates
   - Add monitoring and logging

5. **Week 9-10: Testing & Deployment**
   - Comprehensive testing
   - Performance optimization
   - Deploy to EC2

This architecture showcases your expertise in:
- Production-ready AI/ML systems
- Modern agent frameworks (CrewAI, LangGraph, MCP)
- Scalable async architectures
- Cost-conscious design
- Full-stack implementation skills
- DevOps best practices