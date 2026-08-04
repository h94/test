from dataclasses import dataclass, field
from typing import Any, Dict, List, Type
import json
import re

@dataclass
class OtherInfo:
    """
    otherinfo dataclass
    """
    # === 所有欄位皆為可選，站台沒給就不用填 ===
    starting_pitcher_home: str = "" #主隊先發投手名字
    starting_pitcher_away: str = "" #客隊先發投手名字
    starting_pitcher_era_home: str = "" #主隊先發投手本季防禦率
    starting_pitcher_era_away: str = "" #客隊先發投手本季防禦率
    team_home_start_pitcher_info: dict = field(default_factory=dict) #主隊先發投手資訊
    team_away_start_pitcher_info: dict = field(default_factory=dict) #客隊先發投手資訊
    team_home_topplayer_info: dict = field(default_factory=dict) #主隊關鍵球員資訊
    team_away_topplayer_info: dict = field(default_factory=dict) #客隊關鍵球員資訊
    team_home_standings: dict = field(default_factory=dict) #主隊戰績資訊
    team_away_standings: dict = field(default_factory=dict) #客隊戰績資訊
    highlights: str = "" #比賽戰前分析，這個如果很長的話建議改成寫檔
    home_probability: str = "" #主隊勝負平預測機率 ("XX.X%")
    away_probability: str = "" #客隊勝負平預測機率
    draw_probability: str = "" #平手勝負平預測機率 (看球種，有就填沒有就留空)
    bet_HA:str = "" #預測哪隊贏，不用填(自動計算)
    over_ou_probability: str = "" #大小球預測，Over機率 ("XX.X%")
    under_ou_probability: str = "" #大小球預測，Under機率
    predict_OU: str = "" #大小球預測球頭
    bet_OU: str = "" #某個球頭預測大或小，有寫機率的話框架會自動計算("Over","Under")
    correct_score_home: str = "" #主隊比分預測
    correct_score_away: str = "" #客隊比分預測
    extra_info: dict = field(default_factory=dict) #資料都不在上面的話就寫來這裡(字典的值需要json.dumps)

    # === 型別對應屬性(用於type check) ===
    _type_check_map: Dict[Type, List[str]] = field(init=False, default_factory=lambda: {
        str: [
            'starting_pitcher_home',
            'starting_pitcher_away',
            "starting_pitcher_era_home",
            "starting_pitcher_era_away",
            "home_probability",
            "away_probability",
            "draw_probability",
            "bet_HA",
            "highlights",
            "correct_score_home",
            "correct_score_away",
            "over_ou_probability",
            "under_ou_probability",
            "predict_OU",
            "bet_OU",
        ],
        dict: [
            'extra_info',
            "team_home_start_pitcher_info",
            "team_away_start_pitcher_info",
            "team_home_topplayer_info",
            "team_away_topplayer_info",
            "team_home_standings",
            "team_away_standings",
        ],
        int: [],
    })

    def __post_init__(self):
        """
        做一系列的資料驗證跟自動填入機制
        1.自動檢查欄位的型別是否符合 _type_check_map 設定
        2.如果有extra info，檢查extra info的值是不是字串
        """
        for expected_type, field_list in self._type_check_map.items():
            for field_name in field_list:
                value = getattr(self, field_name, None)
                if not isinstance(value, expected_type):
                    raise TypeError(
                        f"'{field_name}' 需要是 {expected_type.__name__}, 目前為 {type(value).__name__}"
                    )
        if self.extra_info:
            if not all([type(s)==str for k, v in self.extra_info.items() for s in [k, v]]):
                raise TypeError("extra info 字典的值須為字串")

        self.validate_probability_format()
        self.auto_fill_bet_HA()
        self.auto_fill_bet_OU()
        self.check_bet_ha()
        self.check_bet_ou()

    def validate_probability_format(self):
        """
        驗證 home/away/draw 的機率格式是否為 'XX.X%' 'XX%' 的字串

        Raises:
            ValueError: 如果格式錯誤
        """
        pattern = re.compile(r"^(?:0(?:\.\d)?|[1-9]?\d(?:\.\d)?|100(?:\.0)?)%$")
        for label, value in {
            "home_probability": self.home_probability,
            "away_probability": self.away_probability,
            "draw_probability": self.draw_probability,
            "over_ou_probability": self.over_ou_probability,
            "under_ou_probability": self.under_ou_probability
        }.items():
            if value and not pattern.fullmatch(value.strip()):
                raise ValueError(f"{label} 格式錯誤，應為 0~100 的整數或一位小數百分比(如 70%、70.5%、100%、100.0%)，實際為: {value}")

    def auto_fill_bet_HA(self):
        """
        根據最大機率自動填入 "Home", "Away", 或 "Draw"
        """
        prob_map = {
            "Home": self.home_probability,
            "Away": self.away_probability,
            "Draw": self.draw_probability
        }

        # 過濾掉空字串，並轉為浮點數
        parsed_probs = {}
        for key, val in prob_map.items():
            if val:
                try:
                    parsed_probs[key] = float(val.strip('%'))
                except ValueError:
                    continue  # 格式錯誤則略過

        # 若少於 2 個有效資料，則不做處理
        if len(parsed_probs) < 2:
            return

        # 選最大值對應的項目填入 bet_HA
        self.bet_HA = max(parsed_probs, key=parsed_probs.get)

    def auto_fill_bet_OU(self):
        """
        根據最大機率自動填入 "Over" "Under"
        """
        prob_map = {
            "Over": self.over_ou_probability,
            "Under": self.under_ou_probability,
        }

        # 過濾掉空字串，並轉為浮點數
        parsed_probs = {}
        for key, val in prob_map.items():
            if val:
                try:
                    parsed_probs[key] = float(val.strip('%'))
                except ValueError:
                    continue  # 格式錯誤則略過

        # 若少於 2 個有效資料，則不做處理
        if len(parsed_probs) < 2:
            return
        # 檢查球頭有沒有填
        if not self.predict_OU: raise ValueError("大小球預測球頭為空")
        # 選最大值對應的項目填入 bet_OU
        self.bet_OU = max(parsed_probs, key=parsed_probs.get)


    def check_bet_ha(self):
        """
        檢查bet_HA是不是'Home' 'Away'或 'Draw' (大小寫有區別)
        """
        if self.bet_HA:
            if any(check == self.bet_HA for check in ["Home", "Away", "Draw"]):
                return
            else:
                raise ValueError(f"bet_HA 格式錯誤，應為 'Home' 'Away'或 'Draw'，實際為: {self.bet_HA}")

    def check_bet_ou(self):
        """
        檢查bet_OU是不是'Over' 'Under'
        """
        if self.bet_OU:
            if any(check == self.bet_OU for check in ['Over', 'Under']):
                return
            else:
                raise ValueError(f"bet_OU 格式錯誤，應為 'Over' 或 'Under'，實際為: {self.bet_OU}")

    def create_otherinfo(self) -> str:
        """
        建立符合otherinfo的JSON字串

        Returns:
            str: '{"home_probability": "10.0%", "away_probability": "90.0%", "bet_HA": "Away"}'
        """
        self.__post_init__()
        otherinfo = {}
        if self.extra_info: otherinfo = self.extra_info
        for field_name, value in self.__dict__.items():
            if any(keyword in field_name for keyword in ["_type", "extra", "ou_probability"]): continue
            if not value: continue #沒填的屬性就跳過
            if isinstance(value, dict): value = json.dumps(value, ensure_ascii=False) #字典就先轉成JSON字串
            otherinfo[field_name] = value

        if not otherinfo: return "" #不能丟"{}"回去，都沒東西改丟空字串
        return json.dumps(otherinfo, ensure_ascii=False)