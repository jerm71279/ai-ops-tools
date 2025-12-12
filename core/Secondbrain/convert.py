
import sys
import subprocess
import os

def convert_docx_to_html(template_path, docx_path, output_path):
    # Read the template file
    with open(template_path, 'r') as f:
        template_content = f.read()

    # Get the filename without extension for the title
    filename = os.path.basename(docx_path)
    title = os.path.splitext(filename)[0].replace('_', ' ')

    # Convert docx to html using pandoc
    try:
        html_content = subprocess.check_output(['pandoc', '-f', 'docx', '-t', 'html', docx_path], universal_newlines=True)
    except subprocess.CalledProcessError as e:
        print(f"Error processing {docx_path}: {e}")
        return

    # Replace placeholders
    new_html_content = template_content.replace('[Document Title]', title)
    # Be more specific with the content replacement
    new_html_content = new_html_content.replace("""<div class="section-content">
            <p>[Provide a brief overview of the document's purpose and key points. This section should give readers a quick understanding of what to expect.]</p>
        </div>""", f"""<div class="section-content">
            {html_content}
        </div>""")


    # Write the new html content
    with open(output_path, 'w') as f:
        f.write(new_html_content)
    print(f"Created {output_path}")

if __name__ == '__main__':
    if len(sys.argv) != 4:
        print("Usage: python convert.py <template_path> <docx_path> <output_path>")
        sys.exit(1)
    
    template_path = sys.argv[1]
    docx_path = sys.argv[2]
    output_path = sys.argv[3]
    
    convert_docx_to_html(template_path, docx_path, output_path)
