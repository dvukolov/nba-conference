# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.org/en/latest/topics/items.html

from scrapy import Item, Field


class ArenaItem(Item):
    date = Field()
    time = Field()
    road_team = Field()
    home_team = Field()
    arena = Field()


class HomeItem(Item):
    season = Field()
    team = Field()
    home_arena = Field()


class PerfItem(Item):
    date = Field()
    team = Field()
    conference = Field()
    pace = Field()
    ortg = Field()
    free_throw_rate = Field()
    three_pt_att_rate = Field()
    true_shooting_pct = Field()
    total_rebound_pct = Field()
    team_steal_pct = Field()
    team_block_pct = Field()
    effective_fg_pct = Field()
    turnovers_per100 = Field()
    off_rebound_pct = Field()
    def_rebound_pct = Field()


class ScheduleItem(Item):
    season = Field()
    date = Field()
    time = Field()
    road_team_abbr = Field()
    road_team = Field()
    road_team_pts = Field()
    home_team_abbr = Field()
    home_team = Field()
    home_team_pts = Field()
    overtime_flg = Field()
    game_attnd = Field()
    playoff_gm = Field()
