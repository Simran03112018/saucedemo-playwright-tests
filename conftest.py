"""Shared Playwright configuration, authenticated state, and page-object fixtures."""

import os
from pathlib import Path

import pytest
from playwright.sync_api import Browser, Page, Playwright

from pages.cart_page import CartPage
from pages.checkout_page import CheckoutPage
from pages.inventory_page import InventoryPage
from pages.login_page import LoginPage


@pytest.hookimpl(tryfirst=True)
def pytest_sessionstart(session: pytest.Session) -> None:
    """Create output directories before fixtures or reporters write artifacts."""
    Path("reports").mkdir(exist_ok=True)
    Path("test-results").mkdir(exist_ok=True)


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--username",
        action="store",
        default=os.getenv("SAUCE_USERNAME", "standard_user"),
        help="Sauce Demo username (defaults to SAUCE_USERNAME or standard_user).",
    )
    parser.addoption(
        "--password",
        action="store",
        default=os.getenv("SAUCE_PASSWORD", "secret_sauce"),
        help="Sauce Demo password (defaults to SAUCE_PASSWORD or secret_sauce).",
    )
    parser.addoption(
        "--locked-out-username",
        action="store",
        default=os.getenv("SAUCE_LOCKED_OUT_USERNAME", "locked_out_user"),
        help="Sauce Demo locked-out username used by the login validation test.",
    )


@pytest.fixture(scope="session")
def auth_state(
    browser: Browser, playwright: Playwright, request: pytest.FixtureRequest, worker_id: str
) -> str:
    """Log in once and persist browser storage for all non-login test contexts."""
    playwright.selectors.set_test_id_attribute("data-test")
    base_url = request.config.getoption("--base-url") or request.config.getini("base_url")
    username = request.config.getoption("--username")
    password = request.config.getoption("--password")
    state_path = Path(f"test-results/.auth/{worker_id}-storage_state.json")
    state_path.parent.mkdir(parents=True, exist_ok=True)

    context = browser.new_context(base_url=base_url)
    page = context.new_page()
    page.goto("/")
    page.get_by_test_id("username").fill(username)
    page.get_by_test_id("password").fill(password)
    page.get_by_test_id("login-button").click()
    page.get_by_test_id("inventory-container").wait_for(state="visible")
    context.storage_state(path=str(state_path))
    context.close()
    return str(state_path)


@pytest.fixture
def browser_context_args(
    browser_context_args: dict, request: pytest.FixtureRequest, auth_state: str
) -> dict:
    """Use the one-time authenticated state unless a test exercises login."""
    context_args = dict(browser_context_args)
    context_args["base_url"] = (
        request.config.getoption("--base-url") or request.config.getini("base_url")
    )
    if request.node.get_closest_marker("no_auth") is None:
        context_args["storage_state"] = auth_state
    return context_args


@pytest.fixture
def login_page(page: Page) -> LoginPage:
    return LoginPage(page)


@pytest.fixture(scope="session")
def sauce_username(request: pytest.FixtureRequest) -> str:
    return request.config.getoption("--username")


@pytest.fixture(scope="session")
def sauce_password(request: pytest.FixtureRequest) -> str:
    return request.config.getoption("--password")


@pytest.fixture(scope="session")
def locked_out_username(request: pytest.FixtureRequest) -> str:
    return request.config.getoption("--locked-out-username")


@pytest.fixture
def inventory_page(page: Page) -> InventoryPage:
    page.goto("/inventory.html")
    return InventoryPage(page)


@pytest.fixture
def cart_page(page: Page) -> CartPage:
    return CartPage(page)


@pytest.fixture
def checkout_page(page: Page) -> CheckoutPage:
    return CheckoutPage(page)
