from typing import List
from bs4 import BeautifulSoup
import os
import cloudscraper

from app.dtos.news_dto import NewsDTO


class NewsService:
    BASE_URL = os.getenv("FURIA_DRAFT5_URL", "https://draft5.gg/equipe/330-FURIA")

    def __init__(self):
        self.scraper = cloudscraper.create_scraper()

    def _fetch_page_soup(self) -> BeautifulSoup:
        response = self.scraper.get(self.BASE_URL)
        response.raise_for_status()
        return BeautifulSoup(response.text, "html.parser")

    def get_furia_last_news(self) -> List[NewsDTO]:
        soup = self._fetch_page_soup()
        news_list = []

        # Pega todas as divs que contém as notícias
        news_cards = soup.select("div.Card__CardContainer-sc-122kzjp-0 a.NewsCardSmall__NewsCardSmallContainer-sc-1q3y6t7-0")

        for news in news_cards:
            try:
                title = news.select_one("p.NewsCardSmall__Title-sc-1q3y6t7-1").text.strip()
                href = news.get("href")

                if not href:
                    continue

                # Montar link completo se necessário
                source_link = href if href.startswith("http") else f"https://draft5.gg{href}"

                news_dto = NewsDTO(
                    title=title,
                    source_link=source_link
                )

                news_list.append(news_dto)

            except Exception as e:
                print(f"Error parsing news: {e}")
                continue

        return news_list


