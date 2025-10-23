# Pandoc MCP Server

An MCP (Model Context Protocol) server that provides document conversion capabilities using Pandoc with WeasyPrint PDF engine support. Includes customizable fonts, font sizes, and CSS styling.

## Features

- Convert Markdown to PDF with custom fonts and styling
- Convert between many document formats (markdown, docx, html, pdf, etc.)
- Use WeasyPrint as PDF engine (instead of LaTeX)
- Customize fonts, font sizes, margins, and page sizes
- Apply custom CSS for advanced styling
- List all supported input/output formats

## Prerequisites

- Python 3.8+
- Pandoc installed on your system
- WeasyPrint installed on your system
- MCP package

## Installation

### 1. Install System Dependencies

**Pandoc:**
```bash
# macOS
brew install pandoc

# Linux
sudo apt-get install pandoc
```

**WeasyPrint:**
```bash
# macOS
brew install weasyprint

# Linux
sudo apt-get install weasyprint
```

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

Or manually:
```bash
pip install pypandoc mcp
```

### 3. Configure Claude Code

Add the following to your Claude Code MCP settings (`~/.config/claude-code/mcp.json` or project-specific `.claude/mcp.json`):

```json
{
  "mcpServers": {
    "pandoc": {
      "command": "/path/to/your/python",
      "args": ["/path/to/pandoc-mcp/server.py"]
    }
  }
}
```

Replace `/path/to/your/python` with your Python interpreter path and `/path/to/pandoc-mcp/server.py` with the actual path to `server.py`.

For this installation:
```json
{
  "mcpServers": {
    "pandoc": {
      "command": "/Users/ashah/miniforge3/envs/energy311/bin/python",
      "args": ["/Users/ashah/work/pandoc-mcp/server.py"]
    }
  }
}
```

### 4. Restart Claude Code

After updating the MCP configuration, restart Claude Code to load the new server.

## Available Tools

### 1. `convert_md_to_pdf`

Convert Markdown content to PDF with customizable styling.

**Parameters:**
- `markdown_content` (required): The markdown text to convert
- `output_path` (required): Where to save the PDF file
- `css` (optional): Custom CSS for styling
- `font_family` (optional): Font family (default: 'Helvetica')
- `font_size` (optional): Base font size (default: '11pt')
- `page_size` (optional): Page size (default: 'letter')
- `margin` (optional): Page margins (default: '1in')

**Example:**
```python
# Via Claude Code
"Convert this markdown to PDF at ./output.pdf using Arial font at 12pt"
```

### 2. `convert_file`

Convert a file from one format to another.

**Parameters:**
- `input_path` (required): Path to input file
- `output_path` (required): Where to save output file
- `from_format` (optional): Input format (auto-detected if not provided)
- `to_format` (optional): Output format (auto-detected from extension)
- `pdf_engine` (optional): PDF engine to use (default: 'weasyprint')
- `css` (optional): Custom CSS for PDF/HTML output

**Example:**
```python
# Via Claude Code
"Convert document.docx to PDF using weasyprint"
```

### 3. `get_supported_formats`

Get a list of all input and output formats supported by your Pandoc installation.

**Example:**
```python
# Via Claude Code
"What formats does pandoc support?"
```

## Usage Examples

### Example 1: Basic Markdown to PDF

```markdown
# My Document

This is a test document with **bold** and *italic* text.

## Features
- Easy to use
- Customizable fonts
- Professional output
```

Ask Claude Code:
```
"Convert this markdown to PDF at ./my-document.pdf"
```

### Example 2: Custom Font and Size

Ask Claude Code:
```
"Convert this markdown to PDF at ./report.pdf using Times New Roman at 12pt"
```

### Example 3: Custom CSS Styling

Create a custom CSS file:
```css
body {
    font-family: 'Georgia', serif;
    font-size: 13pt;
    color: #2c3e50;
}

h1 {
    color: #3498db;
    border-bottom: 2px solid #3498db;
    padding-bottom: 6pt;
}
```

Ask Claude Code:
```
"Convert this markdown to PDF using my custom CSS file at ./custom-style.css"
```

### Example 4: Convert DOCX to PDF

Ask Claude Code:
```
"Convert my-document.docx to PDF using weasyprint"
```

## Customization

### Default CSS

The server includes a default CSS template (`default-style.css`) with:
- Professional typography
- Code syntax highlighting
- Table styling
- Blockquote formatting
- Page break support

You can modify this file or provide your own CSS when converting.

### Font Options

Common font families you can use:
- **Serif:** 'Times New Roman', 'Georgia', 'Garamond'
- **Sans-serif:** 'Helvetica', 'Arial', 'Verdana'
- **Monospace:** 'Courier New', 'Consolas', 'Monaco'

### Page Sizes

Supported page sizes:
- `letter` (8.5" × 11")
- `a4` (210mm × 297mm)
- `legal` (8.5" × 14")
- `a3`, `a5`, `tabloid`, etc.

### Margins

Specify margins using:
- Inches: `1in`, `0.5in`
- Centimeters: `2cm`, `2.5cm`
- Millimeters: `20mm`, `25mm`

## Troubleshooting

### "Pandoc not found"
Make sure Pandoc is installed and in your PATH:
```bash
which pandoc
pandoc --version
```

### "WeasyPrint not found"
Make sure WeasyPrint is installed and in your PATH:
```bash
which weasyprint
weasyprint --version
```

### Font Issues
If a font isn't rendering correctly, make sure it's installed on your system. WeasyPrint uses system fonts.

### MCP Server Not Loading
1. Check that the Python path in your MCP config is correct
2. Make sure `mcp` and `pypandoc` are installed in that Python environment
3. Check Claude Code logs for error messages

## Technical Details

- **Server:** Python-based MCP server using the `mcp` package
- **Converter:** Uses `pypandoc` wrapper around Pandoc
- **PDF Engine:** WeasyPrint (can be changed to other engines)
- **Communication:** JSON-RPC over stdio

## License

MIT

## Contributing

Feel free to submit issues or pull requests for improvements!
