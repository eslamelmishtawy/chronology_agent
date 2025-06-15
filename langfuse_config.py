"""
Langfuse configuration and initialization for local tracing.
"""
import os
from functools import wraps
from typing import Any, Dict, Optional

# Optional Langfuse imports - gracefully handle missing dependencies
try:
    from langfuse import Langfuse
    from langfuse.callback import CallbackHandler
    from langfuse.decorators import langfuse_context, observe
    LANGFUSE_AVAILABLE = True
except ImportError:
    # Fallback for when Langfuse is not available (cloud deployment)
    LANGFUSE_AVAILABLE = False

    # Mock classes to prevent import errors
    class Langfuse:
        def __init__(self, *args, **kwargs):
            pass
        def trace(self, *args, **kwargs):
            return MockTrace()
        def flush(self):
            pass

    class CallbackHandler:
        def __init__(self, *args, **kwargs):
            pass

    class MockTrace:
        def update(self, *args, **kwargs):
            pass

    def observe(*args, **kwargs):
        def decorator(func):
            return func
        return decorator

    class MockContext:
        def update_current_observation(self, *args, **kwargs):
            pass

    langfuse_context = MockContext()


class LangfuseConfig:
    """Langfuse configuration and utilities for local tracing."""

    def __init__(self):
        if LANGFUSE_AVAILABLE:
            # Initialize Langfuse client for local deployment
            self.langfuse = Langfuse(
                public_key="pk-lf-eec38d61-338e-42a0-8727-12e48136a21d",
                secret_key="sk-lf-3de841e7-c088-4252-8f28-f84d1e517a3d",
                host=os.getenv("LANGFUSE_HOST", "http://localhost:3000")
            )

            # Create callback handler for LangChain integration
            self.callback_handler = CallbackHandler(
                public_key="pk-lf-eec38d61-338e-42a0-8727-12e48136a21d",
                secret_key="sk-lf-3de841e7-c088-4252-8f28-f84d1e517a3d",
                host=os.getenv("LANGFUSE_HOST", "http://localhost:3000")
            )
        else:
            # Use mock objects when Langfuse is not available
            self.langfuse = Langfuse()
            self.callback_handler = CallbackHandler()

    def get_callback_handler(self):
        """Get LangChain callback handler for tracing."""
        return self.callback_handler

    def create_trace(self, name: str, metadata: Optional[Dict[str, Any]] = None):
        """Create a new trace."""
        return self.langfuse.trace(name=name, metadata=metadata or {})

    def flush(self):
        """Flush all pending traces."""
        self.langfuse.flush()


# Global Langfuse configuration instance
langfuse_config = LangfuseConfig()


def trace_function(name: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None):
    """
    Decorator to trace function calls with Langfuse.

    Args:
        name: Custom name for the trace (defaults to function name)
        metadata: Additional metadata to include in the trace
    """
    def decorator(func):
        @observe(name=name or func.__name__)
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Add function metadata
            if metadata:
                langfuse_context.update_current_observation(metadata=metadata)

            # Add input parameters to trace
            langfuse_context.update_current_observation(
                input={
                    "args": [str(arg)[:100] + "..." if len(str(arg)) > 100 else str(arg) for arg in args],
                    "kwargs": {k: str(v)[:100] + "..." if len(str(v)) > 100 else str(v) for k, v in kwargs.items()}
                }
            )

            try:
                result = func(*args, **kwargs)

                # Add output to trace (truncate if too long)
                output_str = str(result)
                if len(output_str) > 1000:
                    output_str = output_str[:1000] + "... (truncated)"

                langfuse_context.update_current_observation(output={"result": output_str})
                return result

            except Exception as e:
                # Log error in trace
                langfuse_context.update_current_observation(
                    level="ERROR",
                    status_message=str(e)
                )
                raise

        return wrapper
    return decorator


def trace_workflow_step(step_name: str):
    """
    Decorator specifically for workflow steps.

    Args:
        step_name: Name of the workflow step
    """
    return trace_function(
        name=f"workflow_step_{step_name}",
        metadata={"step_type": "workflow", "step_name": step_name}
    )


def trace_llm_call(model_name: Optional[str] = None):
    """
    Decorator for LLM calls.

    Args:
        model_name: Name of the LLM model being used
    """
    return trace_function(
        name="llm_call",
        metadata={"call_type": "llm", "model": model_name}
    )


def trace_tool_call(tool_name: str):
    """
    Decorator for tool calls.

    Args:
        tool_name: Name of the tool being called
    """
    return trace_function(
        name=f"tool_{tool_name}",
        metadata={"call_type": "tool", "tool_name": tool_name}
    )
