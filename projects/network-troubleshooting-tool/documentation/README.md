# Workflow Documentation System

Complete workflow documentation solution for creating, organizing, and exporting step-by-step process guides with screenshot support.

## Quick Start

### 1. Install Dependencies

```bash
# For workflow recording (screenshot capture)
pip3 install pillow pynput

# For Linux/WSL (required for screenshot capture)
sudo apt-get install python3-tk python3-dev scrot

# For document export (optional but recommended)
sudo apt-get install pandoc texlive-xetex
pip3 install markdown2
```

### 2. Record a Workflow

```bash
cd tools
python3 workflow-recorder.py --name "my-workflow" --department "IT"
```

**Hotkeys during recording:**
- `F9` - Take screenshot and advance step
- `F10` - Add note to current step
- `ESC` - Stop recording and generate documentation

### 3. Edit Documentation

Open the generated Markdown file in your preferred editor:
- **Obsidian:** Copy `workflows/*.md` to your Obsidian vault
- **VSCode:** Open directly with Markdown preview
- **Any text editor:** Edit the `.md` file

### 4. Export to PDF/HTML

```bash
cd tools

# Export single workflow to PDF
python3 export-workflow.py --input ../documentation/workflows/my-workflow.md --format pdf

# Export all workflows
python3 export-workflow.py --input ../documentation/workflows/ --format pdf --batch

# Export to HTML
python3 export-workflow.py --input ../documentation/workflows/my-workflow.md --format html

# Export to all formats
python3 export-workflow.py --input ../documentation/workflows/my-workflow.md --format all
```

## Directory Structure

```
documentation/
├── workflows/              # Markdown documentation files
│   ├── unifi-vlan-setup.md
│   ├── sonicwall-vpn.md
│   └── backup-procedure.md
├── screenshots/            # Organized screenshot folders
│   ├── unifi-vlan-setup/
│   │   ├── step01_*.png
│   │   ├── step02_*.png
│   │   └── ...
│   └── sonicwall-vpn/
│       └── ...
├── templates/              # Workflow templates
│   ├── network-config-template.md
│   ├── troubleshooting-template.md
│   └── client-deliverable-template.md
└── exports/                # Exported PDF/HTML files
    ├── unifi-vlan-setup.pdf
    └── sonicwall-vpn.html
```

## Workflow Documentation Format

Each workflow follows this structure:

```markdown
# [Workflow Name]

**Document Information:**
- Department: [IT/Sales/Support]
- Created: [Date]
- Last Updated: [Date]
- Owner: [Person/Team]
- Related Docs: [Links]

## Overview
Brief description of the workflow

## Prerequisites
What's needed before starting

## Steps

### Step 1: [Action Name]
![Description](../screenshots/workflow-name/step1.png)

**What to do:**
1. Detailed instructions
2. Additional details

**Notes:**
- Important considerations
- Tips and tricks

### Step 2: [Next Action]
...

## Verification
How to confirm success

## Troubleshooting
Common issues and solutions

## Related Resources
Links and references
```

## Integration with Your Tools

### Obsidian

1. **Copy workflows to your Obsidian vault:**
   ```bash
   cp documentation/workflows/*.md ~/path/to/obsidian-vault/Workflows/
   cp -r documentation/screenshots ~/path/to/obsidian-vault/Workflows/
   ```

2. **Use Obsidian features:**
   - Internal links: `[[related-workflow]]`
   - Tags: `#sop #network #unifi`
   - Backlinks for workflow connections
   - Graph view to visualize workflow relationships

3. **Obsidian plugins to install:**
   - **Dataview** - Query and organize workflows
   - **Templater** - Create workflow templates
   - **Excalidraw** - Add diagrams to workflows

### SharePoint

1. **Export to PDF for upload:**
   ```bash
   python3 tools/export-workflow.py --input documentation/workflows/ --format pdf --batch
   ```

2. **Upload to SharePoint:**
   - Go to your SharePoint document library
   - Upload files from `documentation/exports/`
   - Organize in folders by department

3. **Export to Word for collaborative editing:**
   ```bash
   python3 tools/export-workflow.py --input documentation/workflows/my-workflow.md --format docx
   ```

### NotebookLM

1. **Upload Markdown files directly:**
   - Go to NotebookLM
   - Create a new notebook
   - Upload `.md` files from `documentation/workflows/`

2. **Use for training:**
   - Ask NotebookLM questions about your processes
   - Generate summaries for quick reference
   - Create study guides for new team members

## Claude Code Integration

The **workflow-documenter** skill is available in your central skills directory.

### Using the Skill

When working in Claude Code, you can ask:

- "Create a workflow document for UniFi VLAN setup"
- "Document the backup verification process"
- "Generate a client onboarding checklist"
- "Build a troubleshooting guide for VPN issues"

Claude will generate the template structure, and you can:
1. Use the workflow recorder to capture screenshots
2. Edit the generated Markdown file
3. Export to PDF/HTML for distribution

## Example Workflows

### Network Configuration Example

**Command:**
```bash
python3 tools/workflow-recorder.py --name "unifi-vlan-setup" --department "IT"
```

