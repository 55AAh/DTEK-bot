from dataclasses import dataclass
import logging
from playwright.sync_api import sync_playwright
import re
import json


@dataclass(frozen=True)
class DisconData:
    group: str
    today: dict[str, str]
    tomorrow: dict[str, str]


class DtekApi:
    @classmethod
    def get_shutdowns(cls, street: str, house: str) -> DisconData:
        logger = logging.getLogger("DTEK")

        with sync_playwright() as p:
            logger.info("Launching browser...")
            browser = p.chromium.launch(headless=False)

            logger.info("Fetching index page...")
            page = browser.new_page()
            response = page.goto("https://www.dtek-kem.com.ua/ua/shutdowns")
            page.wait_for_load_state("networkidle")
            assert response is not None
            assert response.status == 200

            # Get page HTML
            index_html = page.content()

            # Extract CSRF token from HTML
            csrf_token = re.findall(
                r'<meta name="csrf-token" content="(.*)">', index_html
            )[0]

            logger.info(f"Requesting houses for street '{street}' ...")
            api_street_response = page.request.post(
                "https://www.dtek-kem.com.ua/ua/ajax",
                multipart={
                    "method": "getHomeNum",
                    "data[0][name]": "street",
                    "data[0][value]": street,
                },
                headers={
                    "X-CSRF-Token": csrf_token,
                },
            )
            assert api_street_response.status == 200
            street_data_json = api_street_response.json()
            logger.info("Street data received.")

        # Find out the house group
        street_data = street_data_json["data"]
        house_data = street_data[house]
        house_group = house_data["sub_type_reason"][0]

        # Extract schedules
        scripts = re.findall(
            r"<script>(DisconSchedule.*)<\/script>", index_html, re.DOTALL
        )[0]
        scripts_fact_text = re.findall(r"DisconSchedule.fact = ({.*})", scripts)[0]
        fact_data = json.loads(scripts_fact_text)["data"]
        days_unix = sorted(map(int, fact_data.keys()))
        fact_day1 = fact_data[str(days_unix[0])][house_group]
        fact_day2 = fact_data[str(days_unix[1])][house_group]

        return DisconData(
            group=house_group,
            today=fact_day1,
            tomorrow=fact_day2,
        )
