#!/usr/bin/env python3
"""
Workflow Documenter - Desktop GUI Application

Simple desktop interface for workflow documentation with buttons for:
- Recording workflows with screenshot capture
- Exporting to PDF/HTML/Word
- Browsing existing workflows
- Managing documentation

Requirements:
    pip3 install pillow pynput
    sudo apt-get install python3-tk  # For Linux/WSL
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
from pathlib import Path
import subprocess
import os
import sys
import json
from datetime import datetime
import threading

try:
    from PIL import ImageGrab, ImageTk, Image
    from pynput import keyboard
    from pynput.keyboard import Key
except ImportError:
    print("ERROR: Required packages not installed")
    print("Run: pip3 install pillow pynput")
    sys.exit(1)


class WorkflowDocumenterGUI:
    """Desktop GUI for Workflow Documentation System"""

    def __init__(self, root):
        self.root = root
        self.root.title("Workflow Documenter")
        self.root.geometry("900x700")

        # Configuration
        self.base_dir = Path(__file__).parent.parent
        self.docs_dir = self.base_dir / "documentation"
        self.workflows_dir = self.docs_dir / "workflows"
        self.screenshots_dir = self.docs_dir / "screenshots"
        self.exports_dir = self.docs_dir / "exports"

        # Recording state
        self.recording = False
        self.current_workflow = None
        self.current_step = 0
        self.steps = []
        self.keyboard_listener = None

        # Create directories if they don't exist
        for directory in [self.workflows_dir, self.screenshots_dir, self.exports_dir]:
            directory.mkdir(parents=True, exist_ok=True)

        # Setup GUI
        self.create_widgets()
        self.refresh_workflow_list()

    def create_widgets(self):
        """Create the GUI layout"""

        # Title
        title_frame = tk.Frame(self.root, bg="#2c3e50", height=60)
        title_frame.pack(fill=tk.X, pady=(0, 10))
        title_frame.pack_propagate(False)

        title_label = tk.Label(
            title_frame,
            text="📝 Workflow Documenter",
            font=("Arial", 18, "bold"),
            bg="#2c3e50",
            fg="white"
        )
        title_label.pack(pady=15)

        # Main container
        main_container = tk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Left panel - Controls
        left_panel = tk.Frame(main_container, width=300)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, padx=(0, 10))
        left_panel.pack_propagate(False)

        # Recording section
        self.create_recording_section(left_panel)

        # Export section
        self.create_export_section(left_panel)

        # Quick actions
        self.create_quick_actions(left_panel)

        # Right panel - Workflow list and preview
        right_panel = tk.Frame(main_container)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.create_workflow_browser(right_panel)

        # Status bar
        self.create_status_bar()

    def create_recording_section(self, parent):
        """Create recording controls section"""

        frame = tk.LabelFrame(parent, text="📹 Record Workflow", padx=10, pady=10)
        frame.pack(fill=tk.X, pady=(0, 10))

        # Workflow name
        tk.Label(frame, text="Workflow Name:").pack(anchor=tk.W)
        self.workflow_name_var = tk.StringVar()
        tk.Entry(frame, textvariable=self.workflow_name_var, width=30).pack(fill=tk.X, pady=(0, 5))

        # Department
        tk.Label(frame, text="Department:").pack(anchor=tk.W)
        self.department_var = tk.StringVar(value="IT")
        departments = ["IT", "Sales", "Support", "Operations", "Finance"]
        ttk.Combobox(frame, textvariable=self.department_var, values=departments, width=27).pack(fill=tk.X, pady=(0, 10))

        # Start/Stop recording button
        self.record_btn = tk.Button(
            frame,
            text="▶ Start Recording",
            command=self.toggle_recording,
            bg="#27ae60",
            fg="white",
            font=("Arial", 10, "bold"),
            height=2
        )
        self.record_btn.pack(fill=tk.X, pady=(0, 5))

        # Screenshot button (disabled until recording)
        self.screenshot_btn = tk.Button(
            frame,
            text="📷 Take Screenshot (F9)",
            command=self.take_screenshot,
            bg="#3498db",
            fg="white",
            state=tk.DISABLED
        )
        self.screenshot_btn.pack(fill=tk.X, pady=(0, 5))

        # Step counter
        self.step_label = tk.Label(frame, text="Steps: 0", font=("Arial", 10))
        self.step_label.pack(anchor=tk.W)

    def create_export_section(self, parent):
        """Create export controls section"""

        frame = tk.LabelFrame(parent, text="📤 Export Workflow", padx=10, pady=10)
        frame.pack(fill=tk.X, pady=(0, 10))

        tk.Label(frame, text="Select workflow to export:").pack(anchor=tk.W, pady=(0, 5))

        # Workflow selector
        self.export_workflow_var = tk.StringVar()
        self.export_combo = ttk.Combobox(frame, textvariable=self.export_workflow_var, width=27, state="readonly")
        self.export_combo.pack(fill=tk.X, pady=(0, 10))

        # Export format buttons
        btn_frame = tk.Frame(frame)
        btn_frame.pack(fill=tk.X)

        tk.Button(
            btn_frame,
            text="PDF",
            command=lambda: self.export_workflow("pdf"),
            bg="#e74c3c",
            fg="white",
            width=8
        ).pack(side=tk.LEFT, padx=(0, 5))

        tk.Button(
            btn_frame,
            text="HTML",
            command=lambda: self.export_workflow("html"),
            bg="#3498db",
            fg="white",
            width=8
        ).pack(side=tk.LEFT, padx=(0, 5))

        tk.Button(
            btn_frame,
            text="Word",
            command=lambda: self.export_workflow("docx"),
            bg="#2980b9",
            fg="white",
            width=8
        ).pack(side=tk.LEFT)

    def create_quick_actions(self, parent):
        """Create quick action buttons"""

        frame = tk.LabelFrame(parent, text="⚡ Quick Actions", padx=10, pady=10)
        frame.pack(fill=tk.X)

        tk.Button(
            frame,
            text="📁 Open Documentation Folder",
            command=self.open_docs_folder,
            bg="#95a5a6",
            fg="white"
        ).pack(fill=tk.X, pady=(0, 5))

        tk.Button(
            frame,
            text="📁 Open Exports Folder",
            command=self.open_exports_folder,
            bg="#95a5a6",
            fg="white"
        ).pack(fill=tk.X, pady=(0, 5))

        tk.Button(
            frame,
            text="🔄 Refresh List",
            command=self.refresh_workflow_list,
            bg="#95a5a6",
            fg="white"
        ).pack(fill=tk.X)

    def create_workflow_browser(self, parent):
        """Create workflow browser section"""

        frame = tk.LabelFrame(parent, text="📚 Existing Workflows", padx=10, pady=10)
        frame.pack(fill=tk.BOTH, expand=True)

        # Search box
        search_frame = tk.Frame(frame)
        search_frame.pack(fill=tk.X, pady=(0, 5))
        tk.Label(search_frame, text="Search:").pack(side=tk.LEFT, padx=(0, 5))
        self.search_var = tk.StringVar()
        self.search_var.trace("w", lambda *args: self.filter_workflows())
        tk.Entry(search_frame, textvariable=self.search_var).pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Workflow listbox
        listbox_frame = tk.Frame(frame)
        listbox_frame.pack(fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(listbox_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.workflow_listbox = tk.Listbox(
            listbox_frame,
            yscrollcommand=scrollbar.set,
            font=("Arial", 10)
        )
        self.workflow_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.workflow_listbox.yview)

        self.workflow_listbox.bind("<<ListboxSelect>>", self.on_workflow_select)
        self.workflow_listbox.bind("<Double-Button-1>", self.open_workflow_file)

        # Preview area
        preview_frame = tk.LabelFrame(frame, text="Preview", padx=5, pady=5)
        preview_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))

        self.preview_text = scrolledtext.ScrolledText(
            preview_frame,
            wrap=tk.WORD,
            height=10,
            font=("Courier", 9)
        )
        self.preview_text.pack(fill=tk.BOTH, expand=True)

        # Action buttons for selected workflow
        action_frame = tk.Frame(frame)
        action_frame.pack(fill=tk.X, pady=(10, 0))

        tk.Button(
            action_frame,
            text="✏️ Edit",
            command=self.edit_workflow,
            bg="#f39c12",
            fg="white"
        ).pack(side=tk.LEFT, padx=(0, 5))

        tk.Button(
            action_frame,
            text="🗑️ Delete",
            command=self.delete_workflow,
            bg="#e74c3c",
            fg="white"
        ).pack(side=tk.LEFT)

    def create_status_bar(self):
        """Create status bar at bottom"""

        self.status_bar = tk.Label(
            self.root,
            text="Ready",
            bd=1,
            relief=tk.SUNKEN,
            anchor=tk.W,
            bg="#ecf0f1"
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    # Recording functions

    def toggle_recording(self):
        """Start or stop recording"""

        if not self.recording:
            self.start_recording()
        else:
            self.stop_recording()

    def start_recording(self):
        """Start recording workflow"""

        workflow_name = self.workflow_name_var.get().strip()
        if not workflow_name:
            messagebox.showerror("Error", "Please enter a workflow name")
            return

        # Sanitize workflow name
        workflow_name = workflow_name.lower().replace(" ", "-")
        self.current_workflow = workflow_name
        self.current_step = 0
        self.steps = []

        # Create screenshot directory
        (self.screenshots_dir / workflow_name).mkdir(parents=True, exist_ok=True)

        # Update UI
        self.recording = True
        self.record_btn.config(text="⏹ Stop Recording", bg="#e74c3c")
        self.screenshot_btn.config(state=tk.NORMAL)
        self.workflow_name_var.set(workflow_name)

        self.update_status(f"Recording: {workflow_name} (Press F9 to capture screenshots)")

        # Start keyboard listener for hotkeys
        self.start_keyboard_listener()

    def stop_recording(self):
        """Stop recording and generate documentation"""

        if not self.steps:
            messagebox.showwarning("Warning", "No steps recorded")
            self.recording = False
            self.record_btn.config(text="▶ Start Recording", bg="#27ae60")
            self.screenshot_btn.config(state=tk.DISABLED)
            self.update_status("Ready")
            if self.keyboard_listener:
                self.keyboard_listener.stop()
            return

        # Generate markdown
        self.generate_markdown()

        # Update UI
        self.recording = False
        self.record_btn.config(text="▶ Start Recording", bg="#27ae60")
        self.screenshot_btn.config(state=tk.DISABLED)
        self.step_label.config(text="Steps: 0")

        # Stop keyboard listener
        if self.keyboard_listener:
            self.keyboard_listener.stop()

        self.update_status(f"Documentation saved: {self.current_workflow}.md")
        self.refresh_workflow_list()

        messagebox.showinfo(
            "Success",
            f"Workflow documentation created!\n\nFile: {self.current_workflow}.md\nSteps: {len(self.steps)}"
        )

    def take_screenshot(self):
        """Capture screenshot and add step"""

        if not self.recording:
            return

        self.current_step += 1
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"step{self.current_step:02d}_{timestamp}.png"
        filepath = self.screenshots_dir / self.current_workflow / filename

        try:
            # Minimize window before screenshot
            self.root.iconify()
            self.root.update()

            # Wait a moment for window to minimize
            self.root.after(500, lambda: self._capture_screenshot(filepath, filename))

        except Exception as e:
            messagebox.showerror("Error", f"Failed to capture screenshot: {e}")
            self.current_step -= 1

    def _capture_screenshot(self, filepath, filename):
        """Actually capture the screenshot after window is minimized"""

        try:
            screenshot = ImageGrab.grab()
            screenshot.save(filepath)

            # Restore window
            self.root.deiconify()

            # Prompt for step details
            self.prompt_step_details(filename)

        except Exception as e:
            self.root.deiconify()
            messagebox.showerror("Error", f"Failed to capture screenshot: {e}")
            self.current_step -= 1

    def prompt_step_details(self, screenshot_file):
        """Prompt user for step title and description"""

        dialog = tk.Toplevel(self.root)
        dialog.title(f"Step {self.current_step} Details")
        dialog.geometry("500x300")
        dialog.transient(self.root)
        dialog.grab_set()

        tk.Label(dialog, text=f"Step {self.current_step}", font=("Arial", 12, "bold")).pack(pady=10)

        tk.Label(dialog, text="Step Title:").pack(anchor=tk.W, padx=20)
        title_var = tk.StringVar(value=f"Step {self.current_step}")
        title_entry = tk.Entry(dialog, textvariable=title_var, width=50)
        title_entry.pack(padx=20, fill=tk.X)
        title_entry.focus_set()

        tk.Label(dialog, text="Description:").pack(anchor=tk.W, padx=20, pady=(10, 0))
        desc_text = scrolledtext.ScrolledText(dialog, height=8, width=50)
        desc_text.pack(padx=20, fill=tk.BOTH, expand=True)

        def save_step():
            step_data = {
                "number": self.current_step,
                "title": title_var.get().strip() or f"Step {self.current_step}",
                "description": desc_text.get("1.0", tk.END).strip(),
                "screenshot": screenshot_file,
                "timestamp": datetime.now().isoformat()
            }
            self.steps.append(step_data)
            self.step_label.config(text=f"Steps: {len(self.steps)}")
            self.update_status(f"Step {self.current_step} added: {step_data['title']}")
            dialog.destroy()

        tk.Button(dialog, text="Save Step", command=save_step, bg="#27ae60", fg="white").pack(pady=10)

    def start_keyboard_listener(self):
        """Start listening for keyboard hotkeys"""

        def on_press(key):
            try:
                if key == Key.f9 and self.recording:
                    self.root.after(0, self.take_screenshot)
            except:
                pass

        self.keyboard_listener = keyboard.Listener(on_press=on_press)
        self.keyboard_listener.start()

    def generate_markdown(self):
        """Generate Markdown documentation from recorded steps"""

        today = datetime.now().strftime("%Y-%m-%d")
        department = self.department_var.get()

        md_content = f"""# {self.current_workflow.replace('-', ' ').title()}

