"""Token tracking utility for monitoring LLM usage"""

from dataclasses import dataclass
from typing import List
import time

@dataclass
class TokenUsage:
    """Represents token usage for a single request"""
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    timestamp: float
    model: str
    request_type: str = "text"  # text, image, or vision
    
    @property
    def cost_estimate(self) -> float:
        """Estimate cost (for reference, Ollama is free)"""
        return 0.0  # Ollama is free


class TokenTracker:
    """Track token usage across multiple requests"""
    
    def __init__(self):
        self.usage_history: List[TokenUsage] = []
        
    def add_usage(
        self, 
        prompt_tokens: int, 
        completion_tokens: int,
        model: str,
        request_type: str = "text"
    ) -> TokenUsage:
        """Add a new usage record"""
        usage = TokenUsage(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=prompt_tokens + completion_tokens,
            timestamp=time.time(),
            model=model,
            request_type=request_type
        )
        self.usage_history.append(usage)
        return usage
    
    def get_total_tokens(self) -> int:
        """Get total tokens used across all requests"""
        return sum(u.total_tokens for u in self.usage_history)
    
    def get_prompt_tokens(self) -> int:
        """Get total prompt tokens"""
        return sum(u.prompt_tokens for u in self.usage_history)
    
    def get_completion_tokens(self) -> int:
        """Get total completion tokens"""
        return sum(u.completion_tokens for u in self.usage_history)
    
    def get_summary(self) -> dict:
        """Get comprehensive usage summary"""
        total_requests = len(self.usage_history)
        total_tokens = self.get_total_tokens()
        avg_tokens = total_tokens / total_requests if total_requests > 0 else 0
        
        return {
            "total_requests": total_requests,
            "total_tokens": total_tokens,
            "prompt_tokens": self.get_prompt_tokens(),
            "completion_tokens": self.get_completion_tokens(),
            "avg_tokens_per_request": avg_tokens,
            "by_type": self._get_breakdown_by_type(),
            "by_model": self._get_breakdown_by_model()
        }
    
    def _get_breakdown_by_type(self) -> dict:
        """Get token breakdown by request type"""
        breakdown = {}
        for usage in self.usage_history:
            if usage.request_type not in breakdown:
                breakdown[usage.request_type] = 0
            breakdown[usage.request_type] += usage.total_tokens
        return breakdown
    
    def _get_breakdown_by_model(self) -> dict:
        """Get token breakdown by model"""
        breakdown = {}
        for usage in self.usage_history:
            if usage.model not in breakdown:
                breakdown[usage.model] = 0
            breakdown[usage.model] += usage.total_tokens
        return breakdown
    
    def reset(self):
        """Clear all usage history"""
        self.usage_history.clear()
    
    def format_summary(self) -> str:
        """Get formatted summary string"""
        summary = self.get_summary()
        return f"""
Token Usage Summary:
-------------------
Total Requests: {summary['total_requests']}
Total Tokens: {summary['total_tokens']:,}
  - Prompt: {summary['prompt_tokens']:,}
  - Completion: {summary['completion_tokens']:,}

By Request Type:
{self._format_dict(summary['by_type'])}

By Model:
{self._format_dict(summary['by_model'])}
        """.strip()
    
    def _format_dict(self, d: dict) -> str:
        """Format dictionary for display"""
        if not d:
            return "  (none)"
        return "\n".join([f"  - {k}: {v:,}" for k, v in d.items()])


def estimate_tokens(text: str) -> int:
    """Rough estimation of tokens (1 token ≈ 4 characters)"""
    return len(text) // 4
