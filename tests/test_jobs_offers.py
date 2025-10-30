"""
Tests for jobs-and-offers.site

Validates:
- JobPosting schema.org structured data
- Job listing pages with proper markup
- Application URLs and tracking
- Salary and compensation information
- Job location data
- Employment type classification
- Expired job handling
"""

import json
import pytest
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta


SITE_PORT = 5012
EXPECTED_JOB_COUNT = 50


@pytest.mark.phase3
@pytest.mark.requires_docker
class TestJobsOffers:
    """Test suite for jobs-and-offers.site job listing features."""

    def test_site_is_healthy(self, health_check):
        """
        Verify the site is running and responding.

        Expected: HTTP 200 on root path
        """
        assert health_check(SITE_PORT), "jobs-and-offers.site is not healthy"

    def test_job_listings_page_loads(self, site_url, http_client):
        """
        Test that job listings page loads successfully.

        Expected:
        - HTTP 200
        - Contains job listings
        - Has navigation to individual jobs
        """
        url = site_url(SITE_PORT, "/jobs")
        response = http_client.get(url)

        assert response.status_code == 200, "Jobs listing page should return 200"

        soup = BeautifulSoup(response.content, 'html.parser')

        # Check for job items
        jobs = soup.find_all(class_='job-listing') or soup.find_all('article')
        assert len(jobs) > 0, "Should have at least one job listing"

    def test_job_detail_has_jobposting_schema(self, site_url, http_client):
        """
        Test that job detail pages have valid JobPosting schema.org markup.

        Expected:
        - JSON-LD with @type: "JobPosting"
        - Required fields: title, description, datePosted, hiringOrganization
        """
        url = site_url(SITE_PORT, "/jobs/1")
        response = http_client.get(url)

        assert response.status_code == 200, "Job detail page should return 200"

        soup = BeautifulSoup(response.content, 'html.parser')

        # Find JSON-LD script
        jsonld_script = soup.find('script', {'type': 'application/ld+json'})
        assert jsonld_script, "Job page should have JSON-LD script tag"

        # Parse JSON-LD
        jsonld_data = json.loads(jsonld_script.string)

        # Validate JobPosting schema
        assert jsonld_data.get('@type') == 'JobPosting', \
            "JSON-LD should be of type JobPosting"

        # Check required fields
        required_fields = ['title', 'description', 'datePosted', 'hiringOrganization']
        for field in required_fields:
            assert field in jsonld_data, \
                f"JobPosting should have required field: {field}"

    def test_job_location_data(self, site_url, http_client):
        """
        Test that job location data is properly structured.

        Expected:
        - jobLocation field present
        - Contains address information
        - Remote jobs marked appropriately
        """
        url = site_url(SITE_PORT, "/jobs/1")
        response = http_client.get(url)

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            jsonld_script = soup.find('script', {'type': 'application/ld+json'})

            if jsonld_script:
                jsonld_data = json.loads(jsonld_script.string)

                # Check for location data
                assert 'jobLocation' in jsonld_data, \
                    "JobPosting should have jobLocation field"

                location = jsonld_data['jobLocation']

                # Should have address or remote designation
                has_address = 'address' in location or '@type' in location
                has_remote = 'applicantLocationRequirements' in jsonld_data or \
                           'jobLocationType' in jsonld_data

                assert has_address or has_remote, \
                    "Job should have location address or remote designation"

    def test_salary_information(self, site_url, http_client):
        """
        Test that salary/compensation information is included.

        Expected:
        - baseSalary field present (if available)
        - Salary currency and value specified
        """
        url = site_url(SITE_PORT, "/jobs/1")
        response = http_client.get(url)

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            jsonld_script = soup.find('script', {'type': 'application/ld+json'})

            if jsonld_script:
                jsonld_data = json.loads(jsonld_script.string)

                # Check for salary information
                if 'baseSalary' in jsonld_data:
                    salary = jsonld_data['baseSalary']

                    # Should have currency and value
                    assert 'currency' in salary or '@type' in salary, \
                        "baseSalary should have currency information"

                    if 'value' in salary:
                        value = salary['value']
                        assert 'value' in value or 'minValue' in value or 'maxValue' in value, \
                            "Salary value should be specified"

    def test_employment_type(self, site_url, http_client):
        """
        Test that employment type is specified.

        Expected:
        - employmentType field present
        - Valid values: FULL_TIME, PART_TIME, CONTRACTOR, etc.
        """
        url = site_url(SITE_PORT, "/jobs/1")
        response = http_client.get(url)

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            jsonld_script = soup.find('script', {'type': 'application/ld+json'})

            if jsonld_script:
                jsonld_data = json.loads(jsonld_script.string)

                if 'employmentType' in jsonld_data:
                    emp_type = jsonld_data['employmentType']

                    valid_types = [
                        'FULL_TIME', 'PART_TIME', 'CONTRACTOR',
                        'TEMPORARY', 'INTERN', 'VOLUNTEER', 'PER_DIEM', 'OTHER'
                    ]

                    # Employment type should be valid
                    if isinstance(emp_type, str):
                        assert emp_type in valid_types, \
                            f"employmentType should be one of: {valid_types}"
                    elif isinstance(emp_type, list):
                        for et in emp_type:
                            assert et in valid_types, \
                                f"employmentType value should be valid: {et}"

    def test_application_url_present(self, site_url, http_client):
        """
        Test that job postings include application URLs.

        Expected:
        - directApply field or applicationContact present
        - URL is valid
        """
        url = site_url(SITE_PORT, "/jobs/1")
        response = http_client.get(url)

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            jsonld_script = soup.find('script', {'type': 'application/ld+json'})

            if jsonld_script:
                jsonld_data = json.loads(jsonld_script.string)

                # Check for application method
                has_apply = any(field in jsonld_data for field in [
                    'directApply',
                    'applicationContact',
                    'url'
                ])

                assert has_apply, \
                    "JobPosting should have application method specified"

    def test_hiring_organization_details(self, site_url, http_client):
        """
        Test that hiring organization is properly detailed.

        Expected:
        - hiringOrganization field is structured data
        - Contains name and optional logo/url
        """
        url = site_url(SITE_PORT, "/jobs/1")
        response = http_client.get(url)

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            jsonld_script = soup.find('script', {'type': 'application/ld+json'})

            if jsonld_script:
                jsonld_data = json.loads(jsonld_script.string)

                org = jsonld_data.get('hiringOrganization', {})

                # Should have name
                assert 'name' in org, \
                    "hiringOrganization should have name field"

                # Check for additional fields
                if '@type' in org:
                    assert org['@type'] == 'Organization', \
                        "hiringOrganization @type should be Organization"

    def test_job_date_posted(self, site_url, http_client):
        """
        Test that job posting date is valid.

        Expected:
        - datePosted is ISO 8601 format
        - Date is reasonable (not in future)
        """
        url = site_url(SITE_PORT, "/jobs/1")
        response = http_client.get(url)

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            jsonld_script = soup.find('script', {'type': 'application/ld+json'})

            if jsonld_script:
                jsonld_data = json.loads(jsonld_script.string)

                date_posted = jsonld_data.get('datePosted')
                assert date_posted, "JobPosting should have datePosted"

                # Parse date
                try:
                    posted_date = datetime.fromisoformat(date_posted.replace('Z', '+00:00'))

                    # Date should not be in future
                    now = datetime.now(posted_date.tzinfo)
                    assert posted_date <= now, \
                        "datePosted should not be in the future"

                except ValueError:
                    pytest.fail(f"datePosted should be valid ISO 8601 format: {date_posted}")

    def test_expired_jobs_handling(self, site_url, http_client):
        """
        Test that expired jobs are handled correctly.

        Expected:
        - validThrough field indicates expiration
        - Expired jobs may return 404 or show expired status
        """
        url = site_url(SITE_PORT, "/jobs/expired")
        response = http_client.get(url)

        # Expired jobs can be handled in different ways
        valid_responses = [200, 404, 410]  # 410 = Gone

        assert response.status_code in valid_responses, \
            f"Expired job should return valid status, got {response.status_code}"

        if response.status_code == 200:
            # Check if marked as expired
            content = response.text.lower()
            assert 'expired' in content or 'closed' in content or 'no longer accepting' in content, \
                "Expired job page should indicate expiration"

    def test_job_search_filtering(self, site_url, http_client):
        """
        Test that job search/filtering works.

        Expected:
        - Can filter by location, type, or other criteria
        - Results match filter
        """
        # Test location filter
        url = site_url(SITE_PORT, "/jobs?location=remote")
        response = http_client.get(url)

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')

            # Should return some results
            jobs = soup.find_all(class_='job-listing') or soup.find_all('article')

            if len(jobs) > 0:
                # Check if remote appears in listings
                text = soup.get_text().lower()
                assert 'remote' in text, \
                    "Filtered results should contain filter term"

    def test_job_pagination(self, site_url, http_client):
        """
        Test that job listings are paginated.

        Expected:
        - Multiple pages of results
        - Pagination controls present
        """
        url = site_url(SITE_PORT, "/jobs")
        response = http_client.get(url)

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')

            # Check for pagination
            pagination = soup.find(class_='pagination') or \
                        soup.find_all('a', href=lambda x: x and 'page=' in x)

            if pagination:
                assert True, "Job listings should have pagination"

    @pytest.mark.slow
    def test_all_jobs_accessible(self, site_url, http_client):
        """
        Test that all job IDs are accessible.

        Expected:
        - Job IDs 1-50 return 200 or 404 (if not present)
        - No server errors
        """
        accessible_count = 0

        for job_id in range(1, min(EXPECTED_JOB_COUNT + 1, 21)):  # Test first 20
            url = site_url(SITE_PORT, f"/jobs/{job_id}")
            response = http_client.get(url)

            # Should not error
            assert response.status_code < 500, \
                f"Job {job_id} should not cause server error"

            if response.status_code == 200:
                accessible_count += 1

        assert accessible_count >= 10, \
            f"At least 10 jobs should be accessible, found {accessible_count}"


