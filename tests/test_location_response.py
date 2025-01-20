import unittest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time  # Import time module for sleep


class TestLocationResponse(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Setup WebDriver
        service = Service(executable_path='/home/linor/Downloads/chromedriver-linux64/chromedriver')
        cls.driver = webdriver.Chrome(service=service)
        cls.driver.get("http://127.0.0.1:5002")

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()

    def test_invalid_locations(self):
        """Test with multiple invalid locations"""
        invalid_inputs = ["-6", "89", "!@", ""]

        for invalid_input in invalid_inputs:
            with self.subTest(location=invalid_input):
                self._test_location_input(invalid_input, expected_error="invalid location")

    def test_valid_location_and_change(self):
        """Test valid locations and switching locations"""
        driver = self.driver

        # First input: Israel
        self._test_location_input("Israel", expected_text="forecast")

        # Click "Check another location"
        try:
            check_another_location_link = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '/html/body/div/a'))
            )
            check_another_location_link.click()
        except Exception as e:
            self.fail(f"Failed to click 'Check another location' link: {e}")

        # Second input: New York
        self._test_location_input("New York", expected_text="forecast")

    def _test_location_input(self, input_text, expected_error=None, expected_text=None):
        """Reusable method to test location input"""
        driver = self.driver

        try:
            location_input = driver.find_element(By.XPATH, '/html/body/div/form/input')
            submit_button = driver.find_element(By.XPATH, '/html/body/div/form/button')

            location_input.clear()
            location_input.send_keys(input_text)
            submit_button.click()

            if expected_error:
                error_message = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, '/html/body/div/p[1]'))
                )
                self.assertIn(expected_error.lower(), error_message.text.lower())
            elif expected_text:
                weather_info = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, '/html/body'))
                )
                self.assertIn(expected_text.lower(), weather_info.text.lower())

            time.sleep(2)

        except Exception as e:
            print(f"Error during input test for '{input_text}': {e}")


if __name__ == "__main__":
    unittest.main()
