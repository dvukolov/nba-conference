# NBA Conference Bias

Statistical modeling of NBA conference bias due to differences in travel and schedule.

Harvard University<br>
Class: STAT 109 — Introduction to Statistical Modeling<br>
Deliverables: [Project Report](https://raw.githubusercontent.com/dvukolov/nba-conference/master/report.pdf) with R code listings

## Table of Contents

* [Project Summary](#project-summary)
   * [Problem Statement](#problem-statement)
   * [Data Collection](#data-collection)
   * [Feature Engineering](#feature-engineering)
   * [Statistical Modeling](#statistical-modeling)
* [Requirements](#requirements)

## Project Summary

### Problem Statement

The National Basketball Association is composed of 30 teams distributed across the United States and equally split between two conferences: the West and the East. We sought to investigate whether there is a potential bias in the NBA that grants teams in one conference a relatively easier path to success due to the differences in travel and schedule.

### Data Collection

Several web scrapers were written to collect the required raw data from Baseball-Reference.com on:

- The past NBA games, their schedule and outcome, as well as the resulting team performance
- All-NBA awards for the best individual players as a reflection of their strength
- The names of the venues where each basketball game took place
- The home arenas for the teams in each year, that served as the starting point for traveling at the beginning of the respective season

The resulting dataset contains information on a total of 24,462 games, 8,535 of which took place between one Western and one Eastern Conference team.

### Feature Engineering

We recreated an itinerary for every team for the past 18 years, similar to the one below for the Boston Celtics during the 2018-19 season:

![boston-celtic-itinerary](https://user-images.githubusercontent.com/949884/129446972-3ba44225-686d-4d0b-a669-8058789521c4.png)

Google Maps APIs were used:

- To geocode the venues into an exact address and its geographic coordinates (latitude and longitude)
- To identify the time zones associated with each geographical location

**Travel-related predictors:** We estimated the amount of travel by each team to a particular location using the geodesic distance. We also computed the number of time zones traveled, the direction of travel (eastward vs westward), and the change in longitude.

**Schedule-related variables:** We take into consideration several aspects tightly interlinked with travel, which can contribute to a build-up of fatigue:

- the number of days of rest a team had prior to the game
- the number of games a team had to play in a fixed period
- the number of games they played while being on the road

**Performance metrics:** Finally, we control for the strongest predictors of team success using multiple performance indicators: the total number of wins for the previous season, the so-called Four Factors, advanced box score statistics, and others.

All of the data mentioned above was summarized with rolling averages and combined in a single dataset for further analysis.

### Statistical Modeling

**Linear Regression:** The analysis was conducted using multiple linear regression. The point differential (the number of points scored by one team minus the number of points scored by the opponent) serves as our response variable. The differences between the indicators for the two competing teams act as explanatory variables.

**Diagnostics:** Particular importance is given to interpretability. To ensure model validity, we run diagnostics and check if the assumptions of linear regression are satisfied, namely: linearity, independence and normality of errors, homoscedasticity, and multicollinearity.

**Resampling:** Finally, stepwise regression and bootstrap are used to assess the inclusion frequency of certain predictors of interest in the final model.

Please see the [project report](https://raw.githubusercontent.com/dvukolov/nba-conference/master/report.pdf) for a detailed description of the research and the findings.

## Requirements

The analysis was conducted in R using a small number of third party packages, particularly: 

- `tidyverse`: for all data handling tasks
- `car`: for computing variance inflation factors and other diagnostics
- `nortest`: for normality tests

To reproduce the results, R version 3.6.0 or higher is required due to a new default method for generating a discrete uniform distribution.

The data collection tools are based on the Scrapy framework in Python. Assuming that the layout of the source website stays the same, the crawlers can be run with:

```shell
$ scrapy crawl <spider name> -t csv -o <output.csv>
```

Additional data present in the `data/` repo directory may have been gathered manually.