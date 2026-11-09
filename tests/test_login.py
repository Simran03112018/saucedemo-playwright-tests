import re

import pytest
from playwright.sync_api import expect

from pages.login_page import LoginPage


@pytest.mark.smoke
@pytest.mark.no_auth
def test_valid_user_lands_on_inventory(
    login_page: LoginPage, sauce_username: str, sauce_password: str
) -> None:
    login_page.open()
    login_page.login(sauce_username, sauce_password)

    expect(login_page.page).to_have_url(re.compile(r".*/inventory\.html$"))
    expect(login_page.page.get_by_test_id("inventory-container")).to_be_visible()


@pytest.mark.regression
@pytest.mark.no_auth
@pytest.mark.parametrize(
    ("missing_field", "expected_error"),
    [
        ("username", "Epic sadface: Username is required"),
        ("password", "Epic sadface: Password is required"),
    ],
    ids=["missing-username", "missing-password"],
)
def test_login_rejects_invalid_input(
    login_page: LoginPage,
    sauce_username: str,
    sauce_password: str,
    missing_field: str,
    expected_error: str,
) -> None:
    login_page.open()
    username = "" if missing_field == "username" else sauce_username
    password = "" if missing_field == "password" else sauce_password
    login_page.login(username, password)

    expect(login_page.error).to_have_text(expected_error)
    expect(login_page.page).not_to_have_url(re.compile(r".*/inventory\.html$"))


@pytest.mark.regression
@pytest.mark.no_auth
def test_locked_out_user_sees_error(
    login_page: LoginPage, locked_out_username: str, sauce_password: str
) -> None:
    login_page.open()
    login_page.login(locked_out_username, sauce_password)

    expect(login_page.error).to_have_text(
        "Epic sadface: Sorry, this user has been locked out."
    )
