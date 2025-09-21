# file: conftest.py

"""
Pytest configuration file containing fixtures and test setup/teardown logic.
Enhanced with ConfigManager integration for seamless configuration management.
"""

import os
import sys
import pytest
from pathlib import Path
from datetime import datetime
from typing import Generator, Dict, Any

from playwright.sync_api import Browser, BrowserContext, Page, Playwright, sync_playwright

# Ensure the project root is on sys.path for package imports
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Import our configuration system
from config.config_manager import (
    ConfigManager,
    get_base_url,
    get_user_credentials,
    get_all_user_credentials,
    get_test_config,
    get_database_config,
    print_config_summary,
    validate_config
)

# Configuration constants
SCREENSHOTS_DIR = Path(__file__).parent / "screenshots"
VIDEOS_DIR = Path(__file__).parent / "videos"
TEST_DATA_DIR = Path(__file__).parent / "test_data"


def pytest_addoption(parser):
    """Add custom command-line options for pytest.
    Only define options that are not provided by common plugins to avoid conflicts.
    """
    parser.addoption(
        "--env",
        action="store",
        help="Environment to run tests against (staging/prod)"
    )
    parser.addoption(
        "--validate-config",
        action="store_true",
        default=False,
        help="Validate configuration and exit"
    )


@pytest.fixture(scope="session", autouse=True)
def config_manager(request) -> ConfigManager:
    """
    Session-scoped fixture providing ConfigManager instance.
    Automatically validates configuration on startup.
    """
    # Override environment if specified via command line
    try:
        cmd_env = request.config.getoption("--env")
        if cmd_env:
            os.environ['APP_ENV'] = cmd_env
    except (ValueError, AttributeError):
        # Handle case where --env is not provided or not available
        pass

    # Create ConfigManager instance
    config = ConfigManager()

    # Validate configuration
    validation = validate_config()
    if validation['errors']:
        print("\n❌ Configuration validation failed:")
        for error in validation['errors']:
            print(f"   • {error}")
        print("\nRun with --validate-config for detailed analysis")
        pytest.exit("Configuration validation failed", returncode=1)

    print(f"✅ Configuration validated successfully for environment: {config.current_env}")
    return config


@pytest.fixture(scope="session")
def test_config_enhanced(request, config_manager: ConfigManager) -> Dict[str, Any]:
    """
    Enhanced session-scoped fixture providing comprehensive test configuration.
    Combines ConfigManager settings with command line overrides.

    Returns:
        Dict containing all test configuration options
    """
    # Get base configuration from ConfigManager
    base_config = config_manager.get_test_config()

    # Apply command line overrides with safe defaults
    try:
        cmd_browser = request.config.getoption("--browser")
    except (ValueError, AttributeError):
        cmd_browser = None

    try:
        cmd_headless = request.config.getoption("--headless")
    except (ValueError, AttributeError):
        cmd_headless = False

    try:
        cmd_base_url = request.config.getoption("--base-url")
    except (ValueError, AttributeError):
        cmd_base_url = None

    # Browser mapping for Playwright
    browser_mapping = {
        "chrome": "chromium",
        "chromium": "chromium",
        "firefox": "firefox",
        "webkit": "webkit",
        "safari": "webkit",
        "edge": "chromium"
    }

    browser_name = browser_mapping.get(cmd_browser or base_config.browser, "chromium")

    return {
        "browser_name": browser_name,
        "headless": cmd_headless or base_config.headless,
        "slowmo": request.config.getoption("--slowmo"),
        "video": request.config.getoption("--video"),
        "tracing": request.config.getoption("--tracing"),
        "base_url": cmd_base_url or config_manager.get_base_url(),
        "implicit_wait": base_config.implicit_wait * 1000,  # Convert to milliseconds
        "explicit_wait": base_config.explicit_wait * 1000,
        "chrome_driver_path": base_config.chrome_driver_path,
        "environment": config_manager.current_env
    }