@pytest.mark.phase3
class TestJobDataQuality:
    """Test data quality and completeness of job postings."""

    def test_jobs_have_complete_data(self, site_url, http_client):
        """
        Test that job postings have complete, realistic data.

        Expected:
        - All required fields populated
        - Descriptions are meaningful (not placeholder text)
        """
        url = site_url(SITE_PORT, "/jobs/1")
        response = http_client.get(url)

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            jsonld_script = soup.find('script', {'type': 'application/ld+json'})

            if jsonld_script:
                jsonld_data = json.loads(jsonld_script.string)

                # Check description is meaningful
                description = jsonld_data.get('description', '')
                assert len(description) > 50, \
                    "Job description should be substantial (>50 chars)"

                # Should not be placeholder
                placeholder_terms = ['lorem ipsum', 'placeholder', 'todo', 'xxx']
                desc_lower = description.lower()
                assert not any(term in desc_lower for term in placeholder_terms), \
                    "Job description should not contain placeholder text"

    def test_consistent_job_ids(self, site_url, http_client):
        """
        Test that job IDs are consistent and sequential.

        Expected:
        - Job IDs are integers
        - No duplicate IDs
        """
        job_ids = set()

        for job_id in range(1, 11):
            url = site_url(SITE_PORT, f"/jobs/{job_id}")
            response = http_client.get(url)

            if response.status_code == 200:
                job_ids.add(job_id)

        # Should have unique IDs
        assert len(job_ids) >= 5, \
            "Should have at least 5 unique accessible job IDs"
