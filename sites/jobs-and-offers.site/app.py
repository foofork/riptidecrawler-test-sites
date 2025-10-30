"""
jobs-and-offers.site - Job Postings Site (Phase 3)
Port: 5012

Features:
- 50 job postings with JobPosting JSON-LD schema
- 30% clean HTML (CSS selectors work)
- 70% messy HTML (need LLM extraction)
- Tracks extraction method per job
"""

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from faker import Faker
import json
from typing import List, Dict
from datetime import datetime, timedelta
import random

app = FastAPI(title="Jobs & Offers")
templates = Jinja2Templates(directory="templates")

# Initialize Faker with seed for reproducibility
fake = Faker()
Faker.seed(42)
random.seed(42)

# Job categories and companies
JOB_CATEGORIES = [
    "Software Engineer", "Data Scientist", "Product Manager", "UX Designer",
    "DevOps Engineer", "Security Analyst", "Marketing Manager", "Sales Representative",
    "Business Analyst", "QA Engineer", "Full Stack Developer", "Mobile Developer",
    "Cloud Architect", "Database Administrator", "Technical Writer", "Project Manager",
    "Customer Success Manager", "HR Manager", "Financial Analyst", "Operations Manager"
]

COMPANIES = [
    "TechCorp", "DataFlow Inc", "CloudScale", "SecureNet", "InnovateLabs",
    "DigitalFirst", "AIVentures", "CodeCraft", "SystemsPlus", "WebDynamics",
    "AppSolutions", "NetworkPro", "CyberShield", "DataMasters", "CloudNine",
    "TechGenius", "SoftwarePlus", "DevTeam", "ProductHQ", "DesignStudio"
]

EMPLOYMENT_TYPES = ["FULL_TIME", "PART_TIME", "CONTRACT", "TEMPORARY", "INTERN"]

def generate_job_data() -> List[Dict]:
    """Generate 50 job postings with mixed HTML quality."""
    jobs = []

    for i in range(50):
        job_id = i + 1
        is_clean_html = i < 15  # First 15 jobs (30%) have clean HTML

        posted_date = fake.date_between(start_date='-60d', end_date='today')
        valid_through = posted_date + timedelta(days=random.randint(30, 90))

        job = {
            'id': job_id,
            'title': random.choice(JOB_CATEGORIES),
            'company': random.choice(COMPANIES),
            'location': f"{fake.city()}, {fake.state_abbr()}",
            'employment_type': random.choice(EMPLOYMENT_TYPES),
            'date_posted': posted_date.isoformat(),
            'valid_through': valid_through.isoformat(),
            'salary_min': random.randint(50, 150) * 1000,
            'salary_max': random.randint(150, 250) * 1000,
            'description': fake.paragraph(nb_sentences=5),
            'requirements': [fake.sentence() for _ in range(random.randint(3, 7))],
            'benefits': [fake.sentence() for _ in range(random.randint(2, 5))],
            'is_clean_html': is_clean_html,
            'extraction_method': 'css_selector' if is_clean_html else 'llm_required'
        }
        jobs.append(job)

    return jobs

# Generate jobs once at startup
JOBS = generate_job_data()

def create_job_jsonld(job: Dict) -> str:
    """Create JobPosting JSON-LD schema."""
    jsonld = {
        "@context": "https://schema.org",
        "@type": "JobPosting",
        "title": job['title'],
        "hiringOrganization": {
            "@type": "Organization",
            "name": job['company']
        },
        "jobLocation": {
            "@type": "Place",
            "address": {
                "@type": "PostalAddress",
                "addressLocality": job['location']
            }
        },
        "datePosted": job['date_posted'],
        "validThrough": job['valid_through'],
        "employmentType": job['employment_type'],
        "baseSalary": {
            "@type": "MonetaryAmount",
            "currency": "USD",
            "value": {
                "@type": "QuantitativeValue",
                "minValue": job['salary_min'],
                "maxValue": job['salary_max'],
                "unitText": "YEAR"
            }
        },
        "description": job['description']
    }
    return json.dumps(jsonld, indent=2)

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Homepage with list of all job postings."""
    return templates.TemplateResponse("index.html", {
        "request": request,
        "jobs": JOBS,
        "total_jobs": len(JOBS),
        "clean_html_count": sum(1 for j in JOBS if j['is_clean_html']),
        "messy_html_count": sum(1 for j in JOBS if not j['is_clean_html'])
    })

@app.get("/job/{job_id}", response_class=HTMLResponse)
async def job_detail(request: Request, job_id: int):
    """Individual job posting page with JSON-LD."""
    job = next((j for j in JOBS if j['id'] == job_id), None)
    if not job:
        return HTMLResponse("<h1>Job not found</h1>", status_code=404)

    jsonld = create_job_jsonld(job)

    # Choose template based on HTML quality
    template = "job_clean.html" if job['is_clean_html'] else "job_messy.html"

    return templates.TemplateResponse(template, {
        "request": request,
        "job": job,
        "jsonld": jsonld
    })

@app.get("/api/jobs")
async def api_jobs():
    """JSON API endpoint for all jobs."""
    return {
        "total": len(JOBS),
        "clean_html_count": sum(1 for j in JOBS if j['is_clean_html']),
        "messy_html_count": sum(1 for j in JOBS if not j['is_clean_html']),
        "jobs": JOBS
    }

@app.get("/api/job/{job_id}")
async def api_job(job_id: int):
    """JSON API endpoint for single job."""
    job = next((j for j in JOBS if j['id'] == job_id), None)
    if not job:
        return {"error": "Job not found"}, 404
    return job

@app.get("/jobs", response_class=HTMLResponse)
async def jobs_listing(request: Request):
    """Job listings page (alias for home page) - tests expect this"""
    return await home(request)

@app.get("/jobs/{job_id}", response_class=HTMLResponse)
async def jobs_detail(request: Request, job_id: int):
    """Job detail page (alias for /job/{id}) - tests expect this"""
    return await job_detail(request, job_id)

@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "jobs-and-offers.site",
        "port": 5012,
        "total_jobs": len(JOBS),
        "clean_html": sum(1 for j in JOBS if j['is_clean_html']),
        "messy_html": sum(1 for j in JOBS if not j['is_clean_html'])
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5012)
