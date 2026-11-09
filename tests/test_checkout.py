import re
from decimal import Decimal

import pytest
from playwright.sync_api import expect

from pages.cart_page import CartPage
from pages.checkout_page import CheckoutPage
from pages.inventory_page import InventoryPage


@pytest.mark.smoke
def test_two_item_checkout_totals_are_consistent(
    inventory_page: InventoryPage,
    cart_page: CartPage,
    checkout_page: CheckoutPage,
) -> None:
    inventory_page.add_item("Sauce Labs Backpack")
    inventory_page.add_item("Sauce Labs Bike Light")
    expect(inventory_page.cart_badge).to_have_text("2")

    inventory_page.open_cart()
    expect(cart_page.items).to_have_count(2)
    assert set(cart_page.item_names()) == {"Sauce Labs Backpack", "Sauce Labs Bike Light"}
    cart_page.checkout()

    checkout_page.enter_information("Ada", "Lovelace", "10001")
    checkout_page.continue_checkout()
    expect(checkout_page.page).to_have_url(re.compile(r".*/checkout-step-two\.html$"))
    expect(checkout_page.page.get_by_test_id("checkout-summary-container")).to_be_visible()

    item_prices = [Decimal(price.removeprefix("$").strip()) for price in checkout_page.item_prices()]
    item_total = Decimal(checkout_page.summary_value("subtotal-label").split("$")[-1])
    tax = Decimal(checkout_page.summary_value("tax-label").split("$")[-1])
    total = Decimal(checkout_page.summary_value("total-label").split("$")[-1])

    assert len(item_prices) == 2
    assert sum(item_prices) == item_total
    assert item_total + tax == total

    checkout_page.finish()
    expect(checkout_page.page.get_by_test_id("complete-header")).to_have_text("Thank you for your order!")


@pytest.mark.regression
@pytest.mark.parametrize(
    ("first_name", "last_name", "postal_code", "expected_error"),
    [
        ("", "Lovelace", "10001", "Error: First Name is required"),
        ("Ada", "", "10001", "Error: Last Name is required"),
        ("Ada", "Lovelace", "", "Error: Postal Code is required"),
    ],
    ids=["missing-first-name", "missing-last-name", "missing-postal-code"],
)
def test_checkout_requires_all_customer_fields(
    inventory_page: InventoryPage,
    cart_page: CartPage,
    checkout_page: CheckoutPage,
    first_name: str,
    last_name: str,
    postal_code: str,
    expected_error: str,
) -> None:
    inventory_page.add_item("Sauce Labs Backpack")
    inventory_page.open_cart()
    cart_page.checkout()
    checkout_page.enter_information(first_name, last_name, postal_code)
    checkout_page.continue_checkout()

    expect(checkout_page.error).to_have_text(expected_error)
    expect(checkout_page.page).to_have_url(re.compile(r".*/checkout-step-one\.html$"))
