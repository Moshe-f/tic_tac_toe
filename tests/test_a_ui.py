# All test with (page: Page) need the server to run manually first!
# Need to run `pip install pytest-playwright` first.
# And run `playwright install` in the terminal/cmd.

from playwright.sync_api import Page, expect


def test_against_computer_ui(client, page: Page):
    response = client.get("/against_computer/easy")
    assert response.status_code == 200
    page.goto("http://127.0.0.1:5000/against_computer/easy")

    expect(page.locator("div.main-container")).to_be_visible()
    expect(page.locator("#button0")).to_be_visible()
    expect(page.get_by_text("computer_easy")).to_be_visible()
    
    page.goto("http://127.0.0.1:5000/against_computer/medium")

    expect(page.locator("#sing-1")).to_be_visible()
    expect(page.locator("#restart")).to_be_visible()
    expect(page.get_by_text("computer_medium")).to_be_visible()
    
    page.goto("http://127.0.0.1:5000/against_computer/impossible")

    expect(page.locator("#turn")).to_be_visible()
    expect(page.locator("#button3")).to_be_visible()
    expect(page.get_by_text("computer_impossible")).to_be_visible()


def test_move_ui(client, page: Page):
    response = client.get("/against_computer/impossible")
    assert response.status_code == 200
    page.goto("http://127.0.0.1:5000/against_computer/impossible")
    page.locator("#button4").click()

    expect(page.locator("#button4")).to_have_text("X")
    page.locator("#button6").click()

    expect(page.locator("#button6")).to_have_text("X")
    page.locator("#restart").click()