@pytest.fixture(scope="session")
def browser_type_launch_args(test_config_enhanced: Dict[str, Any]) -> Dict[str, Any]:
    """
    Session-scoped fixture providing browser launch arguments from config.

    Args:
        test_config_enhanced: Enhanced test configuration

    Returns:
        Dict containing browser launch arguments
    """
    args = []

    # Browser-specific arguments
    if test_config_enhanced["browser_name"] == "chromium":
        args.extend([
            "--disable-web-security",
            "--disable-features=VizDisplayCompositor",
            "--no-sandbox",
            "--disable-dev-shm-usage",
            "--disable-gpu"
        ])

    return {
        "headless": test_config_enhanced["headless"],
        "slow_mo": test_config_enhanced["slowmo"],
        "args": args
    }


@pytest.fixture(scope="session")
def playwright_instance() -> Generator[Playwright, None, None]:
    """Session-scoped fixture providing Playwright instance."""
    with sync_playwright() as p:
        yield p


@pytest.fixture(scope="session")
def browser(
        playwright_instance: Playwright,
        test_config_enhanced: Dict[str, Any],
        browser_type_launch_args: Dict[str, Any]
) -> Generator[Browser, None, None]:
    """
    Session-scoped fixture providing browser instance with ConfigManager settings.

    Args:
        playwright_instance: Playwright instance
        test_config_enhanced: Enhanced test configuration from ConfigManager
        browser_type_launch_args: Browser launch arguments

    Yields:
        Browser instance
    """
    browser_type = getattr(playwright_instance, test_config_enhanced["browser_name"])
    browser_instance = browser_type.launch(**browser_type_launch_args)

    print(f"🌐 Browser launched: {test_config_enhanced['browser_name']} "
          f"(headless: {test_config_enhanced['headless']})")

    yield browser_instance
    browser_instance.close()


@pytest.fixture(scope="function")
def browser_context(
        browser: Browser,
        test_config_enhanced: Dict[str, Any]
) -> Generator[BrowserContext, None, None]:
    """
    Function-scoped fixture providing browser context with ConfigManager settings.

    Args:
        browser: Browser instance
        test_config_enhanced: Enhanced test configuration

    Yields:
        BrowserContext instance
    """
    # Setup directories
    SCREENSHOTS_DIR.mkdir(exist_ok=True)
    VIDEOS_DIR.mkdir(exist_ok=True)

    # Context options based on configuration
    context_options = {
        "viewport": {"width": 1920, "height": 1080},
        "ignore_https_errors": True,
        "java_script_enabled": True,
        "accept_downloads": True,
    }

    # Add video recording if enabled
    if test_config_enhanced["video"]:
        context_options["record_video_dir"] = str(VIDEOS_DIR)
        context_options["record_video_size"] = {"width": 1920, "height": 1080}

    # Create context
    context = browser.new_context(**context_options)

    # Set timeouts from configuration
    context.set_default_timeout(test_config_enhanced["explicit_wait"])
    context.set_default_navigation_timeout(test_config_enhanced["explicit_wait"])

    # Enable tracing if requested
    if test_config_enhanced["tracing"]:
        context.tracing.start(screenshots=True, snapshots=True, sources=True)

    yield context

    # Cleanup
    if test_config_enhanced["tracing"]:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        trace_path = SCREENSHOTS_DIR / f"trace-{test_config_enhanced['environment']}-{timestamp}.zip"
        context.tracing.stop(path=str(trace_path))

    context.close()


@pytest.fixture(scope="function")
def page(browser_context: BrowserContext) -> Generator[Page, None, None]:
    """
    Function-scoped fixture providing page instance.

    Args:
        browser_context: Browser context

    Yields:
        Page instance
    """
    page_instance = browser_context.new_page()
    yield page_instance
    page_instance.close()


# =============================================================================
# CONFIGURATION-BASED FIXTURES
# =============================================================================

@pytest.fixture(scope="session")
def base_url(config_manager: ConfigManager, test_config_enhanced: Dict[str, Any]) -> str:
    """
    Session-scoped fixture providing base URL from ConfigManager.

    Returns:
        Base URL string for current environment
    """
    return test_config_enhanced["base_url"]


@pytest.fixture(scope="session")
def current_environment(config_manager: ConfigManager) -> str:
    """Session-scoped fixture providing current environment name."""
    return config_manager.current_env


