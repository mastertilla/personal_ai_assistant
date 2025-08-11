# Personal AI Assistant - LangGraph Implementation Plan

## Executive Summary

A production-ready personal AI assistant built with LangGraph orchestration, showcasing enterprise-grade workflow automation, Google Suite integration, and sophisticated approval systems. This implementation prioritizes **deterministic, testable, resumable workflows** over framework complexity.

**Key Engineering Highlights:**
- LangGraph-based stateful workflows with checkpointing
- Enterprise-grade approval system with diff previews
- Multi-account Google integration with proper isolation
- Production observability with OpenTelemetry
- Cost-optimized LLM usage with circuit breakers

## Product Overview

### Core Value Proposition
Transform natural language requests into sophisticated multi-step workflows across Google Suite, with enterprise-grade approval controls and full auditability.

### Key Workflows
1. **Email Management**: "Summarize emails about Project X and draft responses"
2. **Meeting Coordination**: "Schedule a meeting with everyone who emailed about the budget"
3. **Daily Planning**: "What should I focus on today based on my emails and calendar?"
4. **Cross-Account Operations**: "Move all personal events to work calendar next week"

## Technical Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    Frontend (React + TypeScript)                 │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────────────┐    │
│  │ Chat UI     │  │ Diff Preview │  │ Account Manager    │    │
│  │ + Workflow  │  │ + Approval   │  │ + OAuth Flow       │    │
│  │ Status      │  │ Controls     │  │                    │    │
│  └─────────────┘  └──────────────┘  └────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
                                │
                    WebSocket + REST API
                                │
┌─────────────────────────────────────────────────────────────────┐
│                Backend (FastAPI + Async + Queue)                 │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────────────┐    │
│  │ Session Mgr │  │ Auth Service │  │ Background Queue   │    │
│  │ + WebSocket │  │ + Multi-OAuth│  │ + Idempotency      │    │
│  └─────────────┘  └──────────────┘  └────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
                                │
┌─────────────────────────────────────────────────────────────────┐
│                   AI Backend (LangGraph Core)                    │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │                LangGraph Workflow Engine                  │  │
│  │  ┌──────────┐ ┌───────────┐ ┌──────────┐ ┌─────────┐  │  │
│  │  │ Intent   │ │ Planning  │ │ Execution│ │ Approval│  │  │
│  │  │ Node     │ │ Node      │ │ Nodes    │ │ Nodes   │  │  │
│  │  └──────────┘ └───────────┘ └──────────┘ └─────────┘  │  │
│  │                                                         │  │
│  │  ┌─────────────────────────────────────────────────┐  │  │
│  │  │        Checkpoint & State Management            │  │  │
│  │  └─────────────────────────────────────────────────┘  │  │
│  └─────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │                    MCP Tool Layer                        │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │  │
│  │  │ Gmail Tools  │  │ Calendar     │  │ Memory Tools │  │  │
│  │  │ (Rate Limited│  │ Tools        │  │              │  │  │
│  │  │ + Retries)   │  │              │  │              │  │  │
│  │  └──────────────┘  └──────────────┘  └──────────────┘  │  │
│  └─────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │                Infrastructure Layer                      │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────┐ │  │
│  │  │ Postgres │  │ Redis    │  │ Qdrant   │  │ Ollama │ │  │
│  │  │ (State + │  │ (Cache + │  │ (Vectors)│  │ (Local │ │  │
│  │  │ Audit)   │  │ Session) │  │          │  │ LLM)   │ │  │
│  │  └──────────┘  └──────────┘  └──────────┘  └────────┘ │  │
│  └─────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### Core Design Principles

1. **Stateful Workflows**: Every step is checkpointed and resumable
2. **Deterministic Execution**: Same input always produces same workflow plan
3. **Approval-First**: All state-changing operations require explicit user consent
4. **Account Isolation**: Strict per-user, per-account data boundaries
5. **Cost Consciousness**: Local models for routing/summaries, cloud for complex reasoning

## Folder Structure (Production-Ready)