**Document Information:**
- Department: {department}
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

        for step in self.steps:
            md_content += f"### Step {step['number']}: {step['title']}\n"
            screenshot_path = f"../screenshots/{self.current_workflow}/{step['screenshot']}"
            md_content += f"![{step['title']}]({screenshot_path})\n\n"

            if step['description']:
                md_content += f"**What to do:**\n{step['description']}\n\n"
            else:
                md_content += "**What to do:**\n1. [Add detailed instructions]\n\n"

        md_content += """## Verification
[Add steps to verify the workflow completed successfully]

## Troubleshooting

**Issue: [Common Problem]**
- [Solution or diagnostic steps]

## Related Resources
- [Links to other documentation]
"""

        # Save markdown file
        output_file = self.workflows_dir / f"{self.current_workflow}.md"
        with open(output_file, 'w') as f:
            f.write(md_content)

    # Export functions

    def export_workflow(self, format_type):
        """Export selected workflow to specified format"""

        workflow = self.export_workflow_var.get()
        if not workflow:
            messagebox.showerror("Error", "Please select a workflow to export")
            return

        input_file = self.workflows_dir / workflow
        if not input_file.exists():
            messagebox.showerror("Error", f"Workflow file not found: {workflow}")
            return

        self.update_status(f"Exporting {workflow} to {format_type.upper()}...")

        # Run export script
        export_script = Path(__file__).parent / "export-workflow.py"
        cmd = [
            sys.executable,
            str(export_script),
            "--input", str(input_file),
            "--format", format_type
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            output_file = self.exports_dir / f"{input_file.stem}.{format_type if format_type != 'docx' else 'docx'}"

            if output_file.exists():
                messagebox.showinfo("Success", f"Exported to:\n{output_file}")
                self.update_status(f"Export complete: {output_file.name}")
            else:
                messagebox.showinfo("Export", result.stdout)

        except subprocess.CalledProcessError as e:
            messagebox.showerror("Export Error", f"Export failed:\n{e.stderr}")
            self.update_status("Export failed")

    # Workflow browser functions

    def refresh_workflow_list(self):
        """Refresh the list of workflows"""

        self.workflow_listbox.delete(0, tk.END)
        workflows = sorted(self.workflows_dir.glob("*.md"))

        self.all_workflows = [wf.name for wf in workflows]

        for workflow in workflows:
            self.workflow_listbox.insert(tk.END, workflow.name)

        # Update export combo box
        self.export_combo['values'] = self.all_workflows
        if self.all_workflows:
            self.export_combo.current(0)

    def filter_workflows(self):
        """Filter workflows based on search"""

        search_term = self.search_var.get().lower()
        self.workflow_listbox.delete(0, tk.END)

        for workflow in self.all_workflows:
            if search_term in workflow.lower():
                self.workflow_listbox.insert(tk.END, workflow)

    def on_workflow_select(self, event):
        """Handle workflow selection"""

        selection = self.workflow_listbox.curselection()
        if not selection:
            return

        workflow_name = self.workflow_listbox.get(selection[0])
        workflow_file = self.workflows_dir / workflow_name

        # Show preview
        try:
            with open(workflow_file, 'r') as f:
                content = f.read()

            self.preview_text.delete("1.0", tk.END)
            self.preview_text.insert("1.0", content[:2000])  # Show first 2000 chars

            if len(content) > 2000:
                self.preview_text.insert(tk.END, "\n\n... (preview truncated)")

        except Exception as e:
            self.preview_text.delete("1.0", tk.END)
            self.preview_text.insert("1.0", f"Error reading file: {e}")

    def open_workflow_file(self, event):
        """Open workflow file in default editor"""

        selection = self.workflow_listbox.curselection()
        if not selection:
            return

        workflow_name = self.workflow_listbox.get(selection[0])
        workflow_file = self.workflows_dir / workflow_name

        self.open_file_in_editor(workflow_file)

    def edit_workflow(self):
        """Edit selected workflow"""

        selection = self.workflow_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a workflow to edit")
            return

        workflow_name = self.workflow_listbox.get(selection[0])
        workflow_file = self.workflows_dir / workflow_name

        self.open_file_in_editor(workflow_file)

    def delete_workflow(self):
        """Delete selected workflow"""

        selection = self.workflow_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a workflow to delete")
            return

        workflow_name = self.workflow_listbox.get(selection[0])

        if messagebox.askyesno("Confirm Delete", f"Delete workflow:\n{workflow_name}\n\nThis cannot be undone!"):
            workflow_file = self.workflows_dir / workflow_name
            try:
                workflow_file.unlink()
                self.refresh_workflow_list()
                self.preview_text.delete("1.0", tk.END)
                messagebox.showinfo("Success", "Workflow deleted")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete:\n{e}")

    def open_file_in_editor(self, filepath):
        """Open file in default editor"""

        try:
            if sys.platform == "win32":
                os.startfile(filepath)
            elif sys.platform == "darwin":
                subprocess.run(["open", filepath])
            else:
                subprocess.run(["xdg-open", filepath])
        except Exception as e:
            messagebox.showerror("Error", f"Could not open file:\n{e}")

    def open_docs_folder(self):
        """Open documentation folder"""

        try:
            if sys.platform == "win32":
                os.startfile(self.docs_dir)
            elif sys.platform == "darwin":
                subprocess.run(["open", self.docs_dir])
            else:
                subprocess.run(["xdg-open", self.docs_dir])
        except Exception as e:
            messagebox.showerror("Error", f"Could not open folder:\n{e}")

    def open_exports_folder(self):
        """Open exports folder"""

        try:
            if sys.platform == "win32":
                os.startfile(self.exports_dir)
            elif sys.platform == "darwin":
                subprocess.run(["open", self.exports_dir])
            else:
                subprocess.run(["xdg-open", self.exports_dir])
        except Exception as e:
            messagebox.showerror("Error", f"Could not open folder:\n{e}")

    def update_status(self, message):
        """Update status bar"""
        self.status_bar.config(text=message)


def main():
    root = tk.Tk()
    app = WorkflowDocumenterGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
