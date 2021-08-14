# -*- coding: utf-8 -*-
import dateutil.parser
import pandas as pd
import scrapy
from parsel import Selector
from scrapy.http import Request
from nba.items import PerfItem

conference_map = {
    "Atlanta Hawks": "E",
    "Boston Celtics": "E",
    "Brooklyn Nets": "E",
    "Charlotte Bobcats": "E",
    "Charlotte Hornets": "E",
    "Chicago Bulls": "E",
    "Cleveland Cavaliers": "E",
    "Dallas Mavericks": "W",
    "Denver Nuggets": "W",
    "Detroit Pistons": "E",
    "Golden State Warriors": "W",
    "Houston Rockets": "W",
    "Indiana Pacers": "E",
    "Los Angeles Clippers": "W",
    "Los Angeles Lakers": "W",
    "Memphis Grizzlies": "W",
    "Miami Heat": "E",
    "Milwaukee Bucks": "E",
    "Minnesota Timberwolves": "W",
    "New Jersey Nets": "E",
    "New Orleans Hornets": "E",
    "New Orleans Pelicans": "W",
    "New Orleans/Oklahoma City Hornets": "W",
    "New York Knicks": "E",
    "Oklahoma City Thunder": "W",
    "Orlando Magic": "E",
    "Philadelphia 76ers": "E",
    "Phoenix Suns": "W",
    "Portland Trail Blazers": "W",
    "Sacramento Kings": "W",
    "San Antonio Spurs": "W",
    "Seattle SuperSonics": "W",
    "Toronto Raptors": "E",
    "Utah Jazz": "W",
    "Vancouver Grizzlies": "W",
    "Washington Wizards": "E",
}


class PerfSpider(scrapy.Spider):
    name = "perf"
    allowed_domains = ["basketball-reference.com"]
    start_urls = ["http://basketball-reference.com/"]
    custom_settings = {
        # exported fields and order
        "FEED_EXPORT_FIELDS": [
            "date",
            "team",
            "conference",
            "pace",
            "ortg",
            "free_throw_rate",
            "three_pt_att_rate",
            "true_shooting_pct",
            "total_rebound_pct",
            "team_steal_pct",
            "team_block_pct",
            "effective_fg_pct",
            "turnovers_per100",
            "off_rebound_pct",
            "def_rebound_pct",
        ]
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
        # Extract performance metrics for each team
        teams_xp = "//a[@itemprop='name']/text()"
        info_xp = "//div[@class='scorebox_meta']/div/text()"
        teams = response.xpath(teams_xp).extract()
        date_ = response.xpath(info_xp).extract_first()
        date_ = dateutil.parser.parse(date_)
        game_date = f"{date_.date()}"

        pace_xp = '//td[@data-stat="off_rtg"]/text()'
        pace_comment_xp = "//comment()[contains(., 'Pace Factor')]"

        comment = (
            response.xpath(pace_comment_xp)
            .extract_first()
            .replace("<!--", "")
            .replace("-->", "")
        )
        sel = Selector(comment)
        pace = sel.xpath(pace_xp).extract()

        ftr_xp = '//tfoot/tr/td[@data-stat="fta_per_fga_pct"]/text()'
        tpar_xp = '//tfoot/tr/td[@data-stat="fg3a_per_fga_pct"]/text()'
        tshp_xp = '//tfoot/tr/td[@data-stat="ts_pct"]/text()'
        trp_xp = '//tfoot/tr/td[@data-stat="trb_pct"]/text()'
        stp_xp = '//tfoot/tr/td[@data-stat="stl_pct"]/text()'
        bp_xp = '//tfoot/tr/td[@data-stat="blk_pct"]/text()'
        efgp_xp = '//tfoot/tr/td[@data-stat="efg_pct"]/text()'
        tp100_xp = '//tfoot/tr/td[@data-stat="tov_pct"]/text()'
        orp_xp = '//tfoot/tr/td[@data-stat="orb_pct"]/text()'
        drp_xp = '//tfoot/tr/td[@data-stat="drb_pct"]/text()'

        df = pd.DataFrame(
            {
                "date": [game_date] * 2,
                "team": teams,
                "conference": [conference_map[team] for team in teams],
                "pace": pace,
                "free_throw_rate": response.xpath(ftr_xp).extract(),
                "three_pt_att_rate": response.xpath(tpar_xp).extract(),
                "true_shooting_pct": response.xpath(tshp_xp).extract(),
                "total_rebound_pct": response.xpath(trp_xp).extract(),
                "team_steal_pct": response.xpath(stp_xp).extract(),
                "team_block_pct": response.xpath(bp_xp).extract(),
                "effective_fg_pct": response.xpath(efgp_xp).extract(),
                "turnovers_per100": response.xpath(tp100_xp).extract(),
                "off_rebound_pct": response.xpath(orp_xp).extract(),
                "def_rebound_pct": response.xpath(drp_xp).extract(),
            }
        )
        numeric_columns = [
            c for c in df.columns if c not in ["date", "team", "conference"]
        ]
        for c in numeric_columns:
            df[c] = df[c].astype(float)

        records = df.to_dict(orient="records")
        for rec in records:
            yield PerfItem(rec)