```
personal-ai-assistant/
│
├── .github/
│   └── workflows/
│       ├── backend-ci.yml
│       ├── frontend-ci.yml
│       └── deploy.yml
│
├── backend/
│   ├── alembic/
│   │   ├── versions/
│   │   └── alembic.ini
│   │
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── config.py
│   │   │
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── deps.py
│   │   │   ├── v1/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── auth.py
│   │   │   │   ├── accounts.py
│   │   │   │   ├── workflows.py      # NEW: Workflow execution endpoints
│   │   │   │   ├── approvals.py
│   │   │   │   └── health.py
│   │   │   └── websocket/
│   │   │       ├── __init__.py
│   │   │       ├── connection_manager.py
│   │   │       └── workflow_updates.py
│   │   │
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   ├── database.py
│   │   │   ├── exceptions.py
│   │   │   ├── redis.py
│   │   │   ├── security.py
│   │   │   ├── tracing.py           # NEW: OpenTelemetry setup
│   │   │   └── logging.py
│   │   │
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── account.py
│   │   │   ├── workflow.py          # NEW: Workflow execution tracking
│   │   │   ├── checkpoint.py        # NEW: LangGraph state persistence
│   │   │   ├── approval.py
│   │   │   └── audit.py
│   │   │
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── account.py
│   │   │   ├── workflow.py          # NEW: Workflow DTOs
│   │   │   ├── approval.py
│   │   │   └── common.py
│   │   │
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── auth_service.py
│   │   │   ├── google_service.py    # Enhanced multi-account OAuth
│   │   │   ├── approval_service.py
│   │   │   ├── audit_service.py
│   │   │   └── cost_service.py      # NEW: Cost tracking and limits
│   │   │
│   │   └── ai/
│   │       ├── __init__.py
│   │       ├── config.py
│   │       │
│   │       ├── workflows/            # LangGraph workflow definitions
│   │       │   ├── __init__.py
│   │       │   ├── base_workflow.py
│   │       │   ├── email_workflow.py
│   │       │   ├── calendar_workflow.py
│   │       │   ├── planning_workflow.py
│   │       │   └── mixed_workflow.py
│   │       │
│   │       ├── nodes/               # Individual LangGraph nodes
│   │       │   ├── __init__.py
│   │       │   ├── base_node.py
│   │       │   ├── intent_classifier.py
│   │       │   ├── email_nodes.py
│   │       │   ├── calendar_nodes.py
│   │       │   ├── planning_nodes.py
│   │       │   ├── approval_nodes.py
│   │       │   └── execution_nodes.py
│   │       │
│   │       ├── state/               # LangGraph state management
│   │       │   ├── __init__.py
│   │       │   ├── conversation_state.py
│   │       │   ├── workflow_state.py
│   │       │   └── postgres_checkpointer.py
│   │       │
│   │       ├── mcp/                # MCP tool integration
│   │       │   ├── __init__.py
│   │       │   ├── manager.py
│   │       │   ├── tools/
│   │       │   │   ├── __init__.py
│   │       │   │   ├── base_tool.py
│   │       │   │   ├── gmail_tools.py
│   │       │   │   ├── calendar_tools.py
│   │       │   │   └── memory_tools.py
│   │       │   └── rate_limiter.py  # NEW: Per-tool rate limiting
│   │       │
│   │       ├── memory/              # Simplified 2-tier memory
│   │       │   ├── __init__.py
│   │       │   ├── memory_system.py
│   │       │   ├── vector_memory.py
│   │       │   └── context_builder.py
│   │       │
│   │       └── utils/
│   │           ├── __init__.py
│   │           ├── cost_optimizer.py
│   │           ├── llm_router.py     # NEW: Local vs cloud model routing
│   │           ├── embeddings.py
│   │           └── prompt_templates.py
│   │
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── conftest.py
│   │   ├── unit/
│   │   │   ├── test_workflows.py    # NEW: Workflow testing
│   │   │   ├── test_nodes.py
│   │   │   ├── test_mcp_tools.py
│   │   │   └── test_state_management.py
│   │   ├── integration/
│   │   │   ├── test_workflow_execution.py
│   │   │   ├── test_google_integration.py
│   │   │   └── test_approval_flow.py
│   │   └── e2e/
│   │       ├── test_email_workflows.py
│   │       ├── test_calendar_workflows.py
│   │       └── test_mixed_workflows.py
│   │
│   ├── scripts/
│   │   ├── init_db.py
│   │   ├── download_models.py
│   │   ├── seed_demo_data.py
│   │   └── backup_checkpoints.py
│   │
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── pyproject.toml
│   └── .env.example
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Chat/
│   │   │   │   ├── ChatInterface.tsx
│   │   │   │   ├── WorkflowVisualizer.tsx  # NEW: Workflow status display
│   │   │   │   └── MessageBubble.tsx
│   │   │   ├── Approval/
│   │   │   │   ├── ApprovalQueue.tsx
│   │   │   │   ├── DiffPreview.tsx         # NEW: Before/after previews
│   │   │   │   └── BatchApproval.tsx       # NEW: Bulk approval UI
│   │   │   └── Account/
│   │   │       ├── AccountManager.tsx
│   │   │       ├── OAuthFlow.tsx
│   │   │       └── PermissionDisplay.tsx   # NEW: Clear scope display
│   │   ├── hooks/
│   │   │   ├── useWebSocket.ts
│   │   │   ├── useWorkflowStatus.ts        # NEW: Workflow state tracking
│   │   │   └── useGoogleAuth.ts
│   │   └── types/
│   │       ├── workflow.ts                 # NEW: Workflow type definitions
│   │       ├── approval.ts
│   │       └── api.ts
│   │
│   ├── package.json
│   └── tsconfig.json
│
├── deployment/
│   ├── terraform/
│   │   ├── main.tf
│   │   ├── monitoring.tf              # NEW: Grafana + AlertManager
│   │   └── security.tf
│   │
│   └── docker/
│       ├── docker-compose.yml
│       ├── docker-compose.prod.yml
│       └── nginx.conf
│
├── docs/
│   ├── ARCHITECTURE.md
│   ├── WORKFLOWS.md                   # NEW: Workflow documentation
│   ├── SECURITY.md
│   ├── DEPLOYMENT.md
│   └── API.md
│
└── monitoring/
    ├── grafana/
    │   └── dashboards/
    │       ├── workflow-performance.json
    │       ├── cost-tracking.json
    │       └── error-analysis.json
    └── prometheus/
        └── rules.yml
```

## LangGraph Workflow Architecture

### Core Workflow Pattern

Every workflow follows this deterministic pattern:

