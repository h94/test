from TCZB import Globals
from Match import Match
from datetime import datetime
import re

class DataTransformer():
    def __init__(self, send_msg):
        self.send_msg = send_msg
        self.setting = Globals.Globals.CrawlerData['transformer']


    def get_match(self, time_stamp, lang, data):
        """由provider 的資料中訊息整理出對應的訊息
        Args:
            參數自行決定要帶入那些
        Returns:
            list: [Match物件]
        """
        game_type, page_type, game_html = data
        try:
            matches = []
            for game_data in game_html:
                league_id = game_data["league_id"]
                league = game_data["league"]
                team_home_id = game_data["team_home_id"]
                team_home = game_data["team_home"]
                team_away_id = game_data["team_away_id"]
                team_away = game_data["team_away"]
                game_date = game_data["game_date"]
                game_time = game_data["game_time"]
                game_id = game_data["game_id"]
                score_home = game_data["score_home"]
                score_away = game_data["score_away"]
                scores = game_data["scores"]
                playbyplay = game_data["playbyplay"]
                game_status = game_data["game_status"]
                odds = game_data["odds"]
                #if not self.check_ststus_time(datetime.now(), game_status, game_date, game_time):return []  #正式開發後必須打開
                match = Match(
                        league_id=league_id,
                        league=league,
                        team_home_id=team_home_id,
                        team_home=team_home,
                        team_away_id=team_away_id,
                        team_away=team_away,
                        game_date=game_date,
                        game_time=game_time,
                        game_id=game_id,
                        score_home=score_home,
                        score_away=score_away,
                        scores=scores,
                        game_status=game_status,
                        game_type=game_type,
                        playbyplay = playbyplay,
                        odds=odds,
                        page_name=page_type,
                        )
                matches.append(match)
            return matches
        except:
            self.send_msg()

    def get_quantify(self, spread):
        spread = str(spread)
        spread = spread.replace(" ","")
        if '/' in spread: # 0.5/1
            front, back = spread.split("/")
            quantify = int((float(front) + float(back))*100)
        elif ',' in spread: # 0,0.5
            front, back = spread.split(",")
            quantify = int((float(front) + float(back))*100)
        else:#1 0.5  0.75 -1
            quantify = int(float(re.sub(r'^\+', "", spread))*200)
        return quantify

    def get_spread(self, site_spread, opposite=False):
        """
        取得球頭

        Args:
            site_spread (str): "27.5" "0.5/1"
            opposite (bool, optional): 是否反轉球頭

        Returns:
            spread (str):
                "1.5/2" opposite=False -> "2+50"
                "1.75" opposite=False -> "2+50"
                "1.25" opposite=False -> "1-50"
                "22.5" opposite=False -> "22.5"
                "22.5" opposite=True -> "-22.5"
                "27:0" opposite=False -> "27:0" (歐讓)
                "27:0" opposite=True -> "0:27" (歐讓)
        """
        #歐洲讓分(27:0, 0:27)
        if ":" in site_spread:
            if not opposite:
                return site_spread  # 原封不動丟回來
            else:
                a, b = site_spread.split(":")
                site_spread = f"{b}:{a}"  # 反轉 spread
                return site_spread

        quantify = self.get_quantify(site_spread)
        quantify = quantify*-1 if opposite == True else quantify
        if quantify %100==0:
            spread = "{:g}".format(quantify/200)
        else:
            head = round(quantify/200)
            percent = head*200-quantify
            spread = f"{head}{'+' if percent>0 else ''}{percent or ''}"
        return spread

    def update(self, odds, play_mode_odd):
        for play_mode, odd_datas in play_mode_odd.items():
            if play_mode not in odds:
                odds[play_mode] = odd_datas
            else:
                for spread, price in odd_datas.items():
                    if spread in odds[play_mode]:
                        odds[play_mode][spread].update(price)
                    else:
                        odds[play_mode].update(odd_datas)
        return odds

    def check_odd(self, odds):
        need_remove = []
        for play_mode, odd_datas in odds.items():
            for spread, price in odd_datas.items():
                if "".join(sorted(price.keys())) not in ["AHN", "AHT", "AH", "OU", "NY", "Value", "EvenOdd"]:
                    need_remove.append([play_mode, spread])
        for play_mode, spread in need_remove:
            odds[play_mode].pop(spread, None)
        need_remove = []
        for play_mode, odd_datas in odds.items():
            if not odd_datas:
                need_remove.append(play_mode)
        for play_mode in need_remove:
            odds.pop(play_mode, None)
        return odds

    def check_ststus_time(self, now, game_status, game_date, game_time):
        """檢查時間與賽事狀態  不符的返回False 由外層跳過
        狀態是2(賽前) 現在時間必須小於賽事時間, 在比賽開打前才送pregame
        狀態是0(賽中) 現在時間可以比賽事時間提早10分或者經過12小時, 賽事提早太多或者經過12小時都沒打完大概都有問題
        狀態是1(賽後)3(延期)4(取消) 現在時間可以比賽事時間經過0.5小時, 因為有遇過賽前賽事的狀態變來變去
        Args:
            now (datetime): datetime.datetime(2023, 3, 25, 13, 25, 46, 655281)
            game_status (str): 0,1,2,3,4
            game_date (str): 2023-03-01
            game_time (str): 12:00
        Returns:
            bool: True, Flase
        """
        try:
            game_date_time = datetime.strptime(game_date+game_time, "%Y-%m-%d%H:%M")
            time_diff = (now-game_date_time).total_seconds()
            result = False
            if game_status == "2" and time_diff < 0:
                result = True
            elif game_status == "0" and -600 < time_diff < 43200:
                result = True
            elif game_status in ["1", "3", "4"] and time_diff > 1800:
                result = True
            return result
        except:
            self.send_msg()

