"""
Claude Processor - Simplified stub version
Uses Claude API to structure content and check consistency
"""
from typing import Dict, Any, List
from anthropic import Anthropic

from .config import ANTHROPIC_API_KEY, CLAUDE_MODEL


class ClaudeProcessor:
    """Uses Claude to process and structure content"""

    def __init__(self):
        if not ANTHROPIC_API_KEY:
            raise ValueError("ANTHROPIC_API_KEY not set in environment")

        self.client = Anthropic(api_key=ANTHROPIC_API_KEY)
        self.model = CLAUDE_MODEL

        print(f"✓ Claude processor initialized (model: {self.model})")

    def structure_content(
        self,
        raw_content: str,
        existing_concepts: List[str] = None,
        similar_notes: List[Dict] = None
    ) -> Dict[str, Any]:
        """
        Extract CONCISE operational metadata (NO verbose content)

        NEW APPROACH: Extract only operational metadata, preserve source
        - Max 200 tokens output
        - OberaConnect-specific fields only
        - No generic summaries or explanations
        """

        # Create concise prompt focused on OberaConnect operations
        prompt = f"""Extract ONLY operational metadata from this OberaConnect document.

Document content (sample):
---
{raw_content[:2000]}
---

Extract these fields (max 10 words each):
1. document_type: [contract/policy/procedure/config/call_flow/other]
2. customer: [specific customer name OR "internal"]
3. technology: [vendor/platform like "SonicWall", "MikroTik", "Azure"]
4. tags: [max 5 OberaConnect tags like "customer/freeport", "tech/sonicwall"]
5. key_data: [critical info only - dates, contacts, IPs]

Return ONLY JSON, NO explanations:
{{
  "title": "brief title",
  "document_type": "...",
  "customer": "...",
  "technology": "...",
  "tags": ["tag1", "tag2"],
  "key_data": {{"field": "value"}},
  "concepts": []
}}"""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=200,  # REDUCED from 2000 - forces concise output
                messages=[{"role": "user", "content": prompt}]
            )

            # Extract JSON from response
            import json
            content = response.content[0].text

            # Try to parse JSON
            if '{' in content:
                json_start = content.index('{')
                json_end = content.rindex('}') + 1
                json_str = content[json_start:json_end]
                structured = json.loads(json_str)
                return structured
            else:
                # Fallback structure
                return self._fallback_structure(raw_content)

        except Exception as e:
            print(f"⚠ Claude structuring failed: {e}")
            return self._fallback_structure(raw_content)

    def check_consistency(self, structured_note: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check a note for consistency issues

        Returns:
        - score: consistency score (0-1)
        - issues: list of problems found
        - suggestions: improvement recommendations
        """

        prompt = f"""Check this note for consistency and quality issues:

Title: {structured_note.get('title')}
Summary: {structured_note.get('summary')}
Concepts: {', '.join(structured_note.get('concepts', []))}

Look for:
- Unclear terminology
- Missing definitions
- Inconsistent naming
- Gaps in explanation

Respond with JSON:
{{
  "score": 0.85,
  "issues": ["issue1", "issue2"],
  "suggestions": ["suggestion1", "suggestion2"]
}}"""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1000,
                messages=[{"role": "user", "content": prompt}]
            )

            import json
            content = response.content[0].text

            if '{' in content:
                json_start = content.index('{')
                json_end = content.rindex('}') + 1
                json_str = content[json_start:json_end]
                result = json.loads(json_str)
                return result
            else:
                return {"score": 0.80, "issues": [], "suggestions": []}

        except Exception as e:
            print(f"⚠ Consistency check failed: {e}")
            return {"score": 0.80, "issues": [], "suggestions": []}

    def analyze_patterns(self, notes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze multiple notes for patterns and insights

        Used by Agent 2 (NotebookLM Analyst)
        """

        # Create summary of notes
        note_summaries = []
        for note in notes[:10]:  # Limit to avoid token overflow
            note_summaries.append(f"- {note.get('title', 'Untitled')}: {note.get('summary', '')[:100]}")

        summaries_text = '\n'.join(note_summaries)

        prompt = f"""Analyze these notes for patterns and consistency issues:

{summaries_text}

Identify:
1. Common themes/patterns
2. Terminology inconsistencies
3. Documentation gaps
4. Improvement opportunities

Respond with JSON:
{{
  "patterns": ["pattern1", "pattern2"],
  "inconsistencies": ["issue1", "issue2"],
  "gaps": ["gap1", "gap2"],
  "recommendations": ["rec1", "rec2"]
}}"""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1500,
                messages=[{"role": "user", "content": prompt}]
            )

            import json
            content = response.content[0].text

            if '{' in content:
                json_start = content.index('{')
                json_end = content.rindex('}') + 1
                json_str = content[json_start:json_end]
                result = json.loads(json_str)
                return result
            else:
                return {"patterns": [], "inconsistencies": [], "gaps": [], "recommendations": []}

        except Exception as e:
            print(f"⚠ Pattern analysis failed: {e}")
            return {"patterns": [], "inconsistencies": [], "gaps": [], "recommendations": []}

    def _fallback_structure(self, raw_content: str) -> Dict[str, Any]:
        """Fallback structure when Claude API fails - metadata only, no verbose content"""
        lines = raw_content.split('\n')
        title = lines[0][:100] if lines else "Untitled"

        return {
            "title": title,
            "document_type": "unknown",
            "customer": "unknown",
            "technology": "",
            "tags": [],
            "key_data": {},
            "concepts": []
        }