```python
from langgraph import StateGraph, END
from typing import TypedDict, Annotated
import operator

class WorkflowState(TypedDict):
    # Input
    user_input: str
    user_id: str
    account_ids: list[str]

    # Processing
    intent: dict
    plan: dict
    context: dict

    # Execution
    steps: Annotated[list, operator.add]
    current_step: int

    # Approval
    approvals_needed: list
    approvals_granted: list

    # Results
    results: Annotated[list, operator.add]
    error: str

    # Metadata
    workflow_id: str
    started_at: str
    cost_estimate: float

def create_base_workflow():
    workflow = StateGraph(WorkflowState)

    # Core nodes (every workflow has these)
    workflow.add_node("classify_intent", classify_intent_node)
    workflow.add_node("build_context", build_context_node)
    workflow.add_node("create_plan", create_plan_node)
    workflow.add_node("estimate_cost", estimate_cost_node)
    workflow.add_node("check_permissions", check_permissions_node)

    # Entry point
    workflow.set_entry_point("classify_intent")

    # Basic flow
    workflow.add_edge("classify_intent", "build_context")
    workflow.add_edge("build_context", "create_plan")
    workflow.add_edge("create_plan", "estimate_cost")
    workflow.add_edge("estimate_cost", "check_permissions")

    return workflow
```

### Specialized Workflows

#### Email Workflow
```python
def create_email_workflow():
    workflow = create_base_workflow()

    # Email-specific nodes
    workflow.add_node("search_emails", search_emails_node)
    workflow.add_node("analyze_content", analyze_email_content_node)
    workflow.add_node("extract_contacts", extract_contacts_node)
    workflow.add_node("draft_response", draft_response_node)
    workflow.add_node("request_approval", request_email_approval_node)
    workflow.add_node("send_email", send_email_node)

    # Email flow from base
    workflow.add_edge("check_permissions", "search_emails")
    workflow.add_edge("search_emails", "analyze_content")
    workflow.add_edge("analyze_content", "extract_contacts")
    workflow.add_edge("extract_contacts", "draft_response")
    workflow.add_edge("draft_response", "request_approval")

    # Conditional approval
    workflow.add_conditional_edges(
        "request_approval",
        lambda state: "send" if state["approvals_granted"] else "end",
        {
            "send": "send_email",
            "end": END
        }
    )

    workflow.add_edge("send_email", END)

    return workflow.compile(
        checkpointer=PostgresCheckpointer(),
        interrupt_before=["request_approval"]  # Always stop for approval
    )
```

#### Calendar Workflow
```python
def create_calendar_workflow():
    workflow = create_base_workflow()

    # Calendar-specific nodes
    workflow.add_node("get_calendar_data", get_calendar_data_node)
    workflow.add_node("find_conflicts", find_conflicts_node)
    workflow.add_node("find_free_slots", find_free_slots_node)
    workflow.add_node("optimize_schedule", optimize_schedule_node)
    workflow.add_node("create_event_draft", create_event_draft_node)
    workflow.add_node("request_approval", request_calendar_approval_node)
    workflow.add_node("create_event", create_event_node)
    workflow.add_node("send_invites", send_invites_node)

    # Calendar flow
    workflow.add_edge("check_permissions", "get_calendar_data")
    workflow.add_edge("get_calendar_data", "find_conflicts")
    workflow.add_edge("find_conflicts", "find_free_slots")
    workflow.add_edge("find_free_slots", "optimize_schedule")
    workflow.add_edge("optimize_schedule", "create_event_draft")
    workflow.add_edge("create_event_draft", "request_approval")

    # Conditional execution
    workflow.add_conditional_edges(
        "request_approval",
        lambda state: "create" if state["approvals_granted"] else "end",
        {
            "create": "create_event",
            "end": END
        }
    )

    workflow.add_edge("create_event", "send_invites")
    workflow.add_edge("send_invites", END)

    return workflow.compile(
        checkpointer=PostgresCheckpointer(),
        interrupt_before=["request_approval"]
    )
```

### Mixed Workflow (Complex Multi-Domain)
```python
def create_mixed_workflow():
    """Handles requests that span email + calendar + planning"""
    workflow = create_base_workflow()

    # Mixed-domain nodes
    workflow.add_node("determine_domains", determine_domains_node)
    workflow.add_node("parallel_email_search", parallel_email_search_node)
    workflow.add_node("parallel_calendar_check", parallel_calendar_check_node)
    workflow.add_node("correlate_data", correlate_data_node)
    workflow.add_node("synthesize_plan", synthesize_plan_node)
    workflow.add_node("create_action_list", create_action_list_node)
    workflow.add_node("batch_approval", batch_approval_node)
    workflow.add_node("execute_actions", execute_actions_node)

    # Mixed flow
    workflow.add_edge("check_permissions", "determine_domains")
    workflow.add_edge("determine_domains", "parallel_email_search")
    workflow.add_edge("determine_domains", "parallel_calendar_check")
    workflow.add_edge(["parallel_email_search", "parallel_calendar_check"], "correlate_data")
    workflow.add_edge("correlate_data", "synthesize_plan")
    workflow.add_edge("synthesize_plan", "create_action_list")
    workflow.add_edge("create_action_list", "batch_approval")

    workflow.add_conditional_edges(
        "batch_approval",
        lambda state: "execute" if state["approvals_granted"] else "end",
        {
            "execute": "execute_actions",
            "end": END
        }
    )

    workflow.add_edge("execute_actions", END)

    return workflow.compile(
        checkpointer=PostgresCheckpointer(),
        interrupt_before=["batch_approval"]
    )
```

## Enterprise-Grade Features

### 1. Approval System with Diff Previews

