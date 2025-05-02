
from datetime import datetime, timezone
from typing import List
from cloudscraper import CloudScraper
from bs4 import BeautifulSoup

from app.dtos.championships_dto import ChampionshipsDTO
from app.config import Settings


class ChampionshipsService:

    def __init__(self, scraper: CloudScraper, settings: Settings):
        self.scraper = scraper
        self.base_url = settings.furia_hltv_url

    def _fetch_page_soup(self) -> BeautifulSoup:
        resp = self.scraper.get(self.base_url)
        resp.raise_for_status()
        return BeautifulSoup(resp.text, "html.parser")

    def scrape_upcoming_and_ongoing_championships(self) -> List[ChampionshipsDTO]:
        soup = self._fetch_page_soup()
        upcoming_and_ongoing_championships = []

        events_container = soup.find("div", {"class": "sub-tab-content-events", "id": "ongoingEvents"})
        if not events_container:

            events_container = soup.find("div", {"class": "sub-tab-content-events", "id": "upcomingEvents"})
            if not events_container:
                 print("Warning: Could not find ongoing or upcoming events container.")
                 return upcoming_and_ongoing_championships

        events_holder = events_container.find("div", class_="upcoming-events-holder")
        if not events_holder:
            print("Warning: Could not find events holder within the container.")
            return upcoming_and_ongoing_championships

        event_links = events_holder.find_all("a", class_="a-reset")

        for event in event_links:
            try:
                event_name_tag = event.select_one(".eventbox-eventname")
                event_name = event_name_tag.text.strip() if event_name_tag else "N/A"

                event_img_tag = event.select_one(".eventbox-eventlogo img")
                event_img_src = event_img_tag.get("src") if event_img_tag else ""
                if event_img_src and event_img_src.startswith('/'):
                    event_img = f"https://www.hltv.org{event_img_src}"
                else:
                    event_img = event_img_src

                event_href = event.get("href")
                event_link = f"https://www.hltv.org{event_href}" if event_href else ""

                date_spans = event.select(".eventbox-date span[data-unix]")

                if len(date_spans) < 2:
                    print(f"Warning: Event '{event_name}' missing start or end date spans.")
                    continue


                try:
                    start_unix = int(date_spans[0]["data-unix"]) / 1000
                    end_unix = int(date_spans[1]["data-unix"]) / 1000

                    start_date_obj = datetime.fromtimestamp(start_unix, tz=timezone.utc).date()
                    end_date_obj = datetime.fromtimestamp(end_unix, tz=timezone.utc).date()
                except (ValueError, KeyError, IndexError):
                    print(f"Warning: Could not parse dates for event '{event_name}'.")
                    continue

                today = datetime.now(timezone.utc).date()

                if start_date_obj <= today <= end_date_obj:
                    status = "ONGOING"
                elif start_date_obj > today:
                    status = "UPCOMING"
                else:
                    status = "PAST"
                    continue

                days_until_event = (start_date_obj - today).days if status == "UPCOMING" else 0

                dto = ChampionshipsDTO(
                    days_until_event=max(days_until_event, 0),
                    event_name=event_name,
                    event_img=event_img,
                    event_link=event_link,
                    start_date=start_date_obj,
                    end_date=end_date_obj,
                    status=status
                )
                upcoming_and_ongoing_championships.append(dto)

            except AttributeError as e:
                print(f"Error parsing event element attribute: {e} - Element: {event}")
                continue
            except Exception as e:
                print(f"Unexpected error parsing event: {e}")
                continue


        upcoming_and_ongoing_championships.sort(key=lambda x: (x.status != "ONGOING", x.start_date))

        return upcoming_and_ongoing_championships