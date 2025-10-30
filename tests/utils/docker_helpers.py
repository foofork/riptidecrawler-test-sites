"""Docker and service health check utilities."""

import time
import subprocess
import requests
from typing import List, Dict, Optional


class DockerHealthChecker:
    """Health checker for Docker Compose services."""

    def __init__(self, base_url: str = "http://localhost"):
        """
        Initialize health checker.

        Args:
            base_url: Base URL for services
        """
        self.base_url = base_url
        self.session = requests.Session()

    def check_service(self, port: int, path: str = "/", timeout: int = 5) -> bool:
        """
        Check if a service is healthy.

        Args:
            port: Port number
            path: Health check path
            timeout: Request timeout

        Returns:
            True if healthy
        """
        url = f"{self.base_url}:{port}{path}"

        try:
            response = self.session.get(url, timeout=timeout)
            return response.status_code == 200
        except Exception:
            return False

    def check_all_services(self, service_ports: Dict[str, int], max_retries: int = 30) -> Dict:
        """
        Check all services with retries.

        Args:
            service_ports: Dict of service_name -> port
            max_retries: Maximum retry attempts

        Returns:
            Dict of service_name -> is_healthy
        """
        results = {name: False for name in service_ports}

        for attempt in range(max_retries):
            all_healthy = True

            for name, port in service_ports.items():
                if not results[name]:  # Skip already healthy services
                    is_healthy = self.check_service(port)
                    results[name] = is_healthy

                    if not is_healthy:
                        all_healthy = False

            if all_healthy:
                print(f"✅ All services healthy (attempt {attempt + 1})")
                return results

            time.sleep(2)

        print(f"⚠️  Some services not healthy after {max_retries} attempts")
        return results

    def wait_for_service(self, port: int, timeout: int = 60) -> bool:
        """
        Wait for a single service to be healthy.

        Args:
            port: Port number
            timeout: Maximum wait time

        Returns:
            True if service became healthy
        """
        start_time = time.time()

        while time.time() - start_time < timeout:
            if self.check_service(port):
                return True
            time.sleep(2)

        return False


def wait_for_services(service_ports: Dict[str, int], timeout: int = 60) -> bool:
    """
    Wait for all services to be healthy.

    Args:
        service_ports: Dict of service_name -> port
        timeout: Maximum wait time

    Returns:
        True if all services became healthy
    """
    checker = DockerHealthChecker()
    results = checker.check_all_services(service_ports, max_retries=timeout // 2)
    return all(results.values())


def get_docker_services() -> List[str]:
    """
    Get list of running Docker Compose services.

    Returns:
        List of service names
    """
    try:
        result = subprocess.run(
            ["docker-compose", "ps", "--services"],
            capture_output=True,
            text=True,
            check=True
        )
        return [line.strip() for line in result.stdout.split('\n') if line.strip()]
    except subprocess.CalledProcessError:
        return []


def start_docker_services(services: Optional[List[str]] = None) -> bool:
    """
    Start Docker Compose services.

    Args:
        services: Specific services to start (None = all)

    Returns:
        True if successful
    """
    cmd = ["docker-compose", "up", "-d"]

    if services:
        cmd.extend(services)

    try:
        subprocess.run(cmd, check=True, capture_output=True)
        return True
    except subprocess.CalledProcessError:
        return False


def stop_docker_services(services: Optional[List[str]] = None) -> bool:
    """
    Stop Docker Compose services.

    Args:
        services: Specific services to stop (None = all)

    Returns:
        True if successful
    """
    cmd = ["docker-compose", "down"]

    if services:
        cmd.extend(services)

    try:
        subprocess.run(cmd, check=True, capture_output=True)
        return True
    except subprocess.CalledProcessError:
        return False