```python
class ApprovalNode:
    """Enterprise-grade approval system with previews"""

    async def request_email_approval(self, state: WorkflowState) -> WorkflowState:
        draft = state["results"][-1]["draft"]

        # Generate diff preview
        preview = {
            "action_type": "send_email",
            "before": "No email",
            "after": draft["body"],
            "recipients": draft["to"],
            "subject": draft["subject"],
            "account": draft["from_account"],
            "estimated_cost": "$0.02",
            "risk_level": "low",
            "undo_window": "5 minutes"
        }

        # Create approval request
        approval_id = await self.approval_service.create_request(
            user_id=state["user_id"],
            workflow_id=state["workflow_id"],
            action_preview=preview,
            timeout_minutes=30
        )

        # Interrupt workflow until approval
        state["approvals_needed"].append(approval_id)

        # Send to frontend via WebSocket
        await self.notify_approval_needed(approval_id, preview)

        return state

class BatchApprovalNode:
    """Handle bulk operations efficiently"""

    async def request_batch_approval(self, state: WorkflowState) -> WorkflowState:
        actions = state["results"][-1]["action_list"]

        # Group similar actions
        grouped = self.group_similar_actions(actions)

        # Create batch preview
        batch_preview = {
            "total_actions": len(actions),
            "groups": [
                {
                    "type": "archive_emails",
                    "count": 45,
                    "sample": "Archive 45 promotional emails older than 30 days",
                    "risk": "low"
                },
                {
                    "type": "move_events",
                    "count": 3,
                    "sample": "Move 3 events from personal to work calendar",
                    "risk": "medium"
                }
            ],
            "estimated_cost": "$0.15",
            "estimated_time": "2 minutes",
            "safety_cap": 100  # Max 100 operations per batch
        }

        approval_id = await self.approval_service.create_batch_request(
            user_id=state["user_id"],
            workflow_id=state["workflow_id"],
            batch_preview=batch_preview,
            timeout_minutes=45
        )

        state["approvals_needed"].append(approval_id)
        return state
```

### 2. Multi-Account Google Integration

```python
class GoogleAccountService:
    """Enterprise multi-account OAuth management"""

    async def connect_account(
        self,
        user_id: str,
        auth_code: str,
        account_type: str
    ) -> ConnectedAccount:
        # Exchange code for tokens
        tokens = await self.oauth_client.exchange_code(auth_code)

        # Get account info
        account_info = await self.get_account_info(tokens["access_token"])

        # Store with encryption
        account = ConnectedAccount(
            user_id=user_id,
            provider="google",
            account_email=account_info["email"],
            account_type=account_type,  # "personal" or "work"
            access_token=self.encrypt_token(tokens["access_token"]),
            refresh_token=self.encrypt_token(tokens["refresh_token"]),
            expires_at=tokens["expires_at"],
            scopes=tokens["scope"].split(),
            created_at=utcnow()
        )

        await self.db.save(account)

        # Audit log
        await self.audit_service.log_account_connection(
            user_id=user_id,
            account_email=account_info["email"],
            scopes_granted=tokens["scope"].split()
        )

        return account

    async def get_fresh_token(self, account_id: str) -> str:
        """Always return valid token with automatic refresh"""
        account = await self.db.get_account(account_id)

        # Check if token needs refresh
        if account.expires_at < utcnow() + timedelta(minutes=5):
            # Refresh token
            new_tokens = await self.oauth_client.refresh_token(
                self.decrypt_token(account.refresh_token)
            )

            # Update stored tokens
            account.access_token = self.encrypt_token(new_tokens["access_token"])
            account.expires_at = new_tokens["expires_at"]
            await self.db.save(account)

            return new_tokens["access_token"]

        return self.decrypt_token(account.access_token)

class MCPGmailTool:
    """Production-ready Gmail integration with proper isolation"""

    async def search_emails(
        self,
        user_id: str,
        account_id: str,
        query: str,
        date_range: Optional[DateRange] = None
    ) -> List[EmailSummary]:
        # Verify account ownership
        account = await self.verify_account_access(user_id, account_id)

        # Get fresh token
        token = await self.google_service.get_fresh_token(account_id)

        # Rate limiting per account
        await self.rate_limiter.acquire(f"gmail:{account_id}")

        try:
            # Build Gmail query
            gmail_query = self.build_gmail_query(query, date_range)

            # Execute with retry logic
            messages = await self.execute_with_retry(
                lambda: self.gmail_client.search(token, gmail_query)
            )

            # Process results with privacy controls
            summaries = []
            for msg in messages:
                summary = EmailSummary(
                    id=msg["id"],
                    subject=msg["subject"],
                    sender=msg["from"],
                    snippet=msg["snippet"][:200],  # Limit data exposure
                    date=msg["date"],
                    thread_id=msg["threadId"],
                    account_id=account_id
                )
                summaries.append(summary)

            # Audit log
            await self.audit_service.log_email_search(
                user_id=user_id,
                account_id=account_id,
                query=query,
                result_count=len(summaries)
            )

            return summaries

        except GoogleAPIError as e:
            await self.handle_api_error(e, account_id)
            raise

    async def execute_with_retry(self, func, max_retries: int = 3):
        """Exponential backoff with jitter"""
        for attempt in range(max_retries):
            try:
                return await func()
            except RateLimitError:
                if attempt == max_retries - 1:
                    raise

                # Exponential backoff with jitter
                delay = (2 ** attempt) + random.uniform(0, 1)
                await asyncio.sleep(delay)
```

### 3. Cost Optimization and Circuit Breakers

