# -*- coding: utf-8 -*-
import pandas as pd
import scrapy
from scrapy.http import Request
from nba.items import ScheduleItem


playoffs = {
    "2018-19": "2019-04-13",
    "2017-18": "2018-04-14",
    "2016-17": "2017-04-15",
    "2015-16": "2016-04-16",
    "2014-15": "2015-04-18",
    "2013-14": "2014-04-19",
    "2012-13": "2013-04-20",
    "2011-12": "2012-04-28",
    "2010-11": "2011-04-16",
    "2009-10": "2010-04-17",
    "2008-09": "2009-04-18",
    "2007-08": "2008-04-19",
    "2006-07": "2007-04-21",
    "2005-06": "2006-04-22",
    "2004-05": "2005-04-23",
    "2003-04": "2004-04-17",
    "2002-03": "2003-04-19",
    "2001-02": "2002-04-20",
    "2000-01": "2001-04-21",
}


class ScheduleSpider(scrapy.Spider):
    name = "schedule"
    allowed_domains = ["basketball-reference.com"]
    start_urls = ["http://basketball-reference.com/"]
    custom_settings = {
        # exported fields and order
        "FEED_EXPORT_FIELDS": [
            "season",
            "date",
            "time",
            "road_team_abbr",
            "road_team",
            "road_team_pts",
            "home_team_abbr",
            "home_team",
            "home_team_pts",
            "overtime_flg",
            "game_attnd",
            "playoff_gm",
        ]
    }

    def start_requests(self):
        self.abbr = pd.read_csv("../data/team-abbr.csv")

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
        # Scrape the schedule table
        row_xp = "//*[@id='schedule']/tbody/tr"
        season_xp = "//h1[@itemprop='name']/span[1]/text()"
        date_xp = './th[@data-stat="date_game"]/a/text()'
        time_xp = './td[@data-stat="game_start_time"]/text()'
        road_xp = './td[@data-stat="visitor_team_name"]/a/text()'
        road_pts_xp = './td[@data-stat="visitor_pts"]/text()'
        home_xp = './td[@data-stat="home_team_name"]/a/text()'
        home_pts_xp = './td[@data-stat="home_pts"]/text()'
        overtime_xp = './td[@data-stat="overtimes"]/text()'
        attend_xp = './td[@data-stat="attendance"]/text()'

        rows = response.xpath(row_xp)

        def parse_table(row):
            return {
                "date": row.xpath(date_xp).extract_first(),
                "time": row.xpath(time_xp).extract_first(),
                "road_team": row.xpath(road_xp).extract_first(),
                "road_team_pts": row.xpath(road_pts_xp).extract_first(),
                "home_team": row.xpath(home_xp).extract_first(),
                "home_team_pts": row.xpath(home_pts_xp).extract_first(),
                "overtime_flg": row.xpath(overtime_xp).extract_first(),
                "game_attnd": row.xpath(attend_xp).extract_first(),
            }

        docs = list(map(parse_table, rows))
        df = pd.DataFrame(docs)

        # Remove games not yet played
        df = df[(df.road_team_pts != "") & df.road_team_pts.notnull()]

        df = df.merge(
            self.abbr.rename(
                columns={"long_name": "road_team", "abbr": "road_team_abbr"}
            ),
            on="road_team",
        ).merge(
            self.abbr.rename(
                columns={"long_name": "home_team", "abbr": "home_team_abbr"}
            ),
            on="home_team",
        )

        season = response.xpath(season_xp).extract_first()
        df["season"] = season
        df["date"] = pd.to_datetime(df["date"]).dt.date.astype(str)
        df["playoff_gm"] = (df.date >= playoffs[season]).astype(int)
        df["game_attnd"] = df["game_attnd"].str.replace(",", "").astype(int)
        columns = [
            "season",
            "date",
            "time",
            "road_team_abbr",
            "road_team",
            "road_team_pts",
            "home_team_abbr",
            "home_team",
            "home_team_pts",
            "overtime_flg",
            "game_attnd",
            "playoff_gm",
        ]
        df = df[columns]
        records = df.to_dict(orient="records")
        for rec in records:
            yield ScheduleItem(rec)
