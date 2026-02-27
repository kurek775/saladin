"""Telemetry callback handler — extends SaladinCallbackHandler with token tracking."""

import logging
from datetime import datetime, UTC
from typing import Any

from app.agents.callbacks import SaladinCallbackHandler
from app.models.schemas import WSEvent
from app.core.event_bus import event_bus
from app.core.telemetry import create_token_usage

logger = logging.getLogger(__name__)


class TelemetryCallbackHandler(SaladinCallbackHandler):
    """Extends SaladinCallbackHandler with on_llm_end token usage extraction."""

    async def on_llm_end(self, response: Any, **kwargs) -> None:
        # Call parent for log event
        await super().on_llm_end(response, **kwargs)

        # Extract token usage from response metadata
        try:
            usage_metadata = None
            model_name = ""

            # LangChain response objects have different structures
            if hasattr(response, 'generations') and response.generations:
                gen = response.generations[0][0] if response.generations[0] else None
                if gen and hasattr(gen, 'message'):
                    msg = gen.message
                    if hasattr(msg, 'usage_metadata'):
                        usage_metadata = msg.usage_metadata
                    if hasattr(msg, 'response_metadata'):
                        model_name = msg.response_metadata.get('model', '')
                        if not usage_metadata:
                            # Try extracting from response_metadata directly
                            rm = msg.response_metadata
                            usage = rm.get('usage', rm.get('token_usage', {}))
                            if usage:
                                usage_metadata = {
                                    'input_tokens': usage.get('input_tokens', usage.get('prompt_tokens', 0)),
                                    'output_tokens': usage.get('output_tokens', usage.get('completion_tokens', 0)),
                                }

            if usage_metadata:
                input_tokens = 0
                output_tokens = 0
                if isinstance(usage_metadata, dict):
                    input_tokens = usage_metadata.get('input_tokens', 0)
                    output_tokens = usage_metadata.get('output_tokens', 0)
                else:
                    input_tokens = getattr(usage_metadata, 'input_tokens', 0)
                    output_tokens = getattr(usage_metadata, 'output_tokens', 0)

                token_usage = create_token_usage(model_name, input_tokens, output_tokens)

                await event_bus.publish(WSEvent(
                    type="telemetry",
                    data={
                        "task_id": self.task_id,
                        "agent_id": self.agent_id,
                        "agent_name": self.agent_name,
                        "model": token_usage.model,
                        "input_tokens": token_usage.input_tokens,
                        "output_tokens": token_usage.output_tokens,
                        "total_tokens": token_usage.total_tokens,
                        "estimated_cost_usd": token_usage.estimated_cost_usd,
                        "timestamp": datetime.now(UTC).isoformat(),
                    },
                ))

        except Exception as e:
            logger.debug("Could not extract token usage: %s", e)
