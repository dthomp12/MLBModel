from selenium import webdriver
import pandas as pd
import time
from datetime import date, timedelta


def offense_link(startDate, endDate, rightHandPitcher):
    rOrL = "2" if rightHandPitcher else "1"
    return 'https://www.fangraphs.com/leaders/splits-leaderboards?splitArr=' + rOrL + '&splitArrPitch=&position=B&autoPt=false&splitTeams=false&statType=team&statgroup=2&startDate=' + startDate + "&endDate=" + endDate + "&players=&filter=&groupBy=season&wxTemperature=&wxPressure=&wxAirDensity=&wxElevation=&wxWindSpeed=&sort=23,1"


day = date(2018, 5, 1)

options = webdriver.ChromeOptions()
options.headless = True

while day.isoformat() != "2018-10-01":
    driver = webdriver.Chrome("/home/drew/PycharmProjects/MLBdata/chromedriver", options=options)
    driver.get(offense_link("2018-03-01", day.isoformat(), True))
    time.sleep(.8)
    html = driver.page_source
    dfVright = pd.read_html(html)[-1]
    driver.get(offense_link("2018-03-01", day.isoformat(), False))
    time.sleep(.8)
    html = driver.page_source
    dfVleft = pd.read_html(html)[-1]
    driver.close()

    dict = {"Date" : day.isoformat()}

    try:
        for index, row in dfVright.iterrows():
            team = row["Tm"]
            wrc = row["wRC+"]
            dict[team + "-R"] = wrc

        for index, row in dfVleft.iterrows():
            team = row["Tm"]
            wrc = row["wRC+"]
            dict[team + "-L"] = wrc

    except:
        continue

    wrcDF = pd.read_csv("wrcs2018.csv")

    new_df = pd.DataFrame([dict])
    final = pd.concat([wrcDF, new_df], ignore_index=True)
    final = final.loc[:, ~final.columns.str.contains('^Unnamed')]
    final.to_csv("wrcs2018.csv")

    day = day + timedelta(days=1)