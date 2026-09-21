from __future__ import annotations

from langgraph.graph import (
    END,
    START,
    StateGraph,
)

from app.graph.nodes import (
    analyze_jd,
    build_context,
    build_metadata,
    check_email_connection,
    detect_and_store_jd,
    draft_email,
    email_not_connected,
    generate_response,
    load_session,
    persist_conversation,
    resolve_jd,
    retrieve_context,
    route_request,
    send_email,
)

from app.graph.state import AgentGraphState
from app.routing import Intent


# ============================================================
# Route After Retrieval
# ============================================================


def route_after_retrieval(
    state: AgentGraphState,
) -> str:
    """
    Decide whether the request requires JD intelligence.
    """

    route_result = state.get(
        "route_result",
    )

    if route_result is None:
        return "build_context"

    if route_result.intent in {
        Intent.JD_ANALYSIS,
        Intent.JD_MATCH,
    }:
        return "analyze_jd"

    return "build_context"


# ============================================================
# Route After JD Resolution
# ============================================================


def route_after_jd_resolution(
    state: AgentGraphState,
) -> str:
    """
    Decide whether the request requires email
    connection validation.

    Email requests must pass through the email
    connection check before continuing.
    """

    route_result = state.get(
        "route_result",
    )

    if route_result is None:
        return "retrieve_context"

    if route_result.intent in {
        Intent.EMAIL_DRAFT,
        Intent.EMAIL_SEND,
    }:
        return "check_email_connection"

    return "retrieve_context"


# ============================================================
# Route After Email Connection Check
# ============================================================


def route_after_email_connection(
    state: AgentGraphState,
) -> str:
    """
    Continue only when the user's email account
    is connected.

    If the account is not connected, terminate
    the email flow with a controlled response.
    """

    email_connection = state.get(
        "email_connection",
    )

    if not email_connection:
        return "email_not_connected"

    if not email_connection.get(
        "connected",
        False,
    ):
        return "email_not_connected"

    return "retrieve_context"


def route_after_email_draft(
    state: AgentGraphState,
) -> str:

    route_result = state.get(
        "route_result",
    )

    if route_result is None:
        return "generate_response"

    if route_result.intent == Intent.EMAIL_SEND:
        return "send_email"

    return "generate_response"

# ============================================================
# Build Agent Graph
# ============================================================


def build_agent_graph():

    graph = StateGraph(
        AgentGraphState,
    )

    # ========================================================
    # Nodes
    # ========================================================

    graph.add_node(
        "load_session",
        load_session,
    )

    graph.add_node(
        "detect_and_store_jd",
        detect_and_store_jd,
    )

    graph.add_node(
        "send_email",
        send_email,
    )

    graph.add_node(
        "route_request",
        route_request,
    )

    graph.add_node(
        "resolve_jd",
        resolve_jd,
    )

    graph.add_node(
        "check_email_connection",
        check_email_connection,
    )

    graph.add_node(
        "email_not_connected",
        email_not_connected,
    )

    graph.add_node(
        "retrieve_context",
        retrieve_context,
    )

    graph.add_node(
        "analyze_jd",
        analyze_jd,
    )

    graph.add_node(
        "build_context",
        build_context,
    )

    graph.add_node(
        "generate_response",
        generate_response,
    )

    graph.add_node(
        "persist_conversation",
        persist_conversation,
    )

    graph.add_node(
        "build_metadata",
        build_metadata,
    )

    graph.add_node(
        "draft_email",
        draft_email,
    )

    # ========================================================
    # Main Flow
    # ========================================================

    graph.add_edge(
        START,
        "load_session",
    )

    graph.add_edge(
    "load_session",
    "detect_and_store_jd",
    )

    graph.add_edge(
        "detect_and_store_jd",
        "route_request",
    )

    graph.add_edge(
        "route_request",
        "resolve_jd",
    )

    # ========================================================
    # After JD Resolution
    #
    # Normal request:
    #     resolve_jd
    #          ↓
    #     retrieve_context
    #
    # Email request:
    #     resolve_jd
    #          ↓
    #     check_email_connection
    # ========================================================

    graph.add_conditional_edges(
        "resolve_jd",
        route_after_jd_resolution,
        {
            "check_email_connection":
                "check_email_connection",
            "retrieve_context":
                "retrieve_context",
        },
    )

    # ========================================================
    # Email Connection Check
    # ========================================================

    graph.add_conditional_edges(
        "check_email_connection",
        route_after_email_connection,
        {
            "email_not_connected":
                "email_not_connected",
            "retrieve_context":
                "retrieve_context",
        },
    )

    # ========================================================
    # Email Not Connected
    #
    # Do not continue into retrieval/generation.
    # The email node itself creates the user-facing
    # response.
    # ========================================================

    graph.add_edge(
        "email_not_connected",
        END,
    )

    # ========================================================
    # JD Intelligence Conditional Branch
    # ========================================================

    graph.add_conditional_edges(
        "retrieve_context",
        route_after_retrieval,
        {
            "analyze_jd":
                "analyze_jd",
            "build_context":
                "build_context",
        },
    )

    graph.add_edge(
        "analyze_jd",
        "build_context",
    )

    # ========================================================
    # Generation
    # ========================================================

    graph.add_conditional_edges(
        "build_context",
        route_after_context,
        {
            "draft_email": "draft_email",
            "generate_response": "generate_response",
        },
    )

    graph.add_conditional_edges(
        "draft_email",
        route_after_email_draft,
        {
            "send_email": "send_email",
            "generate_response": "generate_response",
        },
    )

    graph.add_edge(
        "send_email",
        "generate_response",
    )

    # ========================================================
    # Persistence
    # ========================================================

    graph.add_edge(
        "generate_response",
        "persist_conversation",
    )

    graph.add_edge(
        "persist_conversation",
        "build_metadata",
    )

    # ========================================================
    # End
    # ========================================================

    graph.add_edge(
        "build_metadata",
        END,
    )

    return graph.compile()

def route_after_context(
    state: AgentGraphState,
) -> str:

    route_result = state.get(
        "route_result",
    )

    if route_result is None:
        return "generate_response"

    if route_result.intent in {
        Intent.EMAIL_DRAFT,
        Intent.EMAIL_SEND,
    }:
        return "draft_email"

    return "generate_response"


# ============================================================
# Compiled Graph
# ============================================================

agent_graph = build_agent_graph()