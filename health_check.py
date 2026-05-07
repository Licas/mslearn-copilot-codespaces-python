#!/usr/bin/env python3
"""
Health check script that pings the /ping endpoint and prints the result.
"""
import requests
import sys

def health_check(url: str = "http://localhost:8000/ping") -> bool:
    """
    Ping the /ping endpoint and return True if healthy, False otherwise.
    
    Args:
        url: The endpoint URL (defaults to localhost:8000/ping)
    
    Returns:
        True if the endpoint returns a successful response, False otherwise.
    """
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        
        print(f"✓ Health check passed")
        print(f"  Status Code: {response.status_code}")
        print(f"  Response: {response.json()}")
        return True
    except requests.exceptions.ConnectionError:
        print(f"✗ Health check failed: Unable to connect to {url}")
        return False
    except requests.exceptions.Timeout:
        print(f"✗ Health check failed: Request timed out")
        return False
    except requests.exceptions.HTTPError:
        print(f"✗ Health check failed: HTTP error {response.status_code}")
        return False
    except Exception as e:
        print(f"✗ Health check failed: {str(e)}")
        return False


if __name__ == "__main__":
    success = health_check()
    sys.exit(0 if success else 1)