```python
class CostOptimizer:
    """Production cost controls and optimization"""

    def __init__(self):
        self.daily_limits = {
            "free_user": 5.0,      # $5/day
            "pro_user": 25.0,      # $25/day
            "enterprise": 100.0     # $100/day
        }
        self.hourly_spike_threshold = 10.0  # $10/hour spike protection

    async def check_cost_limits(self, user_id: str, estimated_cost: float) -> bool:
        """Circuit breaker for cost limits"""
        user = await self.user_service.get_user(user_id)
        daily_limit = self.daily_limits.get(user.plan_type, 5.0)

        # Check daily spend
        today_spend = await self.get_daily_spend(user_id)
        if today_spend + estimated_cost > daily_limit:
            await self.notify_cost_limit_exceeded(user_id, daily_limit)
            return False

        # Check hourly spike
        hour_spend = await self.get_hourly_spend(user_id)
        if hour_spend + estimated_cost > self.hourly_spike_threshold:
            await self.notify_spike_protection(user_id)
            return False

        return True

    async def route_llm_request(
        self,
        prompt: str,
        context: dict,
        user_id: str
    ) -> LLMResponse:
        """Smart routing between local and cloud models"""

        # Analyze prompt complexity
        complexity = await self.analyze_prompt_complexity(prompt, context)

        # Route based on complexity and cost
        if complexity.score < 0.3:  # Simple tasks
            model = "ollama:llama3.2:3b"
            estimated_cost = 0.001
        elif complexity.score < 0.7:  # Medium tasks
            model = "ollama:llama3.2:8b"
            estimated_cost = 0.005
        else:  # Complex reasoning
            # Check if user can afford cloud model
            if await self.check_cost_limits(user_id, 0.05):
                model = "openai:gpt-4"
                estimated_cost = 0.05
            else:
                # Fallback to largest local model
                model = "ollama:llama3.2:8b"
                estimated_cost = 0.005

        # Cache check
        cache_key = self.generate_cache_key(prompt, context)
        cached_response = await self.cache.get(cache_key)
        if cached_response and estimated_cost > 0.01:  # Cache expensive calls
            return cached_response

        # Execute with cost tracking
        start_time = time.time()
        response = await self.llm_manager.generate(model, prompt, context)
        execution_time = time.time() - start_time

        # Calculate actual cost
        actual_cost = self.calculate_actual_cost(model, response, execution_time)

        # Track usage
        await self.usage_tracker.record(
            user_id=user_id,
            model=model,
            cost=actual_cost,
            tokens_used=response.token_count,
            execution_time=execution_time
        )

        # Cache if cost-effective
        if actual_cost > 0.01:
            await self.cache.set(cache_key, response, ttl=3600)

        return response

class WorkflowCostEstimator:
    """Estimate workflow costs before execution"""

    async def estimate_workflow_cost(self, plan: dict, context: dict) -> CostEstimate:
        """Estimate total workflow cost"""
        total_cost = 0.0
        step_estimates = []

        for step in plan["steps"]:
            step_cost = await self.estimate_step_cost(step, context)
            step_estimates.append({
                "step": step["name"],
                "estimated_cost": step_cost,
                "reasoning": step.get("cost_reasoning", "")
            })
            total_cost += step_cost

        return CostEstimate(
            total_estimated_cost=total_cost,
            step_breakdown=step_estimates,
            confidence_level=self.calculate_confidence(plan),
            alternative_approaches=await self.suggest_cheaper_alternatives(plan)
        )
```

### 4. Observability and Monitoring

```python
import opentelemetry
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

class WorkflowTracing:
    """Production observability for workflows"""

    def __init__(self):
        self.tracer = trace.get_tracer(__name__)

    async def trace_workflow_execution(self, workflow_id: str, state: WorkflowState):
        """Trace complete workflow with spans"""
        with self.tracer.start_as_current_span(
            "workflow_execution",
            attributes={
                "workflow.id": workflow_id,
                "workflow.type": state.get("workflow_type"),
                "user.id": state["user_id"],
                "accounts.count": len(state["account_ids"])
            }
        ) as workflow_span:

            # Set up workflow context
            workflow_span.set_attribute("workflow.input_length", len(state["user_input"]))
            workflow_span.set_attribute("workflow.estimated_cost", state.get("cost_estimate", 0))

            try:
                # Execute workflow with child spans
                async for step_result in self.execute_workflow_steps(state):
                    await self.trace_step_execution(step_result)

                workflow_span.set_attribute("workflow.status", "completed")
                workflow_span.set_attribute("workflow.steps_completed", state["current_step"])

            except Exception as e:
                workflow_span.set_attribute("workflow.status", "error")
                workflow_span.set_attribute("workflow.error", str(e))
                workflow_span.record_exception(e)
                raise

    async def trace_step_execution(self, step_result: dict):
        """Trace individual step execution"""
        with self.tracer.start_as_current_span(
            f"step_{step_result['name']}",
            attributes={
                "step.name": step_result["name"],
                "step.type": step_result["type"],
                "step.duration_ms": step_result["duration_ms"],
                "step.cost": step_result.get("cost", 0),
                "step.retry_count": step_result.get("retry_count", 0)
            }
        ) as step_span:

            if step_result.get("mcp_tool_used"):
                step_span.set_attribute("mcp.tool", step_result["mcp_tool_used"])
                step_span.set_attribute("mcp.api_calls", step_result.get("api_calls", 0))

            if step_result.get("error"):
                step_span.set_attribute("step.error", step_result["error"])
                step_span.record_exception(Exception(step_result["error"]))

class StructuredLogging:
    """Production-grade structured logging"""

    def __init__(self):
        self.logger = structlog.get_logger()

    async def log_workflow_start(self, workflow_id: str, state: WorkflowState):
        await self.logger.ainfo(
            "workflow_started",
            workflow_id=workflow_id,
            user_id=state["user_id"],
            intent=state.get("intent", {}),
            estimated_cost=state.get("cost_estimate"),
            account_count=len(state["account_ids"]),
            input_length=len(state["user_input"])
        )

    async def log_approval_request(self, approval_id: str, preview: dict):
        await self.logger.ainfo(
            "approval_requested",
            approval_id=approval_id,
            action_type=preview["action_type"],
            risk_level=preview["risk_level"],
            estimated_cost=preview["estimated_cost"],
            timeout_minutes=preview.get("timeout_minutes", 30)
        )

    async def log_mcp_tool_call(self, tool_name: str, account_id: str, result: dict):
        await self.logger.ainfo(
            "mcp_tool_executed",
            tool_name=tool_name,
            account_id=account_id,
            success=result.get("success", False),
            execution_time_ms=result.get("execution_time_ms"),
            api_calls_made=result.get("api_calls", 0),
            rate_limited=result.get("rate_limited", False)
        )

class PerformanceMonitoring:
    """SLO monitoring and alerting"""

    def __init__(self):
        self.slos = {
            "workflow_p95_latency_ms": 5000,    # 95% of workflows < 5s
            "step_p95_latency_ms": 2000,        # 95% of steps < 2s
            "approval_timeout_rate": 0.05,      # < 5% approval timeouts
            "workflow_success_rate": 0.95,      # > 95% success rate
            "api_error_rate": 0.02              # < 2% API errors
        }

    async def check_slo_violations(self):
        """Monitor SLOs and trigger alerts"""
        for metric, threshold in self.slos.items():
            current_value = await self.metrics_client.get_metric(metric)

            if self.is_slo_violated(metric, current_value, threshold):
                await self.alert_manager.trigger_alert(
                    severity="warning",
                    message=f"SLO violation: {metric} = {current_value}, threshold = {threshold}",
                    runbook_url=f"https://docs.company.com/runbooks/{metric}"
                )
```

