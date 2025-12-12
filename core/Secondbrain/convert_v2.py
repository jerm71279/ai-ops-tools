
import sys
import subprocess
import os
from bs4 import BeautifulSoup

def convert_docx_to_html(template_path, docx_path, output_path):
    # Read the template file
    with open(template_path, 'r') as f:
        template_content = f.read()

    # Get the filename without extension for the title
    filename = os.path.basename(docx_path)
    title = os.path.splitext(filename)[0].replace('_', ' ')

    # Convert docx to html using pandoc
    try:
        pandoc_html = subprocess.check_output(['pandoc', '-f', 'docx', '-t', 'html', '--extract-media=.', docx_path], universal_newlines=True)
    except subprocess.CalledProcessError as e:
        print(f"Error processing {docx_path} with pandoc: {e}")
        return

    # Parse the pandoc output and the template
    soup_pandoc = BeautifulSoup(pandoc_html, 'html.parser')
    soup_template = BeautifulSoup(template_content, 'html.parser')

    # --- New Logic to split content ---
    summary_content = ""
    details_content = ""

    first_h1 = soup_pandoc.find('h1')

    if first_h1:
        # Summary is the first h1 and its subsequent siblings until the next h1
        summary_nodes = [first_h1]
        for sibling in first_h1.find_next_siblings():
            if sibling.name == 'h1':
                # This is where the details start
                details_content = str(sibling) + ''.join(str(s) for s in sibling.find_next_siblings())
                break
            summary_nodes.append(sibling)
        else: # No more h1 tags found
            details_content = "" # All content was part of the summary block

        summary_content = ''.join(str(node) for node in summary_nodes)

        # If details_content is empty because there was only one H1, put the summary in details
        # and leave the executive summary with a placeholder. This is more likely for SOPs.
        if not details_content.strip():
             details_content = summary_content
             summary_content = "<p>[No executive summary section found in document.]</p>"

    else:
        # No h1 tags found, put everything in details
        details_content = pandoc_html
        summary_content = "<p>[No executive summary section found in document.]</p>"


    # --- Replace placeholders in the template ---

    # Title
    title_tag = soup_template.find('div', class_='doc-title')
    if title_tag:
        title_tag.string = title

    # Executive Summary
    summary_section = soup_template.find('div', class_='section-title', string='Executive Summary')
    if summary_section:
        content_div = summary_section.find_next_sibling('div', class_='section-content')
        if content_div:
            content_div.clear()
            content_div.append(BeautifulSoup(summary_content, 'html.parser'))

    # Details
    details_section = soup_template.find('div', class_='section-title', string='Details')
    if details_section:
        content_div = details_section.find_next_sibling('div', class_='section-content')
        if content_div:
            # We replace the placeholder <p> tag inside this div
            placeholder_p = content_div.find('p')
            if placeholder_p and '[Main content goes here' in placeholder_p.text:
                placeholder_p.replace_with(BeautifulSoup(details_content, 'html.parser'))


    # Write the new html content
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(str(soup_template))
    print(f"Successfully created structured file: {output_path}")

if __name__ == '__main__':
    if len(sys.argv) != 4:
        print("Usage: python convert.py <template_path> <docx_path> <output_path>")
        sys.exit(1)

    template_path = sys.argv[1]
    docx_path = sys.argv[2]
    output_path = sys.argv[3]

    convert_docx_to_html(template_path, docx_path, output_path)
