#!/usr/bin/env python3
"""
Workflow Recorder - Capture screenshots and generate step-by-step Markdown documentation

Usage:
    python3 workflow-recorder.py --name "unifi-vlan-setup" --department "IT"

Hotkeys during recording:
    F9  - Take screenshot and advance step
    F10 - Add note to current step
    ESC - Stop recording and generate documentation

Requirements:
    pip install pillow pynput python-xlib  # Linux
    pip install pillow pynput pywin32      # Windows
"""

import argparse
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
import json

try:
    from PIL import ImageGrab
    from pynput import keyboard
    from pynput.keyboard import Key, KeyCode
except ImportError:
    print("ERROR: Required packages not installed")
    print("\nFor Linux (WSL/Ubuntu):")
    print("  sudo apt-get install python3-tk python3-dev")
    print("  pip3 install pillow pynput python-xlib")
    print("\nFor Windows:")
    print("  pip install pillow pynput pywin32")
    sys.exit(1)


class WorkflowRecorder:
    """Records workflow steps with screenshots and generates Markdown documentation"""

    def __init__(self, workflow_name: str, department: str = "IT", output_dir: str = "documentation"):
        self.workflow_name = workflow_name
        self.department = department
        self.output_dir = Path(output_dir)
        self.screenshots_dir = self.output_dir / "screenshots" / workflow_name
        self.workflows_dir = self.output_dir / "workflows"

        self.steps: List[Dict] = []
        self.current_step = 0
        self.recording = False
        self.notes_buffer = []

        # Create directories
        self.screenshots_dir.mkdir(parents=True, exist_ok=True)
        self.workflows_dir.mkdir(parents=True, exist_ok=True)

        print(f"\n{'='*60}")
        print(f"Workflow Recorder - {workflow_name}")
        print(f"Department: {department}")
        print(f"{'='*60}\n")
        print("Hotkeys:")
        print("  F9  - Take screenshot and advance step")
        print("  F10 - Add note to current step")
        print("  ESC - Stop recording and generate documentation\n")
        print("Ready to record. Press F9 to start capturing steps...")
        print(f"{'='*60}\n")

    def capture_screenshot(self) -> str:
        """Capture current screen and save to file"""
        self.current_step += 1
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"step{self.current_step:02d}_{timestamp}.png"
        filepath = self.screenshots_dir / filename

        try:
            screenshot = ImageGrab.grab()
            screenshot.save(filepath)
            print(f"✓ Screenshot saved: {filename}")
            return filename
        except Exception as e:
            print(f"✗ Error capturing screenshot: {e}")
            return None

    def add_step(self, screenshot_file: str):
        """Add a new step with screenshot"""
        step_title = input(f"\n[Step {self.current_step}] Enter step title (or press Enter to skip): ").strip()
        if not step_title:
            step_title = f"Step {self.current_step}"

        step_description = input(f"[Step {self.current_step}] Enter description (or press Enter to skip): ").strip()

        step_data = {
            "number": self.current_step,
            "title": step_title,
            "description": step_description,
            "screenshot": screenshot_file,
            "notes": self.notes_buffer.copy(),
            "timestamp": datetime.now().isoformat()
        }

        self.steps.append(step_data)
        self.notes_buffer.clear()
        print(f"✓ Step {self.current_step} added: {step_title}\n")

    def add_note(self):
        """Add a note to the current step"""
        note = input(f"\n[Note] Enter note for step {self.current_step}: ").strip()
        if note:
            self.notes_buffer.append(note)
            print(f"✓ Note added\n")

    def generate_markdown(self) -> str:
        """Generate Markdown documentation from recorded steps"""
        today = datetime.now().strftime("%Y-%m-%d")

        # Create header
        md_content = f"""# {self.workflow_name.replace('-', ' ').title()}

**Document Information:**
- Department: {self.department}
- Created: {today}
- Last Updated: {today}
- Owner: [Your Name/Team]
- Related Docs: []

## Overview
[Add a brief description of what this workflow accomplishes and when to use it]

## Prerequisites
- [Required access/permissions]
- [Tools needed]
- [Prior knowledge required]

## Steps

"""

        # Add each step
        for step in self.steps:
            md_content += f"### Step {step['number']}: {step['title']}\n"

            # Add screenshot
            if step['screenshot']:
                screenshot_path = f"../screenshots/{self.workflow_name}/{step['screenshot']}"
                md_content += f"![{step['title']}]({screenshot_path})\n\n"

            # Add description
            if step['description']:
                md_content += f"**What to do:**\n{step['description']}\n\n"
            else:
                md_content += "**What to do:**\n1. [Add detailed instructions]\n2. [Add additional details]\n3. [Add expected outcome]\n\n"

            # Add notes
            if step['notes']:
                md_content += "**Notes:**\n"
                for note in step['notes']:
                    md_content += f"- {note}\n"
                md_content += "\n"

        # Add footer sections
        md_content += """## Verification
[Add steps to verify the workflow completed successfully]

## Troubleshooting

**Issue: [Common Problem]**
- [Solution or diagnostic steps]

**Issue: [Another Problem]**
- [Solution or diagnostic steps]

## Related Resources
- [Links to other documentation]
- [External references]
- [Tool documentation]
"""

        return md_content

    def save_documentation(self):
        """Save the generated Markdown documentation"""
        md_content = self.generate_markdown()
        output_file = self.workflows_dir / f"{self.workflow_name}.md"

        with open(output_file, 'w') as f:
            f.write(md_content)

        print(f"\n{'='*60}")
        print(f"✓ Documentation generated successfully!")
        print(f"{'='*60}")
        print(f"\nMarkdown file: {output_file}")
        print(f"Screenshots:   {self.screenshots_dir}")
        print(f"Total steps:   {len(self.steps)}")
        print(f"\nNext steps:")
        print(f"1. Review and edit: {output_file}")
        print(f"2. Add missing descriptions and details")
        print(f"3. Export to PDF: pandoc {output_file.name} -o {self.workflow_name}.pdf")
        print(f"{'='*60}\n")

        # Save metadata
        metadata = {
            "workflow_name": self.workflow_name,
            "department": self.department,
            "created": datetime.now().isoformat(),
            "total_steps": len(self.steps),
            "steps": self.steps
        }

        metadata_file = self.workflows_dir / f"{self.workflow_name}.json"
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)

    def on_press(self, key):
        """Handle keyboard events"""
        try:
            # F9 - Capture screenshot
            if key == Key.f9:
                screenshot_file = self.capture_screenshot()
                if screenshot_file:
                    self.add_step(screenshot_file)
                return True

            # F10 - Add note
            elif key == Key.f10:
                self.add_note()
                return True

            # ESC - Stop recording
            elif key == Key.esc:
                print("\n⏹ Stopping recorder...")
                self.recording = False
                return False

        except AttributeError:
            pass

    def start_recording(self):
        """Start the keyboard listener and recording loop"""
        self.recording = True

        # Start keyboard listener
        with keyboard.Listener(on_press=self.on_press) as listener:
            listener.join()

        # Generate documentation when done
        if self.steps:
            self.save_documentation()
        else:
            print("\n⚠ No steps recorded. Exiting without generating documentation.")


def main():
    parser = argparse.ArgumentParser(
        description="Workflow Recorder - Capture screenshots and generate documentation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 workflow-recorder.py --name "unifi-vlan-setup" --department "IT"
  python3 workflow-recorder.py --name "client-onboarding" --department "Sales"
  python3 workflow-recorder.py --name "backup-procedure" --output ~/Documents/workflows
        """
    )

    parser.add_argument(
        '--name',
        required=True,
        help='Workflow name (use hyphens for spaces: "unifi-vlan-setup")'
    )

    parser.add_argument(
        '--department',
        default='IT',
        help='Department name (default: IT)'
    )

    parser.add_argument(
        '--output',
        default='documentation',
        help='Output directory (default: documentation)'
    )

    args = parser.parse_args()

    # Create recorder instance
    recorder = WorkflowRecorder(
        workflow_name=args.name,
        department=args.department,
        output_dir=args.output
    )

    # Start recording
    try:
        recorder.start_recording()
    except KeyboardInterrupt:
        print("\n\n⏹ Recording interrupted by user")
        if recorder.steps:
            save = input("Save documentation anyway? (y/n): ").lower()
            if save == 'y':
                recorder.save_documentation()
        sys.exit(0)


if __name__ == "__main__":
    main()
