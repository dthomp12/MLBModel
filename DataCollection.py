import math
import traceback

import pandas as pd
import datetime

class PitcherNotFoundException(Exception):
    pass


year = "2018"
wrcDF = pd.read_csv("wrcs2018.csv")

team_num = {"ARI": "15", "ATL": "16", "BAL": "2", "BOS": "3", "CHC": "17",
            "CHW": "4", "CIN": "18", "CLE": "5", "COL": "19", "DET": "6", "HOU": "21"
    , "KCR": "7", "LAA": "1", "LAD": "22", "MIA": "20", "MIL": "23", "MIN": "8"
    , "NYM": "25", "NYY": "9", "OAK": "10", "PHI": "26", "PIT": "27", "SDP": "29"
    , "SEA": "11", "SFG": "30", "STL": "28", "TBR": "12", "TEX": "13", "TOR": "14", "WSN": "24"}


def spLink(team, date):
    return f"https://www.fangraphs.com/leaders.aspx?pos=all&stats=sta&lg=all&qual=0&type=8&season={year}&month=1000&season1={year}&ind=0&team={team_num[team]}&rost=&age=&filter=&players=&startdate={year}-03-01&enddate={date}&page=1_50"


def spStats(team, pitcher, date):
    df = pd.read_html(spLink(team, date))[16]
    xFIP, G, IP = None, None, None
    for index, row in df.iterrows():
        if row.iloc[1] == pitcher:
            xFIP = row.iloc[19]
            G = row.iloc[5]
            IP = row.iloc[7]
            break
    if xFIP is None or float(G) < 2:
        raise PitcherNotFoundException
    IP = float(IP)
    IP = math.floor(IP) + (IP % 1) * 1 / 3
    return float(xFIP), round(IP / float(G), 3)

def handLink(spName, spCode):
    letter = spName.split(" ")[1][0].upper()
    return f"https://www.retrosheet.org/boxesetc/{letter}/P{spCode}.htm"

def getHand(spName, spCode):
    df = pd.read_html(handLink(spName, spCode))[0]
    hand = df.iloc[3].iloc[0].split(" ")[3]
    if hand == "Right":
        return 1
    elif hand == "Left":
        return -1
    else:
        return 0

def rpLink(team, date):
    return f"https://www.fangraphs.com/leaders.aspx?pos=all&stats=rel&lg=all&qual=0&type=8&season={year}&month=0&season1={year}&ind=0&team={team_num[team]},ts&rost=0&age=0&filter=&players=0&startdate={year}-03-01&enddate={date}"

def rpStats(team, date):
    df = pd.read_html(rpLink(team, date))[16]
    xFIP = df.iloc[0].iloc[19]
    return float(xFIP)

def offenseLink(team, date):
    return f"https://www.fangraphs.com/leaders.aspx?pos=all&stats=bat&lg=all&qual=0&type=8&season={year}&month=0&season1={year}&ind=0&team={team_num[team]},ts&rost=0&age=0&filter=&players=0&startdate{year}-03-01=&enddate={date}"

def offensiveStats(team, date):
    df = pd.read_html(offenseLink(team, date))[16]
    BsR = df.iloc[0].iloc[18]
    return float(BsR)

def fieldingLink(team, date):
    return f"https://www.fangraphs.com/leaders.aspx?pos=all&stats=fld&lg=all&qual=0&type=1&season={year}&month=0&season1={year}&ind=0&team={team_num[team]},ts&rost=0&age=0&filter=&players=0&startdate{year}-03-01=&enddate={date}"

def fieldingStats(team, date):
    df = pd.read_html(fieldingLink(team, date))[16]
    FRM = df.iloc[0][18]
    OAA = df.iloc[0][19]
    return float(FRM), float(OAA)

def hittingStats(team, date):
    WRCL, WRCR = 0, 0
    for index, row in wrcDF.iterrows():
        if row["Date"] == date:
            WRCL = row[team + "-L"]
            WRCR = row[team + "-R"]
            break
    return int(WRCL), int(WRCR)

def team_stats(team, sp, spCode, dateString):
    date = datetime.date.fromisoformat(dateString)
    date += datetime.timedelta(days=-1)
    date = date.isoformat()

    spxFIP, spIperG = spStats(team, sp, date)

    hand = getHand(sp, spCode)

    rpxFIP = rpStats(team, date)
    BsR = offensiveStats(team, date)
    FRM, OAA = fieldingStats(team, date)
    WRCL, WRCR = hittingStats(team, date)
    return WRCL, WRCR, FRM, OAA, BsR, hand, spxFIP, rpxFIP, spIperG


games = pd.read_csv("GL2018.csv")

for index, row in games.iterrows():
    if index < 480:
        continue
    date = str(row.iloc[0])
    date = date[0:4] + "-" + date[4:6] + "-" + date[6:]

    awayTeam = row.iloc[3]
    homeTeam = row.iloc[6]
    awayScore = row.iloc[9]
    homeScore = row.iloc[10]
    awaySP = row.iloc[102]
    awaySPCode = row.iloc[101]
    homeSP = row.iloc[104]
    homeSPCode = row.iloc[103]

    ou = homeScore + awayScore
    spread = homeScore - awayScore
    homeWin = 1 if spread > 0 else 0

    try:
        stats = team_stats(homeTeam, homeSP, homeSPCode, date) + team_stats(awayTeam, awaySP, awaySPCode, date)
        hWRCL, hWRCR, hFRM, hOAA, hBsR, hHand, hSpxFIP, hRpxFIP, hSpIperG, aWRCL, aWRCR, aFRM, aOAA, aBsR, aHand, aSpxFIP, aRpxFIP, aSpIperG = stats
        data = [date, awayTeam, homeTeam, homeWin, spread, ou, hWRCL, hWRCR, hFRM, hOAA, hBsR, hHand, hSpxFIP, hRpxFIP, hSpIperG, aWRCL, aWRCR, aFRM, aOAA, aBsR, aHand, aSpxFIP, aRpxFIP, aSpIperG]
        for i in range(len(data)):
            data[i] = str(data[i])
        with open("MLBdata.csv", "a") as f:
            f.write(",".join(data))
            f.write("\n")
    except PitcherNotFoundException:
        print("Pitcher not found exception")
        continue
    except Exception:
        print(traceback.format_exc())