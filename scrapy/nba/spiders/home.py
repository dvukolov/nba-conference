import scrapy
from scrapy.http import Request
from nba.items import HomeItem


class HomeSpider(scrapy.Spider):
    name = "home"
    allowed_domains = ["basketball-reference.com"]
    start_urls = ["http://basketball-reference.com/"]
    custom_settings = {
        # exported fields and order
        "FEED_EXPORT_FIELDS": ["season", "team", "home_arena"]
    }

    def start_requests(self):
        seasons = range(2001, 2020)
        urls = [
            f"https://www.basketball-reference.com/leagues/NBA_{season}.html"
            for season in seasons
        ]
        return [Request(url=url) for url in urls]

    def parse(self, response):
        xp = "//th[@data-stat='team_name']/a/@href"
        urls = response.xpath(xp).extract()
        yield from [
            Request(url=response.urljoin(url), callback=self.parse_team) for url in urls
        ]

    def parse_team(self, response):
        season_xp = "//h1[@itemprop='name']/span[1]/text()"
        team_xp = "//h1[@itemprop='name']/span[2]/text()"
        home_xp = (
            "//div[@data-template='Partials/Teams/Summary']/p"
            "/strong[contains(text(),'Arena:')]/following-sibling::text()[1]"
        )
        season = response.xpath(season_xp).extract()
        team = response.xpath(team_xp).extract()
        home_arena = response.xpath(home_xp).extract_first().strip()

        record = {"season": season, "team": team, "home_arena": home_arena}

        yield HomeItem(record)
