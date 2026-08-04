from dataclasses import dataclass, field
import traceback
import json
import re
import OddPath


@dataclass
class Match(object):
    #有如果字樣的,自行判定要不要補到transformer
    league_id: str = ""   #transformer必須有
    league: str = ""   #transformer必須有
    team_home_id: str = ""   #transformer必須有
    team_home: str = ""   #transformer必須有
    team_away_id: str = ""   #transformer必須有
    team_away: str = ""   #transformer必須有
    game_date: str = ""   #transformer必須有
    game_time: str = ""   #transformer必須有
    game_id: str = ""   #transformer必須有
    score_home: str = ""   #transformer必須有
    score_away: str = ""   #transformer必須有
    scores: list = field(default_factory=list)   #transformer必須有
    game_status: str = ""   #transformer必須有
    double_header: str = "N"
    playbyplay: str = field(default_factory=str)   #transformer必須有
    ResultInfo: str = ""  #如果要做賽果資訊 transformer再補
    OtherInfo: str = ""   #如果要做其他賽是資訊 transformer再補
    game_mode: str = "Unknown"
    game_type: str = ""   #transformer必須有
    need_send: bool = field(compare=False, default=False)
    score_count: int = field(compare=False, default_factory=int)
    send_result_count: int = field(compare=False, default_factory=int) #賽果必須透過強制心跳多送幾次出去 這樣才能讓所有的crawlerservice接到賽果的資料
    send_time: int = field(compare=False, default_factory=int)
    receive_time : int = field(compare=False, default_factory=int)
    odds: dict = field(default_factory=dict)  #如果是賠率頁面 transformer再補
    site: str = ""
    country_code: str = ""   #如果是解析name map, transformer再補
    page_name: str = ""    #如果同一場賽事會出現在不同的頁面(比如KU,1XBET會由許多頁面組成所有賠率) transformer再補  要補上該頁面的名稱 才能比對該頁面是否有變化


    def check(self):
        """
        檢查match物件的資料是否合乎邏輯
        如果賠率頁面資訊不完整(沒有主客隊或者分數資訊等等)，需要確保pagename包含這些關鍵字，不然檢查會失敗
        page_name包含market或odd時，只會檢查game_id跟odds
        """
        if any(keyword in self.page_name for keyword in ["market", "odd"]):
            self.check_1(self.game_id, "game_id")
            self.check_8(self.odds, self.game_status)
        else:
            self.check_1(self.league, "league")
            self.check_1(self.league_id, "league_id")
            self.check_1(self.team_home, "team_home")
            self.check_1(self.team_home_id, "team_home_id")
            self.check_1(self.team_away, "team_away")
            self.check_1(self.team_away_id, "team_away_id")
            self.check_1(self.game_id, "game_id")
            self.check_1(self.game_type, "game_type")
            self.check_9(self.game_type)
            self.check_2(self.game_date, "game_date")
            self.check_3(self.game_time, "game_time")
            self.check_4(self.game_status, "game_status")
            self.check_5(self.game_status, self.score_home, "score_home")
            self.check_5(self.game_status, self.score_away, "score_away")
            self.check_6(self.game_status, self.scores, self.score_home, self.score_away)
            if (not self.check_7(self.playbyplay) and self.game_status == "0") or (self.game_status in ["1", "3", "4"] and self.playbyplay!= ""):
                print(f"\033[91m playbyplay 錯誤,Type:{type(self.playbyplay)}, playbyplay:{repr(self.playbyplay)}, game_status:{self.game_status}\033[0m")
            if (not self.check_7(self.ResultInfo) and self.game_status == "1") or (self.game_status in ["0", "3", "4"] and self.ResultInfo!= ""):
                print(f"\033[91m ResultInfo 錯誤,Type:{type(self.ResultInfo)}, ResultInfo:{repr(self.ResultInfo)}, game_status:{self.game_status}\033[0m")
            if not self.check_7(self.OtherInfo):
                print(f"\033[91m OtherInfo 錯誤,Type:{type(self.OtherInfo)}, OtherInfo:{repr(self.OtherInfo)}\033[0m")
            self.check_8(self.odds, self.game_status)

    def check_1(self, data, date_name):
        #必須字串 且 不能是空字串
        if not (type(data) == str and data != ""):
            print(f"\033[91m {date_name} 錯誤, Type:{type(data)}, {date_name}:{repr(data)}\033[0m")

    def check_2(self, data, date_name):
        #必須字串 且 格式必須為dddd-dd-dd (年月日)
        if not (type(data) == str and re.findall(r'\d{4}-\d{2}-\d{2}', data) != [] and len(data) == 10):
            print(f"\033[91m {date_name} 錯誤, Type:{type(data)}, {date_name}:{repr(data)}\033[0m")

    def check_3(self, data, date_name):
        #必須字串 且 格式必須為dd:dd (時分沒有秒)
        if not (type(data) == str and re.findall(r'\d{2}:\d{2}', data) != [] and len(data) == 5):
            print(f"\033[91m {date_name} 錯誤, Type:{type(data)}, {date_name}:{repr(data)}\033[0m")

    def check_4(self, data, date_name):
        #必須是數字類型的字串 且 必須在0~4
        if not  (data in ["0", "1", "2", "3", "4"]):
            print(f"\033[91m {date_name} 錯誤, Type:{type(data)}, {date_name}:{repr(data)}\033[0m")

    def check_5(self, game_status, score_team, score_team_name):
        #主客隊分數在賽前必須是"0",取消延賽必須是"-1",賽中賽後如果有分數訊息必須是整數字串 如果沒分數訊息則"-1"
        retult = False
        if type(score_team) == str and score_team != "":
            if game_status in ["0", "1"]:
                if score_team.isdigit() or score_team == "-1":
                    retult = True
            elif game_status in ["2"]:
                if score_team == "0":
                    retult = True
            elif game_status in ["3", "4"]:
                if score_team == "-1":
                    retult = True
        if not retult:
            print(f"\033[91m {score_team_name} 錯誤,Type:{type(score_team)}, game_status:{repr(game_status)}, {score_team_name}:{repr(score_team)}\033[0m")

    def check_6(self, game_status, scores, score_home, score_away):
        #每節分數在賽前,取消,延賽必須是[],賽中賽後如果有分數必須是[[d,d]] 或 [[d,d], [d,d]](看節數) 如果無分數訊息則為[]
        retult = False
        if type(scores) == list:
            if game_status in ["2", "3", "4"]:
                if scores == []:
                    retult = True
            elif game_status in ["0", "1"]:
                if score_home == "-1" and score_away == "-1":
                    if scores == []:
                        retult = True
                elif score_home != "-1" and score_away != "-1":
                    if scores != []:
                        if {type(score) for score in scores} in [{list}, {tuple}] and \
                        {len(score) for score in scores} == {2} and \
                        {type(s) for score in scores for s in score} == {int}:
                            retult = True
        if not retult:
            print(f"\033[91m scores 錯誤,Type:{type(scores)}, scores:{repr(scores)}, game_status:{repr(game_status)}, score_home:{repr(score_home)}, score_away:{repr(score_away)} \033[0m")

    def check_7(self, data):
        #可以是空字串 不能是'{}' 如果字典內有東西 json.loads後檢查key跟value是不是都是字串
        try:
            result = False
            if data == "":
                result = True
            elif data != '{}':
                data = json.loads(data)
                if all([type(s)==str for k, v in data.items() for s in [k, v]]):
                    result = True
        except:
            error_msg = traceback.format_exc()
            print(f"\033[91m data解析錯誤, type:{type(data)}, data:{repr(data)} {error_msg} \033[0m")
        return result

    def check_8(self, odds, game_status):
        try:
            odd_mapping = OddPath.odd_path
            if game_status in ["1", "3", "4"]:
                if odds != {}:
                    print(f"\033[91m odds錯誤, game_status:{game_status}, odds:{repr(odds)}, 賠率須為{{}}\033[0m")
            else:
                if type(odds) == dict:
                    status_code = {"2":"PreGame","0":"InPlay"}[game_status]
                    for play_mode, price_data in odds.items():
                        if play_mode not in odd_mapping[status_code]:
                            print(f"\033[91m {play_mode}不在{status_code}配置表裡\033[0m")
                        for spread, price in price_data.items():
                            if type(spread) != str or spread=="":
                                print(f"\033[91m spread必須是字串且不可為空, play_mode:{play_mode}, price_data:{repr(price_data)} \033[0m")
                            if "".join(sorted(price.keys())) not in ["AHN", "AHT", "AH", "OU", "NY", "Value", "EvenOdd"]:
                                print(f"\033[91m odd_key錯誤, play_mode:{play_mode}, price_data:{repr(price_data)} \033[0m")
                            for odd_value in price.values():
                                if type(odd_value) == str:
                                    if not (999 > float(odd_value) > 0):
                                        print(f"\033[91m 出現極端賠率, play_mode: {play_mode}, price_data: {repr(price_data)} \033[0m")
                                    if "." in odd_value:
                                        if len(odd_value.split(".")[-1]) >= 4:
                                            print(f"\033[91m 賠率小數點過多, play_mode: {play_mode}, price_data: {repr(price_data)} \033[0m")
                                else:
                                    print(f"\033[91m 賠率不是字串, play_mode: {play_mode}, price_data: {repr(price_data)} \033[0m")
                else:
                    print(f"\033[91m odds格式錯誤, odd須為字典, type:{type(odds)}, odds:{repr(odds)} \033[0m")
        except:
            error_msg = traceback.format_exc()
            print(f"\033[91m odds解析錯誤, type:{type(odds)}, odds:{repr(odds)} {error_msg} \033[0m")

    def check_9(self, game_type):
        # 必須為兩個大寫英文字母，如 "HL"、"BK"、"BS"
        if type(game_type) != str or re.fullmatch(r"[A-Z]{2}", game_type) is None:
            print(f"\033[91m 球種代號格式異常, game_type:{repr(game_type)}\033[0m")
            if game_type == "HL_regular":
                print(f"\033[91m HL常規賽送出的代號須為\"HL\"\033[0m")

    def change_namemap(self):
        """將match物件轉成post給nameapi所需要的格式

        Returns:
            list: list包含多個字典
        """
        return [
            {
                "GameType": self.game_type,
                "Site": self.site,
                "SiteLid": self.league_id,
                "CountryCode": self.country_code,
                "Name": self.league,
            },
            {
                "GameType": self.game_type,
                "Site": self.site,
                "SiteLid": self.league_id,
                "SiteTid": self.team_home_id,
                "CountryCode": self.country_code,
                "Name": self.team_home,
            },
            {
                "GameType": self.game_type,
                "Site": self.site,
                "SiteLid": self.league_id,
                "SiteTid": self.team_away_id,
                "CountryCode": self.country_code,
                "Name": self.team_away,
            },
        ]

    def change_match(self):
        """將match物件轉成crawler service所需的格式
        只有賽前跟賽中需要賠率 其他狀態不會加上賠率

        Returns:
            dict:crawler service所需的字典
        """
        match = {
            "league": self.league,
            "league_id": self.league_id,
            "team_home": self.team_home,
            "team_away": self.team_away,
            "team_home_id": self.team_home_id,
            "team_away_id": self.team_away_id,
            "game_date": self.game_date,
            "game_time": self.game_time,
            "game_id": self.game_id,
            "score_home": self.score_home,
            "score_away": self.score_away,
            "scores": self.scores,
            "game_mode": self.game_mode,
            "game_status": self.game_status,
            "double_header": self.double_header,
            "playbyplay": self.playbyplay,
            "ResultInfo" : self.ResultInfo,
            "OtherInfo": self.OtherInfo,
            "odds": self.change_odd_to_list(self.odds)
        }
        if self.game_status in ["1"]:
            match["playbyplay"] = '{"Time": "Final"}'
        return match

    def change_odd_to_list(self, odd_dct):
        """將物件中的賠率轉成crawler service所需的格式

        Args:
            odd_dct (dict): {"HA":{"4":{"H":"0.5","A":"0.6"}}

        Returns:
            list: [{'PlayMode': 'HA', 'Price': [{'Spread': '4', 'Odd': {'H': '0.5', 'A': '0.6'}}]}]}]
        """
        try:
            return [{"PlayMode":play_mode,"Price":[{"Spread":spread, "Odd":price} for spread, price in spread_data.items()]} for play_mode, spread_data in odd_dct.items()]
        except:
            error_msg = f"{traceback.format_exc()}\nodd_dct: {odd_dct}"
            print(error_msg)
            return []
