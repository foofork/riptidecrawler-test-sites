"""
PDFs and Binaries Test Site
Port: 5004
Tests binary file handling, PDFs, images, and Content-Type detection
"""
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, Response, FileResponse
from fastapi.templating import Jinja2Templates
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.units import inch
from faker import Faker
import random

app = FastAPI(title="PDFs and Binaries Site")
templates = Jinja2Templates(directory="templates")

fake = Faker()
Faker.seed(42)
random.seed(42)


def generate_pdf(title: str, include_table: bool = False) -> bytes:
    """Generate PDF using ReportLab"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    # Title
    story.append(Paragraph(title, styles['Title']))
    story.append(Spacer(1, 0.2 * inch))

    # Content
    for i in range(3):
        story.append(Paragraph(fake.paragraph(), styles['Normal']))
        story.append(Spacer(1, 0.1 * inch))

    # Add table if requested
    if include_table:
        story.append(Spacer(1, 0.2 * inch))
        story.append(Paragraph("Data Table:", styles['Heading2']))

        data = [['Product', 'Price', 'Stock']]
        for _ in range(5):
            data.append([
                fake.catch_phrase(),
                f"${random.randint(10, 1000)}",
                str(random.randint(0, 100))
            ])

        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))

        story.append(table)

    doc.build(story)
    return buffer.getvalue()


def generate_fake_image() -> bytes:
    """Generate a simple fake image (1x1 PNG)"""
    # Minimal valid PNG (1x1 pixel, red)
    png_data = bytes([
        0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A,  # PNG signature
        0x00, 0x00, 0x00, 0x0D, 0x49, 0x48, 0x44, 0x52,  # IHDR chunk
        0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01,  # 1x1 dimensions
        0x08, 0x02, 0x00, 0x00, 0x00, 0x90, 0x77, 0x53,
        0xDE, 0x00, 0x00, 0x00, 0x0C, 0x49, 0x44, 0x41,
        0x54, 0x08, 0xD7, 0x63, 0xF8, 0xCF, 0xC0, 0x00,  # IDAT chunk (red pixel)
        0x00, 0x03, 0x01, 0x01, 0x00, 0x18, 0xDD, 0x8D,
        0xB4, 0x00, 0x00, 0x00, 0x00, 0x49, 0x45, 0x4E,
        0x44, 0xAE, 0x42, 0x60, 0x82  # IEND chunk
    ])
    return png_data


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "pdfs-and-binaries",
        "port": 5007,
        "uptime": "operational"
    }


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Home page with file type overview"""
    return templates.TemplateResponse("home.html", {
        "request": request,
        "title": "PDFs and Binaries Test Site"
    })


@app.get("/pdf/simple")
async def simple_pdf():
    """Generate simple PDF without tables"""
    pdf_content = generate_pdf("Simple PDF Document", include_table=False)
    return Response(
        content=pdf_content,
        media_type="application/pdf",
        headers={"Content-Disposition": "inline; filename=simple.pdf"}
    )


@app.get("/pdf/with-table")
async def pdf_with_table():
    """Generate PDF with data table"""
    pdf_content = generate_pdf("PDF Document with Table", include_table=True)
    return Response(
        content=pdf_content,
        media_type="application/pdf",
        headers={"Content-Disposition": "inline; filename=table.pdf"}
    )


@app.get("/image/{image_id}")
async def get_image(image_id: int):
    """Return fake image"""
    image_data = generate_fake_image()
    return Response(
        content=image_data,
        media_type="image/png",
        headers={"Content-Disposition": f"inline; filename=image_{image_id}.png"}
    )


@app.get("/video/{video_id}")
async def get_video(video_id: int):
    """Return fake video (minimal MP4 header)"""
    # Minimal valid MP4 header
    mp4_data = bytes([
        0x00, 0x00, 0x00, 0x20, 0x66, 0x74, 0x79, 0x70,  # ftyp box
        0x69, 0x73, 0x6F, 0x6D, 0x00, 0x00, 0x02, 0x00,
        0x69, 0x73, 0x6F, 0x6D, 0x69, 0x73, 0x6F, 0x32,
        0x61, 0x76, 0x63, 0x31, 0x6D, 0x70, 0x34, 0x31
    ])
    return Response(
        content=mp4_data,
        media_type="video/mp4",
        headers={"Content-Disposition": f"inline; filename=video_{video_id}.mp4"}
    )


@app.get("/binary/{file_id}")
async def get_binary(file_id: int):
    """Return generic binary data"""
    binary_data = bytes([random.randint(0, 255) for _ in range(1024)])
    return Response(
        content=binary_data,
        media_type="application/octet-stream",
        headers={"Content-Disposition": f"attachment; filename=file_{file_id}.bin"}
    )


@app.get("/mixed-content", response_class=HTMLResponse)
async def mixed_content(request: Request):
    """Page with mixed HTML and binary links"""
    return templates.TemplateResponse("mixed.html", {
        "request": request
    })


@app.get("/content-types")
async def content_types_info():
    """Return information about available content types"""
    return {
        "html_pages": [
            {"url": "/", "content_type": "text/html"},
            {"url": "/mixed-content", "content_type": "text/html"}
        ],
        "pdfs": [
            {"url": "/pdf/simple", "content_type": "application/pdf"},
            {"url": "/pdf/with-table", "content_type": "application/pdf"}
        ],
        "images": [
            {"url": "/image/1", "content_type": "image/png"},
            {"url": "/image/2", "content_type": "image/png"}
        ],
        "videos": [
            {"url": "/video/1", "content_type": "video/mp4"}
        ],
        "binaries": [
            {"url": "/binary/1", "content_type": "application/octet-stream"}
        ],
        "skip_logic": "Check Content-Type header. Skip if not text/html for HTML parsing."
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5004)
