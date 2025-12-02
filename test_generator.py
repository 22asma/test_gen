import subprocess
import json

class TestGenerator:
    def __init__(self, model_name="mistral"):
        self.model_name = model_name
    
    def generate_tests(self, requirements, test_type="gherkin"):
        """
        test_type: 
        "gherkin", "pytest", "api", "data", 
        "owasp", "performance", "e2e"
        """
        try:
            print(f"🚀 Génération de tests ({test_type}) via Ollama…")

            response = self._call_ollama(requirements, test_type)
            cleaned = self._postprocess_output(response)
            return cleaned
        
        except Exception as e:
            print("⚠️ Erreur Ollama → fallback MOCK.")
            print("Erreur :", e)
            return self._generate_mock_tests(test_type)


    def _call_ollama(self, requirements, test_type):

        # =============================
        # INSTRUCTIONS PAR TYPE DE TEST
        # =============================

        if test_type == "gherkin":
            instructions = "Generate detailed Gherkin scenarios."

        elif test_type == "pytest":
            instructions = """
Generate pytest unit tests.
Use assert statements.
Produce fully runnable Python test functions.
"""

        elif test_type == "api":
            instructions = """
Generate API tests in JSON or Postman format.
Include method, URL, body, headers and validation steps.
"""

        elif test_type == "data":
            instructions = """
Generate structured test data.
Include:
- valid data
- invalid data
- boundary values
"""

        elif test_type == "owasp":
            instructions = """
Generate OWASP security test cases.
Include:
- vulnerability type
- malicious payload
- attack description
- expected secure behavior
"""

        elif test_type == "performance":
            instructions = """
Generate Load Testing scripts.
Output must include:

### Locust (Python)
- HttpUser
- tasks()
- constant spawn rate
- load phases

### or JMeter XML snippet
"""

        elif test_type == "e2e":
            instructions = """
Generate End-to-End UI automation scripts.

### 1. Playwright (Python)
Use:
- `sync_playwright()`
- page.goto()
- page.locator().click()
- page.locator().fill()
- expect()

### 2. Selenium (Python)
Use:
- webdriver.Chrome()
- find_element()
- send_keys()
- click()
- assert statements

Scripts must be runnable.
"""

        # =============================
        # PROMPT ENVOYÉ À OLLAMA
        # =============================

        prompt = f"""
You are an AI Test Generation Assistant.

Functional requirement:
{json.dumps(requirements, indent=2)}

Instructions:
{instructions}

Generate high-quality professional test scripts.
"""

        # Appel au modèle Ollama
        result = subprocess.run(
            ["ollama", "run", self.model_name],
            input=prompt.encode("utf-8"),
            capture_output=True
        )

        if result.returncode != 0:
            raise RuntimeError(result.stderr.decode("utf-8"))

        return result.stdout.decode("utf-8")
    

    def _postprocess_output(self, text):
        """Nettoyage simple du texte"""
        return text.strip()


    def _generate_mock_tests(self, test_type):
        """Fallback si Ollama échoue"""

        if test_type == "gherkin":
            return """
Scenario: Mock test
  Given mock input
  When mock action
  Then mock result
"""

        elif test_type == "pytest":
            return """
def test_mock():
    assert True
"""

        elif test_type == "api":
            return """
{
  "name": "Mock API Test",
  "request": {"method": "GET", "url": "/mock"},
  "tests": ["response.status == 200"]
}
"""

        elif test_type == "data":
            return """
{
  "valid": ["mock"],
  "invalid": ["mock"]
}
"""

        elif test_type == "owasp":
            return """
{
  "attack": "SQL Injection",
  "payload": "' OR 1=1 --",
  "expected": "request blocked"
}
"""

        elif test_type == "performance":
            return """
# Mock Locust Script
from locust import HttpUser, task

class MockUser(HttpUser):
    @task
    def test(self):
        self.client.get("/")
"""

        elif test_type == "e2e":
            return """
# MOCK PLAYWRIGHT TEST
from playwright.sync_api import sync_playwright

def test_mock_login():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto("http://localhost/login")
        page.fill("#username", "test")
        page.fill("#password", "pass")
        page.click("#login")
        browser.close()

# MOCK SELENIUM TEST
from selenium import webdriver

def test_mock_e2e():
    driver = webdriver.Chrome()
    driver.get("http://localhost/login")
    driver.find_element("id", "username").send_keys("test")
    driver.find_element("id", "password").send_keys("pass")
    driver.find_element("id", "login").click()
    driver.quit()
"""

# ============================================
# FONCTION IMPORTABLE PAR FLASK → OBLIGATOIRE !
# ============================================

def generate_test_cases(requirements_dict, test_type="gherkin"):
    generator = TestGenerator()
    return generator.generate_tests(requirements_dict, test_type)