@pytest.fixture(scope="session")
def database_config(config_manager: ConfigManager):
    """Session-scoped fixture providing database configuration."""
    try:
        return config_manager.get_database_config()
    except ValueError:
        pytest.skip("Database configuration not available")


# =============================================================================
# USER CREDENTIAL FIXTURES
# =============================================================================

@pytest.fixture(scope="session")
def all_user_credentials(config_manager: ConfigManager) -> Dict[str, Any]:
    """
    Session-scoped fixture providing all available user credentials.

    Returns:
        Dictionary containing all user credentials for current environment
    """
    return config_manager.get_all_user_credentials()


@pytest.fixture(scope="function")
def software_uploader_credentials(all_user_credentials):
    """Function-scoped fixture providing software uploader credentials."""
    role = "software_uploader"
    if role not in all_user_credentials:
        pytest.skip(f"Credentials for {role} not configured in current environment")
    creds = all_user_credentials[role]
    return {"username": creds.username, "password": creds.password}


@pytest.fixture(scope="function")
def distribution_manager_credentials(all_user_credentials):
    """Function-scoped fixture providing distribution manager credentials."""
    role = "distribution_manager"
    if role not in all_user_credentials:
        pytest.skip(f"Credentials for {role} not configured in current environment")
    creds = all_user_credentials[role]
    return {"username": creds.username, "password": creds.password}


@pytest.fixture(scope="function")
def distribution_manager_without_permission_credentials(all_user_credentials):
    """Function-scoped fixture providing distribution manager without permission credentials."""
    role = "distribution_manager_without_permission"
    if role not in all_user_credentials:
        pytest.skip(f"Credentials for {role} not configured in current environment")
    creds = all_user_credentials[role]
    return {"username": creds.username, "password": creds.password}


@pytest.fixture(scope="function")
def device_update_executor_credentials(all_user_credentials):
    """Function-scoped fixture providing device update executor credentials."""
    role = "device_update_executor"
    if role not in all_user_credentials:
        pytest.skip(f"Credentials for {role} not configured in current environment")
    creds = all_user_credentials[role]
    return {"username": creds.username, "password": creds.password}


@pytest.fixture(scope="function")
def device_update_executor_without_permission_credentials(all_user_credentials):
    """Function-scoped fixture providing device update executor without permission credentials."""
    role = "device_update_executor_without_permission"
    if role not in all_user_credentials:
        pytest.skip(f"Credentials for {role} not configured in current environment")
    creds = all_user_credentials[role]
    return {"username": creds.username, "password": creds.password}


@pytest.fixture(scope="function")
def customer_credentials(all_user_credentials):
    """Function-scoped fixture providing customer credentials."""
    role = "customer"
    if role not in all_user_credentials:
        pytest.skip(f"Credentials for {role} not configured in current environment")
    creds = all_user_credentials[role]
    return {"username": creds.username, "password": creds.password}


@pytest.fixture(scope="function")
def valid_user_credentials(software_uploader_credentials):
    """Function-scoped fixture providing default valid user credentials."""
    return software_uploader_credentials


@pytest.fixture(scope="function")
def invalid_user_credentials():
    """Function-scoped fixture providing invalid user credentials for negative testing."""
    return {
        "username": "invalid@olympus.com",
        "password": "wrongpassword123"
    }


# =============================================================================
# PAGE OBJECT FIXTURES
# =============================================================================

@pytest.fixture(scope="function")
def login_page(page: Page):
    """Function-scoped fixture providing LoginPage instance."""
    from omsd_automation.pages.login_page import LoginPage
    return LoginPage(page)


@pytest.fixture(scope="function")
def home_page(page: Page):
    """Function-scoped fixture providing HomePage instance."""
    from omsd_automation.pages.home_page import HomePage
    return HomePage(page)


# =============================================================================
# ACTION LAYER FIXTURES
# =============================================================================

@pytest.fixture(scope="function")
def login_actions(login_page, base_url):
    """Function-scoped fixture providing LoginActions instance pre-navigated to base URL."""
    from omsd_automation.actions.login_actions import LoginActions
    actions = LoginActions(login_page, base_url=base_url)
    # Ensure we are on the login page before performing actions
    try:
        actions.open_login_page(base_url)
    except Exception:
        # Ignore navigation errors here; actual login will surface issues
        pass
    return actions


