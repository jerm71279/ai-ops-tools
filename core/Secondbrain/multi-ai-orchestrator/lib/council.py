#!/usr/bin/env python3
"""
AI Council - Multi-AI Consensus System

Sends the same prompt to multiple AI providers and synthesizes their responses.
Use for important decisions, code reviews, architecture planning, etc.

Usage:
    from lib.council import AICouncil

    council = AICouncil()
    result = council.deliberate("Should we use Redis or PostgreSQL for caching?")
    print(result.summary)
    print(result.consensus)

Author: OberaConnect Engineering
Version: 1.0.0
"""

import logging
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime

from .ai_clients import (
    AIProvider, AIResponse, AIClientFactory,
    ClaudeCLI, GeminiCLI, GrokCLI
)

logger = logging.getLogger(__name__)


@dataclass
class CouncilMember:
    """Represents an AI council member with role and expertise"""
    provider: AIProvider
    role: str
    expertise: List[str]
    weight: float = 1.0  # Voting weight for consensus


@dataclass
class CouncilVote:
    """A single AI's response/vote on a matter"""
    member: CouncilMember
    response: AIResponse
    vote: Optional[str] = None  # APPROVE, REJECT, ABSTAIN, or custom
    confidence: float = 0.0
    reasoning: str = ""


@dataclass
class CouncilDeliberation:
    """Result of a council deliberation"""
    prompt: str
    votes: List[CouncilVote]
    consensus: Optional[str] = None
    summary: str = ""
    dissenting_opinions: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "prompt": self.prompt,
            "votes": [
                {
                    "provider": v.member.provider.value,
                    "role": v.member.role,
                    "vote": v.vote,
                    "confidence": v.confidence,
                    "response": v.response.content[:500] + "..." if len(v.response.content) > 500 else v.response.content,
                    "reasoning": v.reasoning
                }
                for v in self.votes
            ],
            "consensus": self.consensus,
            "summary": self.summary,
            "dissenting_opinions": self.dissenting_opinions,
            "timestamp": self.timestamp
        }

    def to_markdown(self) -> str:
        """Format deliberation as markdown report"""
        md = f"""# AI Council Deliberation

**Timestamp:** {self.timestamp}

## Question
{self.prompt}

## Council Votes

"""
        for vote in self.votes:
            status = "✅" if vote.vote == "APPROVE" else "❌" if vote.vote == "REJECT" else "⚪"
            md += f"""### {vote.member.provider.value.title()} ({vote.member.role})
{status} **{vote.vote or 'No vote'}** (Confidence: {vote.confidence:.0%})

{vote.response.content[:1000]}{"..." if len(vote.response.content) > 1000 else ""}

---

"""

        md += f"""## Consensus
**{self.consensus or 'No consensus reached'}**

{self.summary}
"""

        if self.dissenting_opinions:
            md += "\n## Dissenting Opinions\n"
            for opinion in self.dissenting_opinions:
                md += f"- {opinion}\n"

        return md


# Default council members
DEFAULT_COUNCIL = [
    CouncilMember(
        provider=AIProvider.CLAUDE,
        role="Technical Architect",
        expertise=["code quality", "architecture", "security", "best practices"],
        weight=1.2
    ),
    CouncilMember(
        provider=AIProvider.GEMINI,
        role="Research Analyst",
        expertise=["documentation", "analysis", "patterns", "alternatives"],
        weight=1.0
    ),
    CouncilMember(
        provider=AIProvider.GROK,
        role="Devil's Advocate",
        expertise=["edge cases", "real-world issues", "alternative views"],
        weight=0.8
    ),
]


class AICouncil:
    """
    AI Council for multi-AI consensus decision making.

    Sends prompts to multiple AIs in parallel and synthesizes responses.
    """

    def __init__(
        self,
        members: Optional[List[CouncilMember]] = None,
        synthesizer: AIProvider = AIProvider.CLAUDE,
        timeout: int = 120,
        parallel: bool = True
    ):
        """
        Initialize AI Council.

        Args:
            members: List of council members (defaults to Claude, Gemini, Grok)
            synthesizer: AI to use for synthesizing final consensus
            timeout: Timeout per AI call in seconds
            parallel: Whether to query AIs in parallel
        """
        self.members = members or DEFAULT_COUNCIL
        self.synthesizer = synthesizer
        self.timeout = timeout
        self.parallel = parallel

        # Filter to only available members
        self.active_members = []
        for member in self.members:
            client = AIClientFactory.get_client(member.provider)
            if client.is_available:
                self.active_members.append(member)
            else:
                logger.warning(f"Council member {member.provider.value} not available")

    def get_status(self) -> Dict[str, Any]:
        """Get council status"""
        return {
            "total_members": len(self.members),
            "active_members": len(self.active_members),
            "members": [
                {
                    "provider": m.provider.value,
                    "role": m.role,
                    "available": m in self.active_members
                }
                for m in self.members
            ],
            "synthesizer": self.synthesizer.value
        }

    def _query_member(
        self,
        member: CouncilMember,
        prompt: str,
        context: Optional[str] = None
    ) -> CouncilVote:
        """Query a single council member"""
        client = AIClientFactory.get_client(member.provider)

        # Build role-specific prompt
        full_prompt = f"""You are serving as {member.role} on an AI Council.
Your expertise: {', '.join(member.expertise)}

Please analyze the following and provide your assessment:

{prompt}

{f'Additional context: {context}' if context else ''}

Provide:
1. Your analysis
2. Your vote (APPROVE, REJECT, or NEEDS_DISCUSSION)
3. Your confidence level (0-100%)
4. Key reasoning points
"""

        try:
            response = client.execute(full_prompt)

            # Extract vote from response (simple heuristic)
            content_lower = response.content.lower()
            if "approve" in content_lower and "reject" not in content_lower:
                vote = "APPROVE"
            elif "reject" in content_lower:
                vote = "REJECT"
            else:
                vote = "NEEDS_DISCUSSION"

            # Estimate confidence (simple heuristic)
            confidence = 0.7
            if "confident" in content_lower or "strongly" in content_lower:
                confidence = 0.9
            elif "uncertain" in content_lower or "maybe" in content_lower:
                confidence = 0.5

            return CouncilVote(
                member=member,
                response=response,
                vote=vote,
                confidence=confidence,
                reasoning=response.content[:500]
            )

        except Exception as e:
            logger.error(f"Error querying {member.provider.value}: {e}")
            return CouncilVote(
                member=member,
                response=AIResponse(
                    provider=member.provider,
                    success=False,
                    content="",
                    raw_output="",
                    error=str(e)
                ),
                vote="ABSTAIN",
                confidence=0.0,
                reasoning=f"Error: {e}"
            )

    def deliberate(
        self,
        prompt: str,
        context: Optional[str] = None,
        require_consensus: bool = False,
        synthesize: bool = True
    ) -> CouncilDeliberation:
        """
        Convene the council to deliberate on a matter.

        Args:
            prompt: The question or matter to deliberate
            context: Additional context (code, files, etc.)
            require_consensus: If True, keeps deliberating until consensus
            synthesize: If True, have synthesizer AI summarize results

        Returns:
            CouncilDeliberation with votes and consensus
        """
        logger.info(f"Council deliberating: {prompt[:100]}...")

        votes: List[CouncilVote] = []

        if self.parallel and len(self.active_members) > 1:
            # Query all members in parallel
            with ThreadPoolExecutor(max_workers=len(self.active_members)) as executor:
                futures = {
                    executor.submit(self._query_member, member, prompt, context): member
                    for member in self.active_members
                }

                for future in as_completed(futures):
                    try:
                        vote = future.result(timeout=self.timeout)
                        votes.append(vote)
                        logger.info(f"{vote.member.provider.value}: {vote.vote}")
                    except Exception as e:
                        member = futures[future]
                        logger.error(f"Timeout/error for {member.provider.value}: {e}")
        else:
            # Query sequentially
            for member in self.active_members:
                vote = self._query_member(member, prompt, context)
                votes.append(vote)
                logger.info(f"{vote.member.provider.value}: {vote.vote}")

        # Calculate consensus
        approve_weight = sum(v.member.weight for v in votes if v.vote == "APPROVE")
        reject_weight = sum(v.member.weight for v in votes if v.vote == "REJECT")
        total_weight = sum(v.member.weight for v in votes if v.vote != "ABSTAIN")

        if total_weight > 0:
            if approve_weight / total_weight >= 0.6:
                consensus = "APPROVED"
            elif reject_weight / total_weight >= 0.6:
                consensus = "REJECTED"
            else:
                consensus = "NO_CONSENSUS"
        else:
            consensus = "NO_VOTES"

        # Find dissenting opinions
        dissenting = []
        majority_vote = "APPROVE" if consensus == "APPROVED" else "REJECT" if consensus == "REJECTED" else None
        if majority_vote:
            for vote in votes:
                if vote.vote and vote.vote != majority_vote and vote.vote != "ABSTAIN":
                    dissenting.append(f"{vote.member.provider.value} ({vote.member.role}): {vote.reasoning[:200]}")

        # Synthesize summary
        summary = ""
        if synthesize and len(votes) > 0:
            summary = self._synthesize_results(prompt, votes, consensus)

        return CouncilDeliberation(
            prompt=prompt,
            votes=votes,
            consensus=consensus,
            summary=summary,
            dissenting_opinions=dissenting
        )

    def _synthesize_results(
        self,
        prompt: str,
        votes: List[CouncilVote],
        consensus: str
    ) -> str:
        """Have the synthesizer AI summarize the council's deliberation"""

        votes_summary = "\n\n".join([
            f"### {v.member.provider.value} ({v.member.role})\n"
            f"Vote: {v.vote}\n"
            f"Response: {v.response.content[:800]}"
            for v in votes
        ])

        synth_prompt = f"""You are synthesizing the results of an AI Council deliberation.

ORIGINAL QUESTION:
{prompt}

COUNCIL VOTES:
{votes_summary}

PRELIMINARY CONSENSUS: {consensus}

Please provide:
1. A 2-3 sentence executive summary
2. Key points of agreement
3. Key points of disagreement
4. Recommended action

Keep your response under 300 words."""

        try:
            client = AIClientFactory.get_client(self.synthesizer)
            if client.is_available:
                response = client.execute(synth_prompt)
                return response.content
        except Exception as e:
            logger.error(f"Synthesis failed: {e}")

        return f"Consensus: {consensus}. {len(votes)} council members voted."

    def quick_vote(self, question: str) -> str:
        """
        Quick yes/no vote without full deliberation.

        Returns: "YES", "NO", or "UNDECIDED"
        """
        result = self.deliberate(
            prompt=f"Quick vote (YES or NO): {question}",
            synthesize=False
        )

        if result.consensus == "APPROVED":
            return "YES"
        elif result.consensus == "REJECTED":
            return "NO"
        return "UNDECIDED"

    def review_code(self, code: str, context: str = "") -> CouncilDeliberation:
        """Specialized method for code review"""
        prompt = f"""Please review this code for:
1. Security vulnerabilities
2. Performance issues
3. Code quality and best practices
4. Potential bugs

{context}

```
{code}
```

Vote APPROVE if the code is ready for production, REJECT if it needs significant changes."""

        return self.deliberate(prompt)

    def review_architecture(self, description: str) -> CouncilDeliberation:
        """Specialized method for architecture review"""
        prompt = f"""Please review this architecture/design decision:

{description}

Consider:
1. Scalability
2. Maintainability
3. Security
4. Cost implications
5. Alternative approaches

Vote APPROVE if this is a sound approach, REJECT if there are significant concerns."""

        return self.deliberate(prompt)


    def review_tool_5layer(
        self,
        tool_name: str,
        description: str,
        code_or_docs: str = ""
    ) -> CouncilDeliberation:
        """
        Review a tool/project through the 5-Layer AI OS Model.

        The 5 Layers:
        1. Interface - API/CLI design, authentication, data formats
        2. Intelligence - Query processing, intent classification, NLP
        3. Orchestration - Workflow management, pipeline execution, state
        4. Agents - Specialized execution units, tool integrations
        5. Resources - External services, data stores, MCP servers

        Args:
            tool_name: Name of the tool/project
            description: What the tool does
            code_or_docs: Code snippets or documentation to review
        """
        prompt = f"""# 5-Layer AI OS Review: {tool_name}

You are reviewing this tool through the OberaConnect 5-Layer AI OS framework.

## Tool Description
{description}

{f'## Code/Documentation\n```\n{code_or_docs[:8000]}\n```' if code_or_docs else ''}

---

## Review each layer (score 1-10 and provide specific feedback):

### Layer 1: INTERFACE
- API/CLI design quality
- Authentication mechanisms
- Input validation
- Error handling
- Data format consistency

### Layer 2: INTELLIGENCE
- Query processing capabilities
- Intent classification accuracy
- Natural language understanding
- Response quality
- Context awareness

### Layer 3: ORCHESTRATION
- Workflow management
- Pipeline execution
- State management
- Error recovery
- Scheduling/triggers

### Layer 4: AGENTS
- Specialized execution units
- Tool integrations
- Autonomous capabilities
- Human-in-the-loop controls
- Safety guardrails

### Layer 5: RESOURCES
- External service connections
- Data store integrations
- MCP server compatibility
- Caching strategy
- Rate limiting

---

## Final Assessment
- Overall Score (1-10)
- APPROVE/REJECT for production use
- Top 3 strengths
- Top 3 areas for improvement
- Recommended next steps

Be specific and actionable in your feedback."""

        return self.deliberate(prompt, synthesize=True)

    def review_idea_5layer(
        self,
        idea_name: str,
        description: str,
        target_integration: str = ""
    ) -> CouncilDeliberation:
        """
        Review an idea/proposal through the 5-Layer framework.

        Args:
            idea_name: Name of the idea/proposal
            description: What the idea proposes
            target_integration: Where this would fit in the architecture
        """
        prompt = f"""# 5-Layer AI OS Idea Review: {idea_name}

You are evaluating this idea for integration into OberaConnect's 5-Layer AI OS.

## Idea Description
{description}

{f'## Target Integration Point\n{target_integration}' if target_integration else ''}

---

## Evaluate fit for each layer:

### Layer 1: INTERFACE Impact
- How would this affect API/CLI design?
- Authentication requirements?
- New data formats needed?

### Layer 2: INTELLIGENCE Impact
- New query types supported?
- Intent classification changes?
- NLP/processing requirements?

### Layer 3: ORCHESTRATION Impact
- New workflows needed?
- State management implications?
- Error handling considerations?

### Layer 4: AGENTS Impact
- New agent types required?
- Existing agent modifications?
- Human oversight requirements?

### Layer 5: RESOURCES Impact
- New external services needed?
- Data storage requirements?
- MCP server additions?

---

## Feasibility Assessment
- Implementation complexity (1-10)
- Value delivered (1-10)
- Risk level (1-10)
- APPROVE/REJECT recommendation
- Suggested implementation approach

Vote APPROVE if this idea should be pursued, REJECT if not worth the investment."""

        return self.deliberate(prompt, synthesize=True)

    def morning_standup(
        self,
        yesterday_summary: str = "",
        today_priorities: str = "",
        blockers: str = ""
    ) -> CouncilDeliberation:
        """
        AI Council morning standup - get multi-AI perspective on the day's work.

        Args:
            yesterday_summary: What was accomplished yesterday
            today_priorities: What's planned for today
            blockers: Current blockers or concerns
        """
        prompt = f"""# AI Council Morning Standup

## Yesterday's Progress
{yesterday_summary or 'Not provided'}

## Today's Priorities
{today_priorities or 'Not provided'}

## Current Blockers
{blockers or 'None reported'}

---

Please provide:
1. Assessment of yesterday's progress
2. Feedback on today's priorities (any concerns?)
3. Suggestions for blockers
4. Any risks we should be aware of
5. Recommended focus area

Keep feedback concise and actionable."""

        return self.deliberate(prompt, synthesize=True)


def run_council(prompt: str, output_format: str = "markdown") -> str:
    """
    Convenience function to run a council deliberation.

    Args:
        prompt: The question to deliberate
        output_format: "markdown", "json", or "text"

    Returns:
        Formatted result string
    """
    council = AICouncil()
    result = council.deliberate(prompt)

    if output_format == "json":
        return json.dumps(result.to_dict(), indent=2)
    elif output_format == "markdown":
        return result.to_markdown()
    else:
        return result.summary or str(result.consensus)
