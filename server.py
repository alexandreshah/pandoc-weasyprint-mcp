#!/usr/bin/env python3
"""
MCP Server for Pandoc with WeasyPrint support.
Provides document conversion tools with customizable fonts and styling.
"""

import asyncio
import json
import os
import tempfile
from typing import Any, Optional
import pypandoc
from mcp.server import Server
from mcp.types import Tool, TextContent
from mcp.server.stdio import stdio_server


# Initialize the MCP server
app = Server("pandoc-mcp")


# Default CSS template for PDF styling
DEFAULT_CSS = """
@page {
    size: letter;
    margin: 1in;
}

body {
    font-family: 'Helvetica', 'Arial', sans-serif;
    font-size: 11pt;
    line-height: 1.6;
    color: #333;
}

h1 {
    font-size: 24pt;
    font-weight: bold;
    margin-top: 24pt;
    margin-bottom: 12pt;
}

h2 {
    font-size: 18pt;
    font-weight: bold;
    margin-top: 18pt;
    margin-bottom: 9pt;
}

h3 {
    font-size: 14pt;
    font-weight: bold;
    margin-top: 14pt;
    margin-bottom: 7pt;
}

p {
    margin-bottom: 12pt;
}

code {
    font-family: 'Courier New', monospace;
    font-size: 10pt;
    background-color: #f4f4f4;
    padding: 2px 4px;
}

pre {
    font-family: 'Courier New', monospace;
    font-size: 9pt;
    background-color: #f4f4f4;
    padding: 12pt;
    border-radius: 4px;
    overflow-x: auto;
}

blockquote {
    border-left: 4px solid #ddd;
    padding-left: 12pt;
    margin-left: 0;
    font-style: italic;
}

table {
    border-collapse: collapse;
    width: 100%;
    margin: 12pt 0;
}

th, td {
    border: 1px solid #ddd;
    padding: 8pt;
    text-align: left;
}

th {
    background-color: #f4f4f4;
    font-weight: bold;
}
"""


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available pandoc conversion tools."""
    return [
        Tool(
            name="convert_md_to_pdf",
            description="Convert Markdown to PDF using pandoc with weasyprint engine. Supports custom fonts, font sizes, and CSS styling.",
            inputSchema={
                "type": "object",
                "properties": {
                    "markdown_content": {
                        "type": "string",
                        "description": "The markdown content to convert"
                    },
                    "output_path": {
                        "type": "string",
                        "description": "Path where the PDF should be saved"
                    },
                    "css": {
                        "type": "string",
                        "description": "Optional custom CSS for styling. If not provided, uses default styling."
                    },
                    "font_family": {
                        "type": "string",
                        "description": "Font family (e.g., 'Helvetica', 'Times New Roman', 'Arial'). Default: 'Helvetica'"
                    },
                    "font_size": {
                        "type": "string",
                        "description": "Base font size (e.g., '11pt', '12pt', '14pt'). Default: '11pt'"
                    },
                    "page_size": {
                        "type": "string",
                        "description": "Page size (e.g., 'letter', 'a4', 'legal'). Default: 'letter'"
                    },
                    "margin": {
                        "type": "string",
                        "description": "Page margins (e.g., '1in', '2cm', '20mm'). Default: '1in'"
                    }
                },
                "required": ["markdown_content", "output_path"]
            }
        ),
        Tool(
            name="convert_file",
            description="Convert a file from one format to another using pandoc. Supports many formats including markdown, docx, html, pdf, etc.",
            inputSchema={
                "type": "object",
                "properties": {
                    "input_path": {
                        "type": "string",
                        "description": "Path to the input file"
                    },
                    "output_path": {
                        "type": "string",
                        "description": "Path where the output file should be saved"
                    },
                    "from_format": {
                        "type": "string",
                        "description": "Input format (e.g., 'markdown', 'docx', 'html'). Auto-detected if not provided."
                    },
                    "to_format": {
                        "type": "string",
                        "description": "Output format (e.g., 'pdf', 'docx', 'html'). Auto-detected from output_path extension if not provided."
                    },
                    "pdf_engine": {
                        "type": "string",
                        "description": "PDF engine to use when converting to PDF (e.g., 'weasyprint', 'pdflatex'). Default: 'weasyprint'"
                    },
                    "css": {
                        "type": "string",
                        "description": "Optional custom CSS for PDF/HTML output."
                    }
                },
                "required": ["input_path", "output_path"]
            }
        ),
        Tool(
            name="get_supported_formats",
            description="Get list of input and output formats supported by pandoc.",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool execution requests."""

    if name == "convert_md_to_pdf":
        return await convert_md_to_pdf(arguments)
    elif name == "convert_file":
        return await convert_file(arguments)
    elif name == "get_supported_formats":
        return await get_supported_formats()
    else:
        return [TextContent(type="text", text=f"Unknown tool: {name}")]


async def convert_md_to_pdf(args: dict) -> list[TextContent]:
    """Convert markdown content to PDF with custom styling."""
    try:
        markdown_content = args["markdown_content"]
        output_path = args["output_path"]

        # Get optional parameters
        font_family = args.get("font_family", "Helvetica")
        font_size = args.get("font_size", "11pt")
        page_size = args.get("page_size", "letter")
        margin = args.get("margin", "1in")

        # Build CSS
        if "css" in args and args["css"]:
            css_content = args["css"]
        else:
            # Use default CSS with customizations
            css_content = DEFAULT_CSS.replace("font-family: 'Helvetica', 'Arial', sans-serif;",
                                             f"font-family: '{font_family}', 'Arial', sans-serif;")
            css_content = css_content.replace("font-size: 11pt;", f"font-size: {font_size};")
            css_content = css_content.replace("size: letter;", f"size: {page_size};")
            css_content = css_content.replace("margin: 1in;", f"margin: {margin};")

        # Create temporary CSS file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.css', delete=False) as css_file:
            css_file.write(css_content)
            css_path = css_file.name

        try:
            # Convert using pypandoc
            pypandoc.convert_text(
                markdown_content,
                'pdf',
                format='markdown',
                outputfile=output_path,
                extra_args=[
                    '--pdf-engine=weasyprint',
                    f'--css={css_path}'
                ]
            )

            return [TextContent(
                type="text",
                text=f"✓ Successfully converted markdown to PDF: {output_path}\n\nSettings:\n- Font: {font_family}\n- Font size: {font_size}\n- Page size: {page_size}\n- Margins: {margin}"
            )]
        finally:
            # Clean up temporary CSS file
            if os.path.exists(css_path):
                os.unlink(css_path)

    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Error converting markdown to PDF: {str(e)}"
        )]


async def convert_file(args: dict) -> list[TextContent]:
    """Convert a file from one format to another."""
    try:
        input_path = args["input_path"]
        output_path = args["output_path"]
        from_format = args.get("from_format")
        to_format = args.get("to_format")
        pdf_engine = args.get("pdf_engine", "weasyprint")
        css = args.get("css")

        # Check if input file exists
        if not os.path.exists(input_path):
            return [TextContent(
                type="text",
                text=f"Error: Input file not found: {input_path}"
            )]

        # Build extra arguments
        extra_args = []

        # Add PDF engine if converting to PDF
        if to_format == "pdf" or (not to_format and output_path.endswith('.pdf')):
            extra_args.append(f'--pdf-engine={pdf_engine}')

        # Add CSS if provided
        if css:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.css', delete=False) as css_file:
                css_file.write(css)
                css_path = css_file.name
            extra_args.append(f'--css={css_path}')
        else:
            css_path = None

        try:
            # Convert using pypandoc
            pypandoc.convert_file(
                input_path,
                to_format if to_format else None,
                format=from_format,
                outputfile=output_path,
                extra_args=extra_args if extra_args else None
            )

            return [TextContent(
                type="text",
                text=f"✓ Successfully converted {input_path} to {output_path}"
            )]
        finally:
            # Clean up temporary CSS file
            if css_path and os.path.exists(css_path):
                os.unlink(css_path)

    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Error converting file: {str(e)}"
        )]


async def get_supported_formats() -> list[TextContent]:
    """Get list of supported input and output formats."""
    try:
        # Get pandoc version and formats
        version = pypandoc.get_pandoc_version()
        formats = pypandoc.get_pandoc_formats()

        result = f"Pandoc Version: {version}\n\n"
        result += "Input Formats:\n"
        result += ", ".join(sorted(formats[0]))
        result += "\n\nOutput Formats:\n"
        result += ", ".join(sorted(formats[1]))

        return [TextContent(type="text", text=result)]

    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Error getting supported formats: {str(e)}"
        )]


async def main():
    """Run the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
