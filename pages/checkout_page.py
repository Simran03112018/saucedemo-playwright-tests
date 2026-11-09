from playwright.sync_api import Page


class CheckoutPage:
    def __init__(self, page: Page) -> None:
        self.page = page
        self.first_name = page.get_by_test_id("firstName")
        self.last_name = page.get_by_test_id("lastName")
        self.postal_code = page.get_by_test_id("postalCode")
        self.continue_button = page.get_by_test_id("continue")
        self.cancel_button = page.get_by_test_id("cancel")
        self.finish_button = page.get_by_test_id("finish")
        self.error = page.get_by_test_id("error")

    def enter_information(self, first_name: str, last_name: str, postal_code: str) -> None:
        self.first_name.fill(first_name)
        self.last_name.fill(last_name)
        self.postal_code.fill(postal_code)

    def continue_checkout(self) -> None:
        self.continue_button.click()

    def item_prices(self) -> list[str]:
        return self.page.get_by_test_id("inventory-item-price").all_text_contents()

    def summary_value(self, test_id: str) -> str:
        return self.page.get_by_test_id(test_id).inner_text()

    def finish(self) -> None:
        self.finish_button.click()
