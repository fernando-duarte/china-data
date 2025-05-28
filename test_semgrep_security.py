#!/usr/bin/env python3
"""Test file for Semgrep security detection
This file contains intentional security issues to test Semgrep configuration
DO NOT USE IN PRODUCTION - FOR TESTING ONLY
"""

import hashlib
import os
import pickle
import subprocess

import yaml

# Test 1: Hardcoded secrets (should be detected by p/secrets)
API_KEY = "sk-1234567890abcdef1234567890abcdef"  # Fake API key
DATABASE_PASSWORD = "super_secret_password_123"
AWS_ACCESS_KEY = "AKIAIOSFODNN7EXAMPLE"


# Test 2: SQL Injection vulnerability (should be detected by p/security-audit)
def unsafe_sql_query(user_input):
    """Intentionally vulnerable SQL query"""
    query = f"SELECT * FROM users WHERE name = '{user_input}'"
    return query


# Test 3: Command injection (should be detected by p/security-audit)
def unsafe_command_execution(user_input):
    """Intentionally vulnerable command execution"""
    os.system(f"echo {user_input}")
    subprocess.call(f"ls {user_input}", shell=True)


# Test 4: Insecure deserialization (should be detected by p/python)
def unsafe_pickle_load(data):
    """Intentionally vulnerable pickle deserialization"""
    return pickle.loads(data)


# Test 5: Weak cryptographic hash (should be detected by p/security-audit)
def weak_hash(data):
    """Using weak MD5 hash"""
    return hashlib.md5(data.encode()).hexdigest()


# Test 6: YAML unsafe load (should be detected by p/python)
def unsafe_yaml_load(yaml_string):
    """Intentionally vulnerable YAML loading"""
    return yaml.load(yaml_string)


# Test 7: Path traversal vulnerability (should be detected by p/security-audit)
def unsafe_file_access(filename):
    """Intentionally vulnerable file access"""
    with open(f"/var/data/{filename}") as f:
        return f.read()


# Test 8: Insecure random number generation (should be detected by p/python)
import random


def weak_random():
    """Using weak random number generator"""
    return random.random()


# Test 9: Debug mode enabled (should be detected by p/security-audit)
DEBUG = True
if DEBUG:
    print("Debug mode is enabled - security risk!")

# Test 10: Insecure HTTP usage (should be detected by p/security-audit)
import requests


def insecure_request():
    """Making insecure HTTP request"""
    response = requests.get("http://api.example.com/data", verify=False)
    return response.json()


if __name__ == "__main__":
    print("This is a test file for Semgrep security detection")
    print("It contains intentional security vulnerabilities")
    print("DO NOT USE IN PRODUCTION")
