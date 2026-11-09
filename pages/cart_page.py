from playwright.sync_api import Page


class CartPage:
    def __init__(self, page: Page) -> None:
        self.page = page
        self.items = page.get_by_test_id("inventory-item")
        self.checkout_button = page.get_by_test_id("checkout")
        self.continue_shopping_button = page.get_by_test_id("continue-shopping")

    def item_names(self) -> list[str]:
        return self.page.get_by_test_id("inventory-item-name").all_text_contents()

    def remove_item(self, name: str) -> None:
        item = self.items.filter(has_text=name)
        item.get_by_role("button", name="Remove").click()

    def checkout(self) -> None:
        self.checkout_button.click()

    def continue_shopping(self) -> None:
        self.continue_shopping_button.click()
