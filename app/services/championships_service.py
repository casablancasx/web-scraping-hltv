import os
from datetime import datetime, date
from typing import List
import cloudscraper
from bs4 import BeautifulSoup

from app.dtos.championships_dto import UpComingChampionshipsDto


class ChampionshipsService:
    BASE_URL = os.getenv("FURIA_HLTV_URL", "https://www.hltv.org/team/8297/furia")

    def __init__(self):
        self.scraper = cloudscraper.create_scraper()

    def _fetch_page_soup(self) -> BeautifulSoup:
        resp = self.scraper.get(self.BASE_URL)
        resp.raise_for_status()
        return BeautifulSoup(resp.text, "html.parser")

    def scrape_upcoming_and_ongoing_championships(self) -> List[UpComingChampionshipsDto]:
        soup = self._fetch_page_soup()
        upcoming_and_ongoing_championships = []

        events_container = soup.find("div", {"class": "sub-tab-content-events", "id": "ongoingEvents"})
        if not events_container:
            return upcoming_and_ongoing_championships

        events_holder = events_container.find("div", class_="upcoming-events-holder")
        if not events_holder:
            return upcoming_and_ongoing_championships

        event_links = events_holder.find_all("a", class_="a-reset")

        for event in event_links:
            try:
                event_name = event.select_one(".eventbox-eventname").text.strip()
                event_img = event.select_one(".eventbox-eventlogo img").get("src")
                event_link = "https://www.hltv.org" + event.get("href")

                date_spans = [span for span in event.select(".eventbox-date span") if span.has_attr('data-unix')]

                if len(date_spans) < 2:
                    print(f"Warning: event '{event_name}' missing start or end date.")
                    continue

                start_unix = int(date_spans[0]["data-unix"]) / 1000
                end_unix = int(date_spans[1]["data-unix"]) / 1000
                start_date_obj = datetime.utcfromtimestamp(start_unix).date()
                end_date_obj = datetime.utcfromtimestamp(end_unix).date()

                today = datetime.utcnow().date()

                if start_date_obj <= today <= end_date_obj:
                    status = "ONGOING"
                else:
                    status = "UPCOMING"

                days_until_event = (start_date_obj - today).days if status == "UPCOMING" else 0

                dto = UpComingChampionshipsDto(
                    days_until_event=max(days_until_event, 0),
                    event_name=event_name,
                    event_img=event_img,
                    event_link=event_link,
                    start_date=start_date_obj,
                    end_date=end_date_obj,
                    status=status
                )

                upcoming_and_ongoing_championships.append(dto)

            except Exception as e:
                print(f"Error parsing event: {e}")
                continue

        return upcoming_and_ongoing_championships
