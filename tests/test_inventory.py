from decimal import Decimal

import pytest
from playwright.sync_api import expect

from pages.cart_page import CartPage
from pages.inventory_page import InventoryPage


@pytest.mark.regression
@pytest.mark.parametrize(
    ("sort_value", "expected_order"),
    [
        ("lohi", "ascending-price"),
        ("za", "descending-name"),
    ],
    ids=["price-low-to-high", "name-z-to-a"],
)
def test_sorting_changes_displayed_order(
    inventory_page: InventoryPage, sort_value: str, expected_order: str
) -> None:
    inventory_page.sort_by(sort_value)

    if expected_order == "ascending-price":
        prices = [Decimal(price.replace("$", "")) for price in inventory_page.product_prices()]
        assert prices == sorted(prices)
    else:
        names = inventory_page.product_names()
        assert names == sorted(names, reverse=True)


@pytest.mark.regression
def test_removed_cart_item_updates_inventory_button_and_badge(
    inventory_page: InventoryPage, cart_page: CartPage
) -> None:
    item = "Sauce Labs Backpack"
    inventory_page.add_item(item)
    inventory_page.add_item("Sauce Labs Bike Light")
    expect(inventory_page.cart_badge).to_have_text("2")

    inventory_page.open_cart()
    cart_page.remove_item(item)
    expect(inventory_page.page.get_by_test_id("shopping-cart-badge")).to_have_text("1")
    expect(cart_page.items).to_have_count(1)

    cart_page.continue_shopping()
    expect(inventory_page.item_button(item)).to_have_text("Add to cart")
    expect(inventory_page.cart_badge).to_have_text("1")