**Process:**
1. Press F9, login to UniFi Controller → enter step title "Login to Controller"
2. Press F9, navigate to Networks → enter step title "Access Network Settings"
3. Press F9, create new VLAN → enter step title "Create Guest VLAN"
4. Press F9, verify configuration → enter step title "Verify VLAN Created"
5. Press ESC to stop and generate documentation

**Result:**
- Markdown file: `documentation/workflows/unifi-vlan-setup.md`
- Screenshots: `documentation/screenshots/unifi-vlan-setup/step*.png`

### Client Deliverable Example

**Command:**
```bash
python3 tools/workflow-recorder.py --name "customer-network-handoff" --department "Sales"
```

**Process:**
1. Capture screenshots of network topology
2. Document configuration details
3. Add verification steps

**Export:**
```bash
python3 tools/export-workflow.py --input documentation/workflows/customer-network-handoff.md --format pdf
```

**Result:** Professional PDF ready to email to customer

## Tips and Best Practices

### Screenshot Tips

1. **Use descriptive filenames**
   - ✅ `step3-create-vlan-interface.png`
   - ❌ `screenshot1.png`

2. **Clean up your screen before capturing**
   - Close unnecessary windows
   - Hide sensitive information
   - Use full-screen mode when possible

3. **Capture the right amount**
   - Not too zoomed in (show context)
   - Not too zoomed out (keep text readable)

### Documentation Tips

1. **Keep workflows focused**
   - One workflow = One specific task
   - Break complex processes into multiple related workflows

2. **Update regularly**
   - Review quarterly or after system changes
   - Add "Last Updated" date
   - Mark deprecated workflows clearly

3. **Link related workflows**
   - Use `[[workflow-name]]` syntax in Obsidian
   - Add "Related Resources" section
   - Create workflow maps for complex processes

4. **Use consistent formatting**
   - Follow the standard template
   - Use the same heading structure
   - Maintain naming conventions

### Organization Tips

1. **Use clear naming conventions:**
   - `device-action-details.md` (e.g., `unifi-vlan-setup.md`)
   - `client-deliverable-type.md` (e.g., `customer-network-handoff.md`)
   - `process-department-action.md` (e.g., `backup-it-verification.md`)

2. **Create workflow categories:**
   ```
   workflows/
   ├── network-configs/
   ├── client-deliverables/
   ├── troubleshooting/
   └── internal-procedures/
   ```

3. **Tag workflows for easy searching:**
   - Add tags in frontmatter (for Obsidian)
   - Use consistent tag names (#network, #vpn, #client)

## Troubleshooting

### Recorder Issues

**Problem: Screenshots not capturing**
```bash
# Linux/WSL - Install required packages
sudo apt-get install python3-tk scrot

# Test screenshot capability
python3 -c "from PIL import ImageGrab; ImageGrab.grab().save('test.png')"
```

**Problem: Hotkeys not working**
```bash
# Ensure pynput is installed correctly
pip3 install --upgrade pynput

# Check permissions (Linux)
# You may need to run with sudo for global hotkeys
```

### Export Issues

**Problem: PDF export fails**
```bash
# Install pandoc and LaTeX
sudo apt-get install pandoc texlive-xetex

# Verify installation
pandoc --version
```

**Problem: Images not showing in PDF**
- Ensure screenshot paths are relative: `../screenshots/workflow-name/step1.png`
- Check that screenshot files exist in the correct location
- Use `--embed-resources` flag with pandoc

### WSL-Specific Issues

**Problem: Cannot capture screenshots in WSL**

WSL doesn't have direct display access. Options:
1. Use Windows-side Python with the recorder
2. Take screenshots manually (Win+Shift+S) and save to screenshots folder
3. Run the recorder on Windows and mount the documentation folder

## Advanced Usage

### Custom Templates

Create custom templates in `documentation/templates/`:

```bash
# Copy existing workflow
cp documentation/workflows/unifi-vlan-setup.md documentation/templates/network-config-template.md

# Edit template, replace specifics with placeholders
# Use template for new workflows
```

### Batch Processing

Process multiple workflows at once:

```bash
# Export all workflows to PDF
python3 tools/export-workflow.py --input documentation/workflows/ --format pdf --batch

# Export specific category
python3 tools/export-workflow.py --input documentation/workflows/network-configs/ --format pdf --batch
```

### Automation

Add to your workflow:

```bash
# Automated daily export to SharePoint folder
#!/bin/bash
cd /home/mavrick/Projects/network-troubleshooting-tool
python3 tools/export-workflow.py \
  --input documentation/workflows/ \
  --format pdf \
  --output /mnt/sharepoint/SOPs/ \
  --batch
```

## Support

For issues or questions:
- Check the workflow-documenter skill documentation
- Review example workflows in `documentation/workflows/`
- Check tool help: `python3 workflow-recorder.py --help`

## Next Steps

1. **Try the recorder:**
   ```bash
   python3 tools/workflow-recorder.py --name "test-workflow" --department "IT"
   ```

2. **Create your first workflow:**
   - Document a process you do regularly
   - Use the recorder to capture steps
   - Export to PDF and share with team

3. **Integrate with your tools:**
   - Copy workflows to Obsidian vault
   - Export PDFs to SharePoint
   - Upload to NotebookLM for AI assistance

4. **Build your library:**
   - Document all common procedures
   - Create department-specific workflows
   - Build client deliverable templates