## 7-Week Implementation Plan

### **Week 1: Foundation & Infrastructure**

**Goal**: Bulletproof foundation with auth, database, and basic LangGraph setup

**Deliverables**:
1. **Core Infrastructure**
   - FastAPI application with async support
   - PostgreSQL with Alembic migrations
   - Redis for caching and sessions
   - JWT authentication system
   - OpenTelemetry tracing setup

2. **Database Schema**
   ```sql
   -- Users and authentication
   CREATE TABLE users (
       id UUID PRIMARY KEY,
       email VARCHAR(255) UNIQUE NOT NULL,
       plan_type VARCHAR(50) DEFAULT 'free',
       created_at TIMESTAMP DEFAULT NOW()
   );

   -- Multi-account Google integration
   CREATE TABLE connected_accounts (
       id UUID PRIMARY KEY,
       user_id UUID REFERENCES users(id),
       provider VARCHAR(50) NOT NULL,
       account_email VARCHAR(255) NOT NULL,
       account_type VARCHAR(50) NOT NULL, -- 'personal' or 'work'
       encrypted_access_token TEXT,
       encrypted_refresh_token TEXT,
       expires_at TIMESTAMP,
       scopes TEXT[] DEFAULT '{}',
       created_at TIMESTAMP DEFAULT NOW(),
       UNIQUE(user_id, provider, account_email)
   );

   -- LangGraph workflow state persistence
   CREATE TABLE workflow_checkpoints (
       workflow_id UUID PRIMARY KEY,
       user_id UUID REFERENCES users(id),
       workflow_type VARCHAR(100) NOT NULL,
       current_state JSONB NOT NULL,
       current_step VARCHAR(100),
       started_at TIMESTAMP DEFAULT NOW(),
       last_updated TIMESTAMP DEFAULT NOW(),
       status VARCHAR(50) DEFAULT 'running'
   );

   -- Approval system
   CREATE TABLE action_approvals (
       id UUID PRIMARY KEY,
       workflow_id UUID REFERENCES workflow_checkpoints(workflow_id),
       user_id UUID REFERENCES users(id),
       action_type VARCHAR(100) NOT NULL,
       action_preview JSONB NOT NULL,
       status VARCHAR(50) DEFAULT 'pending',
       created_at TIMESTAMP DEFAULT NOW(),
       resolved_at TIMESTAMP,
       timeout_at TIMESTAMP
   );

   -- Cost and usage tracking
   CREATE TABLE usage_logs (
       id UUID PRIMARY KEY,
       user_id UUID REFERENCES users(id),
       workflow_id UUID,
       model_used VARCHAR(100),
       cost_usd DECIMAL(10,6),
       tokens_used INTEGER,
       execution_time_ms INTEGER,
       created_at TIMESTAMP DEFAULT NOW()
   );

   -- Audit trail
   CREATE TABLE audit_logs (
       id UUID PRIMARY KEY,
       user_id UUID REFERENCES users(id),
       account_id UUID,
       action VARCHAR(100) NOT NULL,
       details JSONB,
       ip_address INET,
       user_agent TEXT,
       created_at TIMESTAMP DEFAULT NOW()
   );
   ```

3. **Basic LangGraph Setup**
   - PostgreSQL checkpointer implementation
   - Base workflow structure
   - Simple intent classification node

4. **Security Foundation**
   - Token encryption/decryption
   - Rate limiting per user
   - Input validation with Pydantic v2

**Testing**:
- All API endpoints respond correctly
- Database migrations work
- Basic auth flow (register/login)
- LangGraph checkpointing works

---

### **Week 2: Google OAuth & Multi-Account Management**

**Goal**: Production-ready Google integration with proper security

**Deliverables**:
1. **OAuth Implementation**
   - Google OAuth 2.0 flow with PKCE
   - Automatic token refresh
   - Secure token storage with encryption
   - Scope minimization per account type

2. **Account Management**
   - Connect/disconnect multiple Google accounts
   - Account type labeling (personal/work)
   - Permission display in UI
   - Account switching logic

