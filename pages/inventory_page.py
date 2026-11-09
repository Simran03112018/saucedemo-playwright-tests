import re

from playwright.sync_api import Locator, Page


class InventoryPage:
    def __init__(self, page: Page) -> None:
        self.page = page
        self.inventory = page.get_by_test_id("inventory-container")
        self.sort_select = page.get_by_test_id("product-sort-container")
        self.cart_link = page.get_by_test_id("shopping-cart-link")
        self.cart_badge = page.get_by_test_id("shopping-cart-badge")
        self.items = page.get_by_test_id("inventory-item")

    def add_item(self, name: str) -> None:
        self._item(name).get_by_role("button", name="Add to cart").click()

    def remove_item(self, name: str) -> None:
        self._item(name).get_by_role("button", name="Remove").click()

    def item_button(self, name: str) -> Locator:
        return self._item(name).get_by_role("button", name=re.compile(r"^(Add to cart|Remove)$"))

    def sort_by(self, value: str) -> None:
        self.sort_select.select_option(value)

    def product_names(self) -> list[str]:
        return self.page.get_by_test_id("inventory-item-name").all_text_contents()

    def product_prices(self) -> list[str]:
        return self.page.get_by_test_id("inventory-item-price").all_text_contents()

    def open_cart(self) -> None:
        self.cart_link.click()

    def _item(self, name: str) -> Locator:
        return self.items.filter(has_text=name)
