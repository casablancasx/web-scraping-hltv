from typing import List
from bs4 import BeautifulSoup
from cloudscraper import CloudScraper

from app.dtos.news_dto import NewsDTO
from app.config import Settings


class NewsService:


    def __init__(self, scraper: CloudScraper, settings: Settings):
        self.scraper = scraper
        self.base_url = settings.furia_draft5_url

    def _fetch_page_soup(self) -> BeautifulSoup:
        response = self.scraper.get(self.base_url)
        response.raise_for_status()
        return BeautifulSoup(response.text, "html.parser")

    def get_furia_last_news(self) -> List[NewsDTO]:
        soup = self._fetch_page_soup()
        news_list = []

        news_cards = soup.select("div.Card__CardContainer-sc-122kzjp-0 a.NewsCardSmall__NewsCardSmallContainer-sc-1q3y6t7-0")

        for news in news_cards:
            try:
                title_tag = news.select_one("p.NewsCardSmall__Title-sc-1q3y6t7-1")
                title = title_tag.text.strip() if title_tag else "N/A"

                href = news.get("href")
                if not href:
                    continue

                source_link = href if href.startswith("http") else f"https://draft5.gg{href}"

                news_dto = NewsDTO(
                    title=title,
                    source_link=source_link
                )
                news_list.append(news_dto)

            except AttributeError as e:
                print(f"Error parsing news element: {e} - Element: {news}")
                continue
            except Exception as e:
                print(f"Unexpected error parsing news: {e}")
                continue

        return news_list