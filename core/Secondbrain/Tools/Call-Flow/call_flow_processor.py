import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

#!/usr/bin/env python3
"""
Call Flow Processor - OberaConnect
Processes existing call flow documents from SharePoint into standardized format
"""

from typing import Dict, Any, List, Optional
from pathlib import Path
from docx import Document
import json
import re
from datetime import datetime
from call_flow_generator import CallFlowGenerator


class CallFlowProcessor:
    """Process existing call flow documents into standardized format"""

    # Field mappings from document labels to our standardized fields
    FIELD_MAPPINGS = {
        "business name": "business_name",
        "address": "address",
        "contact name": "contact_name",
        "contact number": "contact_number",
        "business hours": "business_hours",
        "main phone number": "main_phone_number",
        "current internet service provider": "internet_provider",
        "current it vendor": "it_vendor",
        "current phone vendor": "phone_vendor",
        "are we creating number(s) or porting number(s)": "creating_or_porting",
        "if porting": "numbers_to_port",
        "requested port date": "requested_port_date",
        "extension": "extension_list",
        "blf keys": "blf_keys",
        "portal access to connectware": "portal_access",
        "connectmobile application": "mobile_app_users",
        "texting": "texting_type",
        "which numbers need texting": "texting_numbers",
        "how are calls during business hours routed": "business_hours_routing",
        "is there a current script for the auto attendant": "auto_attendant_script",
        "how are after hours calls routed": "after_hours_routing",
        "is there a current script for after hours": "after_hours_script",
        "what do you want the after-hours vm to say": "after_hours_vm_message",
        "would you like standard voicemail or voicemail to email": "voicemail_type",
        "holiday schedule": "holiday_schedule",
        "faxing setup": "fax_setup",
        "phone training": "phone_training_needed",
        "integrations": "integrations",
        "paging setup": "paging_setup",
        "alarm lines": "alarm_lines",
        "elevator lines": "elevator_lines",
        "phone count": "phone_count",
        "cordless phone count": "cordless_count",
        "conference phone count": "conference_phone_count",
        "wall mounted phones": "wall_mounted_count",
        "headsets": "headsets",
        "call recording": "call_recording",
        "reporting": "reporting_needs"
    }

    def __init__(self):
        self.generator = CallFlowGenerator()
        self.sharepoint_dir = Path("input_documents/sharepoint/shared/preservation_hold_library")
        self.processed_dir = Path("call_flows_processed")
        self.processed_dir.mkdir(exist_ok=True)

        print(f"✓ Call Flow Processor initialized")
        print(f"  Source: {self.sharepoint_dir}")
        print(f"  Output: {self.processed_dir}")

    def find_call_flows(self) -> List[Path]:
        """Find all call flow documents in SharePoint directory"""
        call_flows = []

        if not self.sharepoint_dir.exists():
            print(f"⚠ SharePoint directory not found: {self.sharepoint_dir}")
            return call_flows

        for file_path in self.sharepoint_dir.glob("*.docx"):
            filename_lower = file_path.name.lower()
            if "call flow" in filename_lower or "phone menu" in filename_lower:
                call_flows.append(file_path)

        return sorted(call_flows)

    def extract_from_docx(self, file_path: Path) -> Dict[str, Any]:
        """
        Extract call flow data from a DOCX file

        Returns:
            Dictionary with extracted field values
        """
        doc = Document(file_path)
        extracted = {
            "source_document": file_path.name,
            "processed_at": datetime.now().isoformat()
        }

        # Get all text content
        full_text = []
        for para in doc.paragraphs:
            text = para.text.strip()
            if text:
                full_text.append(text)

        # Process each line looking for field:value patterns
        current_field = None
        current_value = []

        for line in full_text:
            # Check if this line contains a field label
            matched_field = None
            for label, field_name in self.FIELD_MAPPINGS.items():
                if label in line.lower():
                    matched_field = field_name
                    # Extract value after the colon or question mark
                    if ':' in line:
                        value = line.split(':', 1)[1].strip()
                    elif '?' in line:
                        value = line.split('?', 1)[1].strip()
                    else:
                        value = ""

                    # Save previous field if exists
                    if current_field and current_value:
                        extracted[current_field] = ' '.join(current_value)

                    current_field = field_name
                    current_value = [value] if value else []
                    break

            # If no field matched and we have a current field, this is continuation
            if not matched_field and current_field:
                current_value.append(line)

        # Save last field
        if current_field and current_value:
            extracted[current_field] = ' '.join(current_value)

        # Post-process certain fields
        extracted = self._post_process(extracted)

        return extracted

    def _post_process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Post-process extracted data for consistency"""

        # Extract customer name from business name or filename
        if "business_name" not in data or not data.get("business_name"):
            # Try to extract from source document name
            source = data.get("source_document", "")
            if source:
                # Extract customer name from filename like "Tracery Interiors Call Flow_..."
                match = re.match(r"(.+?)(?:\s+Call Flow|\s+Phone)", source)
                if match:
                    data["business_name"] = match.group(1).strip()

        # Normalize creating_or_porting
        cop = data.get("creating_or_porting", "").lower()
        if "port" in cop:
            data["creating_or_porting"] = "porting"
        elif "creat" in cop:
            data["creating_or_porting"] = "creating"

        # Parse phone numbers from text
        if "numbers_to_port" in data:
            numbers_text = data["numbers_to_port"]
            # Find all phone number patterns
            numbers = re.findall(r'\d{10}|\d{3}[-.\s]?\d{3}[-.\s]?\d{4}', numbers_text)
            # Clean and format
            cleaned = [re.sub(r'[^\d]', '', n) for n in numbers]
            data["numbers_to_port"] = cleaned if cleaned else numbers_text

        return data

    def process_single(self, file_path: Path) -> Dict[str, Any]:
        """
        Process a single call flow document

        Returns:
            Extracted and standardized data
        """
        print(f"\n📄 Processing: {file_path.name}")

        # Extract data
        data = self.extract_from_docx(file_path)

        # Save as JSON
        customer_name = data.get("business_name", "unknown")
        safe_name = re.sub(r'[^\w\s-]', '', customer_name).replace(' ', '_')
        json_file = self.processed_dir / f"{safe_name}_data.json"

        with open(json_file, 'w') as f:
            json.dump(data, f, indent=2, default=str)

        print(f"   ✓ Extracted to: {json_file.name}")

        # Generate standardized DOCX
        try:
            output_path = self.generator.create_call_flow(data)
            print(f"   ✓ Generated standardized: {output_path.name}")
        except Exception as e:
            print(f"   ⚠ Could not generate DOCX: {e}")

        return data

    def process_all(self) -> List[Dict[str, Any]]:
        """
        Process all call flow documents found in SharePoint

        Returns:
            List of extracted data for all call flows
        """
        call_flows = self.find_call_flows()

        if not call_flows:
            print("⚠ No call flow documents found")
            return []

        print(f"\n📁 Found {len(call_flows)} call flow documents")
        print("=" * 50)

        results = []
        errors = []

        for file_path in call_flows:
            try:
                data = self.process_single(file_path)
                results.append(data)
            except Exception as e:
                print(f"   ❌ Error: {e}")
                errors.append({
                    "file": file_path.name,
                    "error": str(e)
                })

        # Summary
        print("\n" + "=" * 50)
        print("PROCESSING SUMMARY")
        print("=" * 50)
        print(f"✅ Successfully processed: {len(results)}")
        print(f"❌ Errors: {len(errors)}")

        if errors:
            print("\nError details:")
            for err in errors:
                print(f"  - {err['file']}: {err['error']}")

        # Save summary
        summary = {
            "processed_at": datetime.now().isoformat(),
            "total_found": len(call_flows),
            "successful": len(results),
            "errors": errors,
            "customers": [r.get("business_name", "Unknown") for r in results]
        }

        summary_file = self.processed_dir / "processing_summary.json"
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)

        print(f"\n📊 Summary saved to: {summary_file}")

        return results

    def generate_index(self) -> Path:
        """
        Generate an index file of all processed call flows

        Returns:
            Path to index file
        """
        # Get all processed JSON files
        json_files = list(self.processed_dir.glob("*_data.json"))

        index_data = []
        for json_file in json_files:
            with open(json_file, 'r') as f:
                data = json.load(f)
                index_data.append({
                    "customer": data.get("business_name", "Unknown"),
                    "main_number": data.get("main_phone_number", ""),
                    "contact": data.get("contact_name", ""),
                    "file": json_file.name,
                    "source": data.get("source_document", "")
                })

        # Sort by customer name
        index_data.sort(key=lambda x: x["customer"])

        # Save index
        index_file = self.processed_dir / "call_flow_index.json"
        with open(index_file, 'w') as f:
            json.dump(index_data, f, indent=2)

        print(f"\n📇 Index generated: {index_file}")
        print(f"   Total call flows indexed: {len(index_data)}")

        return index_file


def main():
    """Process all existing call flows"""
    processor = CallFlowProcessor()

    print("\n" + "=" * 50)
    print("CALL FLOW BATCH PROCESSOR")
    print("=" * 50)

    # Process all call flows
    results = processor.process_all()

    # Generate index
    if results:
        processor.generate_index()

    print("\n✅ Processing complete!")
    print(f"   Processed files in: {processor.processed_dir}")


if __name__ == "__main__":
    main()