@pytest.fixture(scope="function")
def home_actions(home_page):
    """Function-scoped fixture providing HomeActions instance."""
    from omsd_automation.actions.home_actions import HomeActions
    return HomeActions(home_page)


# =============================================================================
# UTILITY FIXTURES
# =============================================================================

@pytest.fixture(scope="function")
def screenshot_on_failure(request, page: Page, current_environment: str):
    """
    Function-scoped fixture that automatically takes screenshots on test failure.

    Args:
        request: Pytest request object
        page: Page instance
        current_environment: Current environment name
    """
    yield

    if hasattr(request.node, 'rep_call') and request.node.rep_call.failed:
        # Ensure screenshots directory exists
        SCREENSHOTS_DIR.mkdir(exist_ok=True)

        # Generate screenshot filename with environment context
        test_name = request.node.name
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        screenshot_path = SCREENSHOTS_DIR / f"failure_{current_environment}_{test_name}_{timestamp}.png"

        # Take screenshot
        try:
            page.screenshot(path=str(screenshot_path), full_page=True)
            print(f"\n📸 Screenshot saved: {screenshot_path}")
        except Exception as e:
            print(f"\n❌ Failed to take screenshot: {e}")


@pytest.fixture(scope="function")
def test_data_paths() -> Dict[str, Path]:
    """Function-scoped fixture providing test data paths."""
    TEST_DATA_DIR.mkdir(exist_ok=True)
    return {
        "base": TEST_DATA_DIR,
        "uploads": TEST_DATA_DIR / "uploads",
        "downloads": TEST_DATA_DIR / "downloads",
        "templates": TEST_DATA_DIR / "templates"
    }


# =============================================================================
# PYTEST HOOKS
# =============================================================================

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    Pytest hook to make test results available to fixtures.
    This enables the screenshot_on_failure fixture to work.
    """
    outcome = yield
    rep = outcome.get_result()
    setattr(item, "rep_" + rep.when, rep)


def pytest_configure(config):
    """Called after command line options have been parsed."""

    # Handle configuration validation request
    try:
        if config.getoption("--validate-config"):
            print_config_summary()
            pytest.exit("Configuration validation completed", returncode=0)
    except (ValueError, AttributeError):
        # Option not provided or not available
        pass

    # Create necessary directories
    for directory in [SCREENSHOTS_DIR, VIDEOS_DIR, TEST_DATA_DIR]:
        directory.mkdir(exist_ok=True)


def pytest_sessionstart(session):
    """Called after the Session object has been created."""
    print("\n" + "=" * 80)
    print("🚀 OMSD AUTOMATION TEST SUITE - STARTING")
    print("=" * 80)

    # Print configuration summary
    try:
        config = ConfigManager()
        print(f"🎯 Environment: {config.current_env}")
        print(f"🌐 Base URL: {config.get_base_url()}")
        print(f"👥 Available Users: {len(config.get_all_user_credentials())}")

        # Print browser info if available
        test_config = config.get_test_config()
        print(f"🌐 Browser: {test_config.browser} (Headless: {test_config.headless})")

    except Exception as e:
        print(f"⚠️  Could not load configuration summary: {e}")


def pytest_sessionfinish(session, exitstatus):
    """Called after the whole test run finished."""
    print("\n" + "=" * 80)
    print("🏁 OMSD AUTOMATION TEST SUITE - COMPLETED")
    print(f"📊 Exit Status: {exitstatus}")

    # Print summary of generated artifacts
    screenshot_count = len(list(SCREENSHOTS_DIR.glob("*.png"))) if SCREENSHOTS_DIR.exists() else 0
    video_count = len(list(VIDEOS_DIR.glob("*.webm"))) if VIDEOS_DIR.exists() else 0

    if screenshot_count > 0:
        print(f"📸 Screenshots captured: {screenshot_count}")
    if video_count > 0:
        print(f"🎥 Videos recorded: {video_count}")

    print("=" * 80)