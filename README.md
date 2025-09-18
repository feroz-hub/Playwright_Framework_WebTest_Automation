# Playwright Framework WebTest Automation

A Python end-to-end web test automation framework for the Olympus Medical Software Delivery web application, built on Playwright with the Page Object Model (POM) pattern and pytest as the test runner.

This repository aims to provide maintainable page objects, utilities for configuration and logging, and example tests for login and related flows.


## Tech Stack and Tooling
- Language: Python (version not pinned) — TODO: confirm supported Python version (e.g., 3.10+)
- Test Runner: pytest
- Browser Automation: Microsoft Playwright (sync API)
- Pytest Plugin: pytest-playwright
- Config: YAML via PyYAML
- Reporting: allure-pytest (Allure reports) — TODO: install Allure Commandline for report viewing if needed
- Package Manager: pip (requirements listed in requirement.txt)


## Repository Structure
- LICENSE
- README.md
- config.yaml — central configuration (environment, URLs, credentials, test data)
- requirement.txt — Python dependencies for pip install -r requirement.txt
- omsd_automation/
  - pages/
    - base_page.py — common Playwright helpers (click/fill/get text/screenshot/etc.)
    - home_page.py — Home/Dashboard Page Object
    - login_page.py — Login Page Object
  - utils/
    - config_reader.py — loads config.yaml and provides access helpers
    - logger_utils.py — structured logging helper
    - login_utils.py — high-level login helper
    - logout_utils.py — sign-out utility
- tests/
  - test_config.py — shared constants/paths/timeouts for tests
  - test_login.py — parameterized login test flow (example)


## Configuration
The framework is configured through config.yaml at the repo root.

Key settings:
- env: active environment key under environments (e.g., staging, prod)
- environments: per-environment base_url and users credentials
- base_url, browser, headless, waits
- tests.login: credentials/data for parametrized tests

Important notes:
- The current config.yaml contains plaintext credentials and database values intended for testing. For security, move secrets out of version control (e.g., use environment variables, .env files, or a secret manager). TODO: replace credentials with environment-variable lookups and provide a .env.example.
- Switching environments: Edit the env value at the top of config.yaml (e.g., staging → prod). The code reads that value via Config.get_env(). There is currently no environment variable override implemented.


## Requirements
- Python: TODO: confirm exact version. It is recommended to use a modern Python 3 version (e.g., 3.10+).
- Node.js is NOT required to run tests when using pytest-playwright wheels, but Playwright browser binaries must be installed via the Playwright Python package.
- OS: Windows/macOS/Linux supported by Playwright


## Setup
1) Create and activate a virtual environment
- macOS/Linux:
  - python3 -m venv .venv
  - source .venv/bin/activate
- Windows (PowerShell):
  - python -m venv .venv
  - .venv\\Scripts\\Activate.ps1

2) Install Python dependencies
- pip install -r requirement.txt

3) Install Playwright browsers
- playwright install

4) Optional: Allure reporting CLI
- To generate and view Allure reports, you need the Allure commandline tool (separate from the allure-pytest plugin):
  - macOS (brew): brew install allure — TODO: verify
  - Windows: Install via Scoop/Chocolatey or download from Allure releases — TODO: add exact steps for your environment


## Running Tests
- Run the full test suite:
  - pytest
- Run with quiet output:
  - pytest -q
- Run a specific test file:
  - pytest tests/test_login.py -q
- Filter tests by keyword:
  - pytest -k login -q
- Markers: test_config.py defines marker name constants (smoke, integration, regression), but they are not yet used in decorators. TODO: add proper pytest markers and document usage.

Playwright headed/headless mode:
- Default headless/headed comes from config.yaml (headless: false currently). You can also override with pytest-playwright CLI options, e.g.:
  - pytest --headed
  - pytest --browser chromium

Allure report generation (if allure CLI installed):
- Generate results:
  - pytest --alluredir=allure-results
- Serve the report locally:
  - allure serve allure-results


## Test Data and Fixtures
- The example test tests/test_login.py uses pytest-playwright's built-in page fixture.
- It also refers to fixtures/objects like login_page, home_page, base_page, and to logging helpers from omsd_automation.utils.logger (module not present). TODOs:
  - Provide a conftest.py to construct and yield page objects (LoginPage, HomePage, BasePage) and any shared logger instance.
  - Align imports to logger_utils (current file) or add a logger module that matches imports in tests.


## Common Commands
- Install deps: pip install -r requirement.txt
- Install browsers: playwright install
- Run tests: pytest -q
- Update Playwright: pip install -U playwright pytest-playwright && playwright install


## Environment Variables
The current code primarily reads from config.yaml using Config.get(). There is no environment variable override implemented yet.

Recommended TODOs:
- Support ENV selection via an environment variable (e.g., OMSD_ENV=staging) to override config.yaml env.
- Load secrets from environment variables or a .env file (use python-dotenv) instead of committing plaintext credentials.
- Provide a .env.example showcasing expected variables.

Example (future idea):
- OMSD_ENV=prod pytest -q


## Entry Points and Scripts
- Entry point: pytest executes tests under tests/.
- No Makefile or scripts/ directory is present. Use the common commands above.
- IDEs can run pytest directly; CI can invoke pytest with the same commands.


## Known Gaps / TODOs
- Confirm and document supported Python version and OS matrix.
- Replace plaintext credentials in config.yaml with environment-based configuration; check in a sanitized config.example.yaml.
- Add conftest.py with fixtures for page objects (login_page, home_page, base_page) used in tests.
- Fix import inconsistencies in tests (e.g., logger import path, BasePage method names vs. usage) or update page objects to expose the used methods.
- Document Allure CLI installation steps per OS.
- Consider adding a Makefile or task runner for common commands.


## License
This project is licensed under the MIT License. See the LICENSE file for details.
