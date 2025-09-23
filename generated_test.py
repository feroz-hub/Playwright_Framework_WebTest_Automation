import re
from playwright.sync_api import sync_playwright


with sync_playwright() as playwright:
    browser = playwright.chromium.launch(headless=False,slow_mo=600)
    page = browser.new_page()
    page.goto("https://softwaredelivery-stg3.olympusmedical.com")
    page.get_by_role("textbox", name="Email Address").click()
    page.get_by_role("textbox", name="Email Address").fill("48200010.olympusssa.onmicrosoft.com@amer.teams.ms")
    page.get_by_role("textbox", name="Password").click()
    page.get_by_role("textbox", name="Password").fill("9xFXgZQR@kdgj")
    page.get_by_role("button", name="Sign in").click()
    page.get_by_role("button", name="Accept All Cookies").click()



    # ---------------------
