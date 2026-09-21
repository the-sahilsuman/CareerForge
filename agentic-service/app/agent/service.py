from __future__ import annotations

from app.agent.models import (
    AgentRequest,
    AgentResponse,
)
from app.core.errors import (
    AgentError,
    AgentLLMError,
    AgentRetrievalError,
    AgentSessionError,
)
from app.core.logging import get_logger
from app.graph import agent_graph


logger = get_logger(__name__)


class AgentService:
    """
    Public service facade for the CareerForge agent.

    AgentService is intentionally thin.

    LangGraph owns the actual agent orchestration:

        session
            ↓
        routing
            ↓
        JD resolution
            ↓
        retrieval
            ↓
        context
            ↓
        generation
            ↓
        persistence
            ↓
        metadata

    AgentService is responsible for:

    - validating the incoming request
    - invoking LangGraph
    - converting internal failures into safe agent errors
    - extracting the final response
    - returning the API-level AgentResponse
    """

    async def chat(
        self,
        request: AgentRequest,
    ) -> AgentResponse:
        """
        Execute one agent request through LangGraph.

        Internal/provider/database errors must not be exposed
        directly to the API consumer.
        """

        # ====================================================
        # Validation
        # ====================================================

        if request is None:
            raise AgentSessionError(
                "Agent request is required."
            )

        user_id = request.user_id.strip()

        if not user_id:
            raise AgentSessionError(
                "user_id is required."
            )

        message = request.message.strip()

        if not message:
            raise AgentSessionError(
                "message cannot be empty."
            )

        # ====================================================
        # Initial graph state
        # ====================================================

        initial_state = {
            "user_id": user_id,
            "message": message,
            "jd_id": request.jd_id,
        }

        logger.info(
            "Starting agent graph: user=%s jd=%s",
            user_id,
            request.jd_id,
        )

        # ====================================================
        # Execute LangGraph
        # ====================================================

        try:
            result = await agent_graph.ainvoke(
                initial_state,
            )

        except AgentError:
            # Already classified as a safe agent error.
            raise

        except Exception as exc:
            """
            Never expose raw provider/database/internal
            exceptions to the caller.

            Keep the original exception in server logs
            for debugging and observability.
            """

            logger.exception(
                "Agent graph execution failed: "
                "user=%s jd=%s error=%s",
                user_id,
                request.jd_id,
                str(exc),
            )

            error_message = str(exc).lower()

            # ------------------------------------------------
            # LLM / Provider failures
            # ------------------------------------------------

            if any(
                keyword in error_message
                for keyword in (
                    "quota",
                    "rate limit",
                    "rate_limit",
                    "resource_exhausted",
                    "429",
                    "llm",
                    "model",
                    "generation",
                    "openrouter",
                    "gemini",
                    "huggingface",
                )
            ):
                raise AgentLLMError(
                    "The AI service is temporarily unavailable. "
                    "Please try again shortly."
                ) from exc

            # ------------------------------------------------
            # Retrieval failures
            # ------------------------------------------------

            if any(
                keyword in error_message
                for keyword in (
                    "retrieval",
                    "embedding",
                    "vector",
                    "s3",
                    "knowledge",
                    "chunk",
                )
            ):
                raise AgentRetrievalError(
                    "I couldn't retrieve the required information "
                    "right now. Please try again."
                ) from exc

            # ------------------------------------------------
            # Session / state failures
            # ------------------------------------------------

            if any(
                keyword in error_message
                for keyword in (
                    "session",
                    "redis",
                    "state",
                    "checkpoint",
                )
            ):
                raise AgentSessionError(
                    "The conversation session could not be processed. "
                    "Please try again."
                ) from exc

            # ------------------------------------------------
            # Generic safe failure
            # ------------------------------------------------

            raise AgentError(
                "The agent could not process your request "
                "right now. Please try again."
            ) from exc

        # ====================================================
        # Validate graph result
        # ====================================================

        if not result:
            logger.error(
                "Agent graph returned an empty result: "
                "user=%s jd=%s",
                user_id,
                request.jd_id,
            )

            raise AgentError(
                "Agent graph returned no result."
            )

        # ====================================================
        # Extract final response
        # ====================================================

        answer = result.get(
            "answer",
            "",
        )

        if not isinstance(answer, str):
            logger.error(
                "Agent graph returned invalid answer type: "
                "user=%s type=%s",
                user_id,
                type(answer).__name__,
            )

            raise AgentError(
                "Agent graph returned an invalid response."
            )

        answer = answer.strip()

        if not answer:
            logger.error(
                "Agent graph completed without a response: "
                "user=%s jd=%s",
                user_id,
                request.jd_id,
            )

            raise AgentError(
                "Agent graph completed without a response."
            )

        # ====================================================
        # Extract active JD
        # ====================================================

        active_jd = result.get(
            "active_jd",
        )

        active_jd_id = None

        if active_jd is not None:
            active_jd_id = getattr(
                active_jd,
                "jd_id",
                None,
            )

        # ====================================================
        # Extract retrieved chunks
        # ====================================================

        retrieved_chunks = result.get(
            "retrieved_chunks",
            [],
        )

        if retrieved_chunks is None:
            retrieved_chunks = []

        if not isinstance(
            retrieved_chunks,
            list,
        ):
            logger.warning(
                "Invalid retrieved_chunks value; "
                "defaulting to zero: user=%s",
                user_id,
            )

            retrieved_chunks = []

        # ====================================================
        # Extract metadata
        # ====================================================

        metadata = result.get(
            "metadata",
            {},
        )

        if metadata is None:
            metadata = {}

        if not isinstance(
            metadata,
            dict,
        ):
            logger.warning(
                "Invalid metadata value; "
                "defaulting to empty dictionary: user=%s",
                user_id,
            )

            metadata = {}

        # ====================================================
        # Completion logging
        # ====================================================

        logger.info(
            "Agent graph completed: "
            "user=%s jd=%s retrieved=%d",
            user_id,
            active_jd_id,
            len(retrieved_chunks),
        )

        # ====================================================
        # Return API-level response
        # ====================================================

        return AgentResponse(
            message=answer,
            user_id=user_id,
            jd_id=active_jd_id,
            retrieved_chunks=len(
                retrieved_chunks
            ),
            metadata=metadata,
        )


# ============================================================
# Singleton
# ============================================================

agent_service = AgentService()