3. **Security Features**
   - Per-account data isolation
   - Audit logging for all account operations
   - Token rotation policy
   - Revocation handling

4. **Frontend Integration**
   - OAuth flow UI
   - Account management dashboard
   - Clear scope permission display

**Testing**:
- Full OAuth flow for multiple accounts
- Token refresh mechanism
- Account isolation verification
- Security audit of token handling

---

### **Week 3: MCP Tools & Rate Limiting**

**Goal**: Production-ready tool integration with reliability

**Deliverables**:
1. **MCP Tool Framework**
   - Base tool class with retry logic
   - Centralized rate limiting
   - Circuit breaker pattern
   - Tool registry and lifecycle management

2. **Gmail MCP Tools**
   ```python
   class GmailTools:
       async def search_emails(self, account_id: str, query: str) -> List[EmailSummary]
       async def read_email(self, account_id: str, email_id: str) -> EmailDetail
       async def create_draft(self, account_id: str, draft: EmailDraft) -> DraftResult
       async def send_email(self, account_id: str, email: Email) -> SendResult
       async def modify_labels(self, account_id: str, email_ids: List[str], labels: List[str]) -> LabelResult
   ```

3. **Calendar MCP Tools**
   ```python
   class CalendarTools:
       async def get_events(self, account_id: str, date_range: DateRange) -> List[Event]
       async def find_free_slots(self, account_ids: List[str], duration: int, constraints: dict) -> List[TimeSlot]
       async def create_event(self, account_id: str, event: EventDraft) -> EventResult
       async def check_conflicts(self, account_ids: List[str], proposed_event: EventDraft) -> ConflictResult
   ```

4. **Background Task Queue**
   - Celery/Dramatiq setup for async operations
   - Idempotency keys for all operations
   - Dead letter queue for failed tasks

**Testing**:
- Individual tool functionality
- Rate limiting behavior
- Error handling and retries
- Queue processing reliability

---

### **Week 4: LangGraph Workflows & Orchestration**

**Goal**: Sophisticated workflow orchestration with state management

**Deliverables**:
1. **Core Workflow Engine**
   ```python
   class WorkflowOrchestrator:
       async def execute_workflow(self, user_input: str, user_id: str) -> WorkflowResult
       async def resume_workflow(self, workflow_id: str) -> WorkflowResult
       async def cancel_workflow(self, workflow_id: str) -> bool
   ```

2. **Email Workflow Implementation**
   - Email search and analysis
   - Contact extraction
   - Response drafting
   - Approval integration

3. **Calendar Workflow Implementation**
   - Multi-calendar analysis
   - Conflict detection
   - Optimal scheduling
   - Invite coordination

4. **State Management**
   - Persistent checkpointing
   - State recovery after failures
   - Parallel execution support

**Testing**:
- Complete workflow execution
- Checkpoint recovery
- Error handling across nodes
- State consistency validation

---

### **Week 5: Approval System & Real-time Updates**

**Goal**: Enterprise-grade approval system with live updates

**Deliverables**:
1. **Approval System**
   ```python
   class ApprovalSystem:
       async def create_approval_request(self, workflow_id: str, action_preview: dict) -> str
       async def process_approval_response(self, approval_id: str, approved: bool) -> bool
       async def handle_approval_timeout(self, approval_id: str) -> None
       async def create_batch_approval(self, actions: List[dict]) -> str
   ```

2. **Diff Preview Generation**
   - Before/after comparisons for emails
   - Calendar event change previews
   - Risk assessment for each action
   - Cost estimation display

3. **WebSocket Implementation**
   - Real-time workflow status updates
   - Approval notifications
   - Progress tracking
   - Error notifications

4. **Undo System**
   - Compensating actions for destructive operations
   - 5-minute undo window
   - Action logging for rollback

**Testing**:
- Approval flow end-to-end
- WebSocket connection stability
- Timeout handling
- Undo functionality

---

### **Week 6: Cost Optimization & Observability**

**Goal**: Production monitoring and cost controls

**Deliverables**:
1. **Cost Management**
   ```python
   class CostManager:
       async def estimate_workflow_cost(self, plan: dict) -> CostEstimate
       async def check_user_limits(self, user_id: str, estimated_cost: float) -> bool
       async def route_llm_request(self, prompt: str, complexity: float) -> LLMResponse
   ```

2. **Model Router**
   - Local vs cloud model selection
   - Complexity-based routing
   - Response caching for expensive calls
   - Fallback strategies

3. **Observability Stack**
   - OpenTelemetry distributed tracing
   - Structured JSON logging
   - Prometheus metrics
   - Grafana dashboards

4. **Performance Monitoring**
   - SLO definition and monitoring
   - Alert configuration
   - Performance regression detection

**Testing**:
- Cost limit enforcement
- Model routing accuracy
- Monitoring data collection
- Alert triggering

---

### **Week 7: Integration Testing & Production Deployment**

**Goal**: Production-ready deployment with comprehensive testing

**Deliverables**:
1. **End-to-End Testing**
   - Complete workflow scenarios
   - Multi-account operations
   - Error recovery testing
   - Load testing

2. **Production Infrastructure**
   - EC2 deployment with Docker
   - SSL certificates and domain setup
   - Database backups
   - Log aggregation

3. **Security Hardening**
   - Security audit and fixes
   - HTTPS enforcement
   - Input sanitization validation
   - Rate limiting verification

4. **Documentation & Demo**
   - API documentation
   - Architecture diagrams
   - Deployment guides
   - Video walkthrough

**Testing**:
- Production smoke tests
- Security penetration testing
- Performance benchmarks
- Documentation review

## Example Production Flows

### Flow 1: "Schedule a meeting with everyone who emailed about Project X"

```python
# LangGraph execution trace
async def execute_complex_scheduling_flow():
    workflow_id = "wf_schedule_project_x_123"

    # State progression through nodes:
    # 1. classify_intent -> "mixed_workflow" (email + calendar)
    # 2. build_context -> Retrieves user preferences, recent patterns
    # 3. create_plan -> Multi-step plan with cost estimate
    # 4. estimate_cost -> $0.12 (email search + LLM analysis + calendar ops)
    # 5. check_permissions -> Verifies Gmail + Calendar access
    # 6. search_emails -> Finds 8 emails about "Project X"
    # 7. extract_contacts -> john@company.com, jane@company.com, mike@company.com
    # 8. parallel_calendar_check -> Checks availability across 3 calendars
    # 9. find_optimal_slots -> Monday 2pm, Tuesday 10am available
    # 10. create_meeting_draft -> Detailed meeting proposal
    # 11. request_approval -> Shows preview with attendees, time, agenda
    # 12. [INTERRUPT - wait for user approval]
    # 13. create_event -> Creates calendar event after approval
    # 14. send_invites -> Sends invitations to attendees

    # WebSocket updates sent to frontend:
    # "🤔 Understanding your request..."
    # "📧 Searching emails for Project X discussions..."
    # "👥 Found 8 relevant emails from 3 people"
    # "📅 Checking calendar availability..."
    # "✨ Found optimal time slots"
    # "⏳ Waiting for your approval to create meeting..."
    # "✅ Meeting created and invites sent!"
```

### Flow 2: Daily Planning - "What should I focus on today?"

```python
# LangGraph execution with parallel processing
async def execute_daily_planning_flow():
    workflow_id = "wf_daily_planning_456"

    # Parallel execution branches:
    branches = {
        "email_analysis": [
            "get_unread_emails",      # 23 unread emails
            "categorize_by_priority", # 5 urgent, 8 important, 10 low
            "extract_action_items"    # 12 tasks requiring response
        ],
        "calendar_analysis": [
            "get_todays_schedule",    # 4 meetings scheduled
            "calculate_free_time",    # 3 hours available
            "identify_prep_needed"    # 2 meetings need preparation
        ],
        "pattern_analysis": [
            "get_historical_patterns", # Usually does reports on Monday
            "check_recurring_tasks",   # Weekly report due
            "analyze_energy_levels"    # Most productive 9-11am
        ]
    }

    # Synthesis phase:
    # "correlate_insights" -> Combines all analyses
    # "generate_priority_list" -> Creates ranked action list
    # "suggest_time_blocks" -> Proposes schedule optimization
    # "create_action_plan" -> Final prioritized plan

    # Result delivered to user:
    # "Based on your emails, calendar, and usual Monday patterns:
    #  1. Respond to urgent email from Sarah about budget (15 min)
    #  2. Prepare slides for 2pm client meeting (45 min)
    #  3. Complete weekly team report (30 min)
    #  4. Review contract from legal team (20 min)
    #
    #  Suggested schedule:
    #  - 9:00-9:45am: Prepare client meeting slides (high energy time)
    #  - 9:45-10:00am: Quick email responses
    #  - 10:30-11:00am: Weekly report
    #  - 1:30-2:00pm: Review contract before client meeting"
```

## Production Considerations

### Security Checklist
- ✅ Encrypted token storage with rotation
- ✅ Per-user data isolation guarantees
- ✅ Minimal scope requests with clear consent
- ✅ Audit trail for all actions
- ✅ Rate limiting and abuse protection
- ✅ HTTPS enforcement with HSTS
- ✅ Input validation and sanitization

### Scalability Considerations
- **Current**: Single EC2 instance (0-1000 users)
- **Phase 2**: Separate services (RDS, ElastiCache, ECS)
- **Phase 3**: Microservices with queue-based architecture

### Cost Optimization
- **Local models**: 90% of operations (routing, summaries, simple tasks)
- **Cloud models**: Only for complex multi-step reasoning
- **Caching**: Aggressive caching for expensive operations
- **Circuit breakers**: Hard limits to prevent cost overruns

### Monitoring & Alerting
- **SLOs**: p95 latency, success rates, cost per user
- **Alerts**: SLO violations, security events, cost spikes
- **Dashboards**: Real-time workflow performance, cost tracking
- **Logs**: Structured JSON with correlation IDs

## Why This Architecture Wins

### For Hiring Managers
1. **Production Engineering**: Real-world concerns (cost, security, observability)
2. **Modern AI Stack**: LangGraph, MCP, proper orchestration
3. **Enterprise Features**: Approval workflows, audit trails, compliance
4. **Scalability**: Clear path from MVP to enterprise scale

### For Technical Interviews
1. **System Design**: Multi-tier architecture with proper separation
2. **State Management**: Complex workflow orchestration
3. **API Design**: RESTful + WebSocket hybrid
4. **Error Handling**: Comprehensive retry and recovery strategies
5. **Testing**: Unit, integration, and E2E test strategies

### For Business Value
1. **User Experience**: Natural language → complex automation
2. **Enterprise Ready**: Security, compliance, audit features
3. **Cost Effective**: Optimized for sustainable unit economics
4. **Extensible**: Easy to add new tools and capabilities

This implementation showcases sophisticated engineering while solving a real problem that businesses face every day. The LangGraph-only approach reduces complexity while maintaining all the production-grade features that demonstrate senior-level engineering capabilities.