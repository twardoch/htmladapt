# this_file: src/htmladapt/llm/reconciler.py
"""LLM-powered conflict resolution for HTMLAdapt."""

import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class LLMReconciler:
    """LLM-powered reconciler for resolving complex matching conflicts.

    Integrates with OpenAI API for semantic understanding of content
    when traditional algorithms fail to find matches.
    """

    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4o-mini",
        max_context_tokens: int = 1000
    ) -> None:
        """Initialize the LLM reconciler.

        Args:
            api_key: OpenAI API key
            model: LLM model name
            max_context_tokens: Maximum tokens per request
        """
        self.api_key = api_key
        self.model = model
        self.max_context_tokens = max_context_tokens

        # Try to import OpenAI client
        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=api_key)
            self._available = True
        except ImportError:
            logger.warning("OpenAI library not available. LLM reconciliation disabled.")
            self.client = None
            self._available = False

    def resolve_conflict(
        self,
        edited_content: str,
        original_candidates: list[str],
        context: dict | None = None
    ) -> dict:
        """Resolve matching conflict using LLM.

        Args:
            edited_content: Edited content that needs matching
            original_candidates: List of potential original content matches
            context: Additional context for resolution

        Returns:
            Resolution result with best match and confidence
        """
        if not self._available:
            return {
                "best_match_index": None,
                "confidence": 0.0,
                "reasoning": "LLM reconciliation not available"
            }

        try:
            prompt = self._build_resolution_prompt(
                edited_content,
                original_candidates,
                context
            )

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200,
                temperature=0.1
            )

            return self._parse_llm_response(response, len(original_candidates))

        except Exception as e:
            logger.error(f"LLM reconciliation failed: {e}")
            return {
                "best_match_index": None,
                "confidence": 0.0,
                "reasoning": f"LLM error: {str(e)}"
            }

    def _build_resolution_prompt(
        self,
        edited_content: str,
        original_candidates: list[str],
        context: dict | None = None
    ) -> str:
        """Build prompt for LLM conflict resolution.

        Args:
            edited_content: Edited content
            original_candidates: Original content candidates
            context: Additional context

        Returns:
            Formatted prompt string
        """
        prompt = f"""You are helping to match edited HTML content with its original version for content merging.

EDITED CONTENT:
{edited_content}

ORIGINAL CANDIDATES:
"""

        for i, candidate in enumerate(original_candidates):
            prompt += f"{i}: {candidate}\n"

        prompt += """
TASK: Identify which original candidate (by number) best matches the edited content semantically.
Consider:
- Meaning and intent preservation
- Content similarity despite text changes
- Structural equivalence

Respond with ONLY a JSON object:
{
  "match_index": <number or null>,
  "confidence": <0.0-1.0>,
  "reasoning": "<brief explanation>"
}"""

        return prompt

    def _parse_llm_response(self, response, num_candidates: int) -> dict:
        """Parse LLM response into structured result.

        Args:
            response: OpenAI API response
            num_candidates: Number of original candidates

        Returns:
            Parsed resolution result
        """
        try:
            import json

            content = response.choices[0].message.content.strip()

            # Try to extract JSON from response
            if content.startswith('{') and content.endswith('}'):
                result = json.loads(content)

                # Validate response
                match_index = result.get("match_index")
                if match_index is not None and not (0 <= match_index < num_candidates):
                    match_index = None

                confidence = result.get("confidence", 0.0)
                if not isinstance(confidence, (int, float)) or not (0.0 <= confidence <= 1.0):
                    confidence = 0.0

                return {
                    "best_match_index": match_index,
                    "confidence": float(confidence),
                    "reasoning": result.get("reasoning", "LLM resolution")
                }

        except Exception as e:
            logger.error(f"Failed to parse LLM response: {e}")

        return {
            "best_match_index": None,
            "confidence": 0.0,
            "reasoning": "Failed to parse LLM response"
        }

    def is_available(self) -> bool:
        """Check if LLM reconciliation is available.

        Returns:
            True if LLM client is available
        """
        return self._available