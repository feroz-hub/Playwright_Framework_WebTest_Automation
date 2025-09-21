# file: config/config_manager.py

"""
Enhanced configuration manager for OMSD Automation that loads settings
from environment variables with fallback to YAML configuration.
Handles all user roles and database configurations from your existing setup.
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from dotenv import load_dotenv


@dataclass
class UserCredentials:
    """Data class for user credentials."""
    username: str
    password: str
    role: Optional[str] = None
    description: Optional[str] = None


@dataclass
class DatabaseConfig:
    """Data class for database configuration."""
    server: str
    name: str
    username: str
    password: str


@dataclass
class TestConfig:
    """Data class for test configuration."""
    browser: str
    headless: bool
    implicit_wait: int
    explicit_wait: int
    chrome_driver_path: Optional[str] = None


@dataclass
class TestLoginConfig:
    """Data class for test-specific login configuration."""
    username: str
    password: str
    expected: str = "success"


class ConfigManager:
    """
    Enhanced configuration manager that handles all OMSD automation settings.
    Loads from environment variables with YAML fallbacks.
    """

    # Define all available user roles
    USER_ROLES = [
        "software_uploader",
        "distribution_manager",
        "distribution_manager_without_permission",
        "device_update_executor_without_permission",
        "device_update_executor",
        "customer"
    ]

    def __init__(self, config_file: str = "config/config.yaml", env_file: str = ".env"):
        """
        Initialize the configuration manager.

        Args:
            config_file: Path to YAML configuration file
            env_file: Path to .env file
        """
        self.config_file = Path(config_file)
        self.env_file = Path(env_file)

        # Load environment variables
        self._load_env_variables()

        # Load YAML configuration for non-sensitive data
        self._load_yaml_config()

        # Get current environment
        self.current_env = self._get_current_environment()

    def _load_env_variables(self) -> None:
        """Load environment variables from .env file."""
        if self.env_file.exists():
            load_dotenv(self.env_file)
            print(f"✅ Loaded environment variables from {self.env_file}")
        else:
            print(f"⚠️  Warning: .env file not found at {self.env_file}")
            print("   Environment variables will be loaded from system only.")

    def _load_yaml_config(self) -> None:
        """Load non-sensitive configuration from YAML file."""
        if self.config_file.exists():
            with open(self.config_file, 'r') as file:
                self.yaml_config = yaml.safe_load(file) or {}
            print(f"✅ Loaded YAML configuration from {self.config_file}")
        else:
            print(f"⚠️  Warning: Config file not found at {self.config_file}")
            self.yaml_config = {}

    def _get_current_environment(self) -> str:
        """
        Get current environment from environment variable or YAML config.

        Returns:
            str: Current environment name
        """
        env = os.getenv('APP_ENV', self.yaml_config.get('env', 'staging'))
        print(f"🎯 Current environment: {env}")
        return env

    def get_base_url(self) -> str:
        """
        Get base URL for current environment.

        Returns:
            str: Base URL
        """
        # Priority: Environment variable > YAML environment config > YAML root config
        env_var_name = f"{self.current_env.upper()}_BASE_URL"

        base_url = (
                os.getenv(env_var_name) or
                os.getenv('BASE_URL') or
                self.yaml_config.get('environments', {}).get(self.current_env, {}).get('base_url') or
                self.yaml_config.get('base_url', '')
        )

        if not base_url:
            raise ValueError(f"Base URL not configured for environment: {self.current_env}")

        return base_url

    def get_user_credentials(self, user_role: str) -> UserCredentials:
        """
        Get user credentials for a specified role.

        Args:
            user_role: User role (e.g., 'software_uploader', 'distribution_manager')

        Returns:
            UserCredentials: User credentials object

        Raises:
            ValueError: If a user role is not found
        """
        if user_role not in self.USER_ROLES:
            raise ValueError(f"Invalid user role: {user_role}. Available roles: {self.USER_ROLES}")

        # Try environment variables first (priority order)
        env_patterns = [
            f"{self.current_env.upper()}_{user_role.upper()}_USERNAME",
            f"{user_role.upper()}_USERNAME"
        ]

        username = None
        password = None

        for pattern in env_patterns:
            username = os.getenv(pattern)
            if username:
                # Get corresponding password
                password_pattern = pattern.replace('_USERNAME', '_PASSWORD')
                password = os.getenv(password_pattern)
                break

        # Fallback to YAML if not found in the environment
        if not username or not password:
            yaml_users = (
                self.yaml_config.get('environments', {})
                .get(self.current_env, {})
                .get('users', {})
            )

            if user_role in yaml_users:
                username = username or yaml_users[user_role].get('username')
                password = password or yaml_users[user_role].get('password')

        if not username or not password:
            raise ValueError(
                f"Credentials not found for user role: {user_role} in environment: {self.current_env}.\n"
                f"Please check your .env file or config.yaml for {self.current_env.upper()}_{user_role.upper()}_USERNAME/PASSWORD"
            )

        # Get additional metadata from YAML
        role_info = (
            self.yaml_config.get('environments', {})
            .get(self.current_env, {})
            .get('users', {})
            .get(user_role, {})
        )

        return UserCredentials(
            username=username,
            password=password,
            role=role_info.get('role'),
            description=role_info.get('description')
        )

    def get_all_user_credentials(self) -> Dict[str, UserCredentials]:
        """
        Get all available user credentials for the current environment.

        Returns:
            Dict[str, UserCredentials]: Dictionary of all user credentials
        """
        all_credentials = {}

        for user_role in self.USER_ROLES:
            try:
                all_credentials[user_role] = self.get_user_credentials(user_role)
            except ValueError as e:
                print(f"⚠️  Warning: Could not load credentials for {user_role}: {e}")

        return all_credentials

    def get_database_config(self) -> DatabaseConfig:
        """
        Get database configuration.

        Returns:
            DatabaseConfig: Database configuration object
        """
        server = os.getenv('DB_SERVER') or self.yaml_config.get('db', {}).get('server_fallback', '')
        name = os.getenv('DB_NAME') or self.yaml_config.get('db', {}).get('name_fallback', '')
        username = os.getenv('DB_USERNAME') or self.yaml_config.get('db', {}).get('username', '')
        password = os.getenv('DB_PASSWORD') or self.yaml_config.get('db', {}).get('password', '')

        if not all([server, name, username, password]):
            missing = [k for k, v in
                       {'server': server, 'name': name, 'username': username, 'password': password}.items() if not v]
            raise ValueError(f"Database configuration incomplete. Missing: {missing}")

        return DatabaseConfig(
            server=server,
            name=name,
            username=username,
            password=password
        )

    def get_test_config(self) -> TestConfig:
        """
        Get test configuration.

        Returns:
            TestConfig: Test configuration object
        """
        return TestConfig(
            browser=os.getenv('BROWSER') or self.yaml_config.get('browser', 'chrome'),
            headless=self._get_boolean_env('HEADLESS', self.yaml_config.get('headless', False)),
            implicit_wait=int(os.getenv('IMPLICIT_WAIT', self.yaml_config.get('implicit_wait', 5))),
            explicit_wait=int(os.getenv('EXPLICIT_WAIT', self.yaml_config.get('explicit_wait', 10))),
            chrome_driver_path=os.getenv('CHROME_DRIVER_PATH') or self.yaml_config.get('chrome_driver_path')
        )

    def get_test_login_config(self) -> TestLoginConfig:
        """
        Get test-specific login configuration.

        Returns:
            TestLoginConfig: Test login configuration object
        """
        username = os.getenv('TEST_LOGIN_USERNAME') or self.yaml_config.get('tests', {}).get('login', [{}])[0].get(
            'username', '')
        password = os.getenv('TEST_LOGIN_PASSWORD') or self.yaml_config.get('tests', {}).get('login', [{}])[0].get(
            'password', '')
        expected = self.yaml_config.get('tests', {}).get('login', {}).get('expected', 'success')

        if not username or not password:
            raise ValueError(
                "Test login credentials not configured. Check TEST_LOGIN_USERNAME and TEST_LOGIN_PASSWORD.")

        return TestLoginConfig(
            username=username,
            password=password,
            expected=expected
        )

    def get_upload_file_path(self, file_key: str) -> str:
        """
        Get to upload a file path.

        Args:
            file_key: File key (e.g., 'esg_410')

        Returns:
            str: File path
        """
        env_var = f"UPLOAD_{file_key.upper()}_PATH"
        file_path = (
                os.getenv(env_var) or
                self.yaml_config.get('upload_files', {}).get(file_key, '')
        )

        if not file_path:
            raise ValueError(f"Upload file path not configured for: {file_key}")

        return file_path

    def get_available_user_roles(self) -> List[str]:
        """
        Get list of available user roles for current environment.

        Returns:
            List[str]: List of available user roles
        """
        yaml_roles = (
            self.yaml_config.get('environments', {})
            .get(self.current_env, {})
            .get('user_roles', [])
        )

        return yaml_roles or self.USER_ROLES

    @staticmethod
    def _get_boolean_env(env_var: str, default: bool) -> bool:
        """
        Convert environment variable to boolean.

        Args:
            env_var: Environment variable name
            default: Default value if not set

        Returns:
            bool: Boolean value
        """
        value = os.getenv(env_var, str(default)).lower()
        return value in ('true', '1', 'yes', 'on')

    def validate_configuration(self) -> Dict[str, Any]:
        """
        Validate the current configuration and return the status.

        Returns:
            Dict with validation results
        """
        validation_results = {
            'environment': self.current_env,
            'base_url': None,
            'database': None,
            'users': {},
            'test_config': None,
            'errors': []
        }

        try:
            validation_results['base_url'] = self.get_base_url()
        except ValueError as e:
            validation_results['errors'].append(f"Base URL: {e}")

        try:
            validation_results['database'] = self.get_database_config()
        except ValueError as e:
            validation_results['errors'].append(f"Database: {e}")

        try:
            validation_results['test_config'] = self.get_test_config()
        except Exception as e:
            validation_results['errors'].append(f"Test Config: {e}")

        # Validate user credentials
        for role in self.get_available_user_roles():
            try:
                validation_results['users'][role] = self.get_user_credentials(role)
            except ValueError as e:
                validation_results['errors'].append(f"User {role}: {e}")

        return validation_results

    def print_configuration_summary(self) -> None:
        """Print a summary of the current configuration."""
        print("\n" + "=" * 60)
        print("🔧 OMSD AUTOMATION CONFIGURATION SUMMARY")
        print("=" * 60)

        validation = self.validate_configuration()

        print(f"🎯 Environment: {validation['environment']}")
        print(f"🌐 Base URL: {validation.get('base_url', 'Not configured')}")

        if validation['users']:
            print(f"\n👥 Available Users ({len(validation['users'])}):")
            for role, creds in validation['users'].items():
                print(f"   ✅ {role}: {creds.username}")

        if validation['database']:
            db = validation['database']
            print(f"\n🗄️  Database: {db.name} @ {db.server}")

        if validation['test_config']:
            tc = validation['test_config']
            print(f"\n🧪 Test Config: {tc.browser} | Headless: {tc.headless}")

        if validation['errors']:
            print(f"\n❌ Configuration Errors ({len(validation['errors'])}):")
            for error in validation['errors']:
                print(f"   • {error}")
        else:
            print(f"\n✅ Configuration is valid!")

        print("=" * 60)


# Global configuration instance
config = ConfigManager()


# Convenience functions for easy access
def get_base_url() -> str:
    """Get base URL for the current environment."""
    return config.get_base_url()


def get_user_credentials(user_role: str) -> UserCredentials:
    """Get user credentials for a specified role."""
    return config.get_user_credentials(user_role)


def get_all_user_credentials() -> Dict[str, UserCredentials]:
    """Get all available user credentials."""
    return config.get_all_user_credentials()


def get_database_config() -> DatabaseConfig:
    """Get database configuration."""
    return config.get_database_config()


def get_test_config() -> TestConfig:
    """Get test configuration."""
    return config.get_test_config()


def get_test_login_config() -> TestLoginConfig:
    """Get test login configuration."""
    return config.get_test_login_config()


def get_upload_file_path(file_key: str) -> str:
    """Get to upload a file path."""
    return config.get_upload_file_path(file_key)


def validate_config() -> Dict[str, Any]:
    """Validate current configuration."""
    return config.validate_configuration()


def print_config_summary() -> None:
    """Print configuration summary."""
    config.print_configuration_summary()


# Auto-validation on import (can be disabled by setting SKIP_CONFIG_VALIDATION=true)
if not os.getenv('SKIP_CONFIG_VALIDATION', '').lower() == 'true':
    try:
        validation = validate_config()
        if validation['errors']:
            print("⚠️  Configuration validation found issues. Run print_config_summary() for details.")
    except Exception:
        pass  # Silent fail on import