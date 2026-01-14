import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

"""
Metadata Extractor - OberaConnect Focused
Extracts ONLY operational metadata from documents (200 tokens max)
NO verbose summaries, NO generic content
"""
from typing import Dict, Any, List, Optional
from anthropic import Anthropic
from pathlib import Path
import re
from datetime import datetime

from core.config import ANTHROPIC_API_KEY, CLAUDE_MODEL


class MetadataExtractor:
    """Extract concise operational metadata from OberaConnect documents"""

    def __init__(self):
        if not ANTHROPIC_API_KEY:
            raise ValueError("ANTHROPIC_API_KEY not set in environment")

        self.client = Anthropic(api_key=ANTHROPIC_API_KEY)
        self.model = CLAUDE_MODEL
        print(f"✓ Metadata extractor initialized (model: {self.model})")

    def extract_metadata(
        self,
        raw_content: str,
        file_path: Optional[Path] = None
    ) -> Dict[str, Any]:
        """
        Extract ONLY operational metadata (200 tokens max)

        Returns:
        - document_type: contract/policy/procedure/config/call_flow
        - customer: Customer name or "internal"
        - technology: Specific vendor/platform
        - date: Document date
        - tags: OberaConnect-specific tags (max 5)
        - action_items: Specific tasks if any
        - key_contacts: Names/roles if applicable
        """

        # Prepare content sample (first 2000 chars to avoid token overflow)
        content_sample = raw_content[:2000]

        # Add filename context if available
        filename_context = ""
        if file_path:
            filename_context = f"\nFilename: {file_path.name}"

        prompt = f"""Extract ONLY operational metadata from this OberaConnect document.

{filename_context}

Document content:
---
{content_sample}
---

Extract ONLY these fields (be concise, max 10 words per field):

1. document_type: [contract/policy/procedure/config/call_flow/network_diagram/other]
2. customer: [specific customer name OR "internal" OR "N/A"]
3. technology: [specific vendor/platform like "SonicWall NSa 3700", "MikroTik CCR", "Azure VPN", "NinjaOne" OR "N/A"]
4. date: [any date found in YYYY-MM-DD format OR "N/A"]
5. tags: [max 5 OberaConnect-specific tags like "customer/city-of-freeport", "tech/sonicwall", "process/onboarding"]
6. action_items: [specific tasks/todos OR "none"]
7. key_contacts: [names and roles OR "none"]

Return ONLY a JSON object, NO explanations:
{{
  "document_type": "...",
  "customer": "...",
  "technology": "...",
  "date": "...",
  "tags": ["tag1", "tag2"],
  "action_items": ["item1"] or [],
  "key_contacts": ["name: role"] or []
}}"""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=200,  # STRICT LIMIT - forces concise output
                messages=[{"role": "user", "content": prompt}]
            )

            # Extract JSON from response
            import json
            content = response.content[0].text

            # Parse JSON
            if '{' in content:
                json_start = content.index('{')
                json_end = content.rindex('}') + 1
                json_str = content[json_start:json_end]
                metadata = json.loads(json_str)

                # Validate and clean
                metadata = self._validate_metadata(metadata)
                return metadata
            else:
                return self._fallback_metadata(file_path)

        except Exception as e:
            print(f"⚠ Metadata extraction failed: {e}")
            return self._fallback_metadata(file_path)

    def extract_call_flow_metadata(self, raw_content: str) -> Dict[str, Any]:
        """
        Specialized extraction for call flow documents
        """

        prompt = f"""Extract call flow details from this document.

{raw_content[:2000]}

Extract ONLY:
1. customer_name: [customer name]
2. phone_numbers: [list of phone numbers]
3. business_hours: [hours like "Mon-Fri 8am-5pm"]
4. routing_rules: [brief description]

Return JSON only:
{{
  "customer_name": "...",
  "phone_numbers": ["..."],
  "business_hours": "...",
  "routing_rules": "..."
}}"""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=200,
                messages=[{"role": "user", "content": prompt}]
            )

            import json
            content = response.content[0].text

            if '{' in content:
                json_start = content.index('{')
                json_end = content.rindex('}') + 1
                json_str = content[json_start:json_end]
                return json.loads(json_str)
            else:
                return {}

        except Exception as e:
            print(f"⚠ Call flow extraction failed: {e}")
            return {}

    def extract_contract_metadata(self, raw_content: str) -> Dict[str, Any]:
        """
        Specialized extraction for contract documents
        """

        prompt = f"""Extract contract details from this document.

{raw_content[:2000]}

Extract ONLY:
1. customer_name: [customer]
2. contract_type: [Managed Services/Voice/Network/etc]
3. start_date: [YYYY-MM-DD]
4. end_date: [YYYY-MM-DD]
5. renewal_terms: [brief]
6. services: [list]

Return JSON only:
{{
  "customer_name": "...",
  "contract_type": "...",
  "start_date": "...",
  "end_date": "...",
  "renewal_terms": "...",
  "services": ["..."]
}}"""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=200,
                messages=[{"role": "user", "content": prompt}]
            )

            import json
            content = response.content[0].text

            if '{' in content:
                json_start = content.index('{')
                json_end = content.rindex('}') + 1
                json_str = content[json_start:json_end]
                return json.loads(json_str)
            else:
                return {}

        except Exception as e:
            print(f"⚠ Contract extraction failed: {e}")
            return {}

    def _validate_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and clean extracted metadata"""

        # Ensure required fields exist
        required_fields = ["document_type", "customer", "technology", "tags"]
        for field in required_fields:
            if field not in metadata:
                metadata[field] = "N/A" if field != "tags" else []

        # Limit tags to 5
        if isinstance(metadata.get("tags"), list):
            metadata["tags"] = metadata["tags"][:5]

        # Ensure lists for array fields
        for field in ["tags", "action_items", "key_contacts"]:
            if field in metadata and not isinstance(metadata[field], list):
                metadata[field] = []

        return metadata

    def _fallback_metadata(self, file_path: Optional[Path] = None) -> Dict[str, Any]:
        """Fallback metadata when extraction fails"""

        filename = file_path.name if file_path else "unknown"

        return {
            "document_type": "unknown",
            "customer": self._extract_customer_from_filename(filename),
            "technology": "N/A",
            "date": datetime.now().strftime("%Y-%m-%d"),
            "tags": [],
            "action_items": [],
            "key_contacts": []
        }

    def _extract_customer_from_filename(self, filename: str) -> str:
        """Try to extract customer name from filename"""

        # Common patterns in OberaConnect filenames
        filename_lower = filename.lower()

        known_customers = [
            "city of freeport", "freeport",
            "engel", "volker",
            "dunlap",
            "juban",
            "fortified",
            "jubilee",
            "roger",
            "tracery",
            "7 brew", "brew",
            "celebration",
            "setco"
        ]

        for customer in known_customers:
            if customer in filename_lower:
                return customer.title()

        return "N/A"
