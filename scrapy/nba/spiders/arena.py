# -*- coding: utf-8 -*-
import logging
import dateutil.parser
import scrapy
from scrapy.http import Request
from nba.items import ArenaItem


class ArenaSpider(scrapy.Spider):
    name = "arena"
    allowed_domains = ["basketball-reference.com"]
    start_urls = ["http://basketball-reference.com/"]
    custom_settings = {
        # exported fields and order
        "FEED_EXPORT_FIELDS": ["date", "time", "road_team", "home_team", "arena"]
    }

    def start_requests(self):
        seasons = range(2001, 2020)
        urls = [
            f"https://www.basketball-reference.com/leagues/NBA_{season}_games.html"
            for season in seasons
        ]
        return [Request(url=url) for url in urls]

    def parse(self, response):
        # Go to each month page
        xp = "//div[@class='filter']/div/a/@href"
        urls = response.xpath(xp).extract()
        yield from [
            Request(url=response.urljoin(url), callback=self.parse_month)
            for url in urls
        ]

    def parse_month(self, response):
        # Go to the Box Score page for each game
        xp = "//td[@data-stat='box_score_text']/a/@href"
        urls = response.xpath(xp).extract()
        yield from [
            Request(url=response.urljoin(url), callback=self.parse_box) for url in urls
        ]

    def parse_box(self, response):
        # Extract location of the game
        teams_xp = "//a[@itemprop='name']/text()"
        info_xp = "//div[@class='scorebox_meta']/div/text()"
        teams = response.xpath(teams_xp).extract()
        info = response.xpath(info_xp).extract()
        if len(info) == 1:
            logging.warning(f"No arena info at: {response.url}")
            date_ = info[0]
            arena = ""
        else:
            date_, arena = info

        date_ = dateutil.parser.parse(date_)
        game_date = f"{date_.date()}"
        game_time = f"{date_.time():%-I:%M%p}".lower()[:-1]

        record = {
            "date": game_date,
            "time": game_time,
            "road_team": teams[0],
            "home_team": teams[1],
            "arena": arena,
        }

        yield ArenaItem(record)
