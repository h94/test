import Compair
import Merge
import Heart_beat
import time
from datetime import datetime
import copy
from collections import defaultdict

class FlowControl(object):
    def __init__(self, send_msg, site_type):
        self.send_msg = send_msg
        self.site_type = site_type  #Appsetting設置scor或odd,沒有賠率的比分站台用score, 有賠率的用odd
        self.compair = Compair.Compair(send_msg)
        self.merge = Merge.Merge(send_msg)
        self.heart_beat = Heart_beat.Heart_beat(send_msg, self.site_type)
        self.each_cache = {} #各別檔案的快取
        self.merge_dct = {} #合併個別檔案後的快取
        self.status_cache = {}  #該場賽事目前的賽事狀態快取
        self.each_game_id = set() #用來紀錄太久沒收到資料的each_game_ID
        self.merge_id = set() #用來紀錄太久沒更新資料的merge_id
        self.time_cache = defaultdict(time.time)


    def flow_control(self, matches):
        self.remove_long_time_cache()
        need_remove = self.check_each_cache()
        matches = need_remove + matches #因為順序 必須這樣寫 不用+=
        now, datetime_now  = time.time(), datetime.now()
        send_datas = {}
        game_ids = [match.game_id+match.page_name for match in matches]
        gameid_dict = {}
        for index, game_id in enumerate(game_ids):
            gameid_dict[game_id] = index
        for index, match in enumerate(matches):
            try:
                if (match.team_home and match.team_away) and (match.team_home == match.team_away): continue
                if len(match.team_home) > 80 or len(match.team_away) > 80: continue
                if index not in gameid_dict.values():continue
                
                game_id = match.game_id
                game_status = match.game_status
                page_name = match.page_name
                if not self.check_ststus(game_id, game_status): continue
                each_game_id = f"{game_id}@{page_name}"
                match.receive_time = now
                is_change = True
                new_odd = match.odds
                if each_game_id in self.each_cache:
                    cache = self.each_cache[each_game_id]
                    merge = self.merge_dct.get(game_id, {})
                    if match == cache:
                        is_change = False
                        new_odd = {}
                    else:
                        new_odd = self.compair.compair_odd(cache, match, merge)
                self.each_cache[each_game_id] = match
                self.merge.merge(self.merge_dct, match, new_odd)
                if game_id not in self.merge_dct:continue
                self.remove_not_HA_OU(self.merge_dct[game_id], datetime_now)
                self.merge_dct[game_id].need_send = False
                if is_change:
                    self.merge_dct[game_id].need_send = True
            except:
                msg = f"match: {match}"
                self.send_msg(msg=msg)
                continue
        send_datas = self.heart_beat.heart_beat(self.merge_dct)
        return send_datas


    def remove_long_time_cache(self):
        """如果一直沒接收到該筆資料,則刪除該筆快取
        """
        try:
            send_data = {
                "remove_each_cache": [],
                "remove_merge": [],
            }

            for each_game_id in self.each_game_id:
                each_cache = self.each_cache.pop(each_game_id, None)
                if each_cache:
                    send_data["remove_each_cache"].append([each_cache.game_type, each_game_id, each_cache.game_status])

            for merge_id in self.merge_id:
                merge = self.merge_dct.pop(merge_id, None)
                if merge:
                    send_data["remove_merge"].append([merge.game_type, merge_id, merge.game_status])

            self.each_game_id = set()
            self.merge_id = set()

            if list(send_data.values()) != [[], []]:
                self.send_msg(msg=send_data, level="Trace")
        except:
            self.send_msg()


    def check_ststus(self, game_id, game_status):
        """多台provider在提供資料,在接近開賽事,有時會有一點點時間差,A機器先丟了inplay,B機器丟了pregame,這時必須拋棄pregame
        02=>cache 0 + match 2 已經cache 0 inplay 又接到2 pregame 不正常順序 返回False

        Args:
            game_id (str): 5461455
            game_status (str): 0,1,2,3,4

        Returns:
            bool: True, False
        """
        try:
            result = True
            if game_id not in self.status_cache:
                self.status_cache[game_id] = game_status
            else:
                match_status = game_status
                cache_status = self.status_cache[game_id]
                if match_status != cache_status:
                    if cache_status + match_status in ["02", "10", "12", "30", "32", "40", "42"]:
                        result = False
                    else:
                        self.status_cache[game_id] = game_status
            return result
        except:
            msg = f"game_id: {game_id}, game_status: {game_status}"
            self.send_msg(msg=msg)
            return False


    def wait(self, name, sleep_time):
        """依據 name 來判斷是否有超過 sleep_time
        Args:
            name (str): "2H", "3M" 等待的時間名稱  當KEY來使用  不要重複即可
            sleep_time (int): 7200, 180 name所要等待的秒數

        Returns:
            bool: True, False 是否超過等待的時間就
        """
        run = False
        now = time.time()
        time_diff = now - self.time_cache[name]
        if time_diff > sleep_time:
            run = True
            self.time_cache[name] = now
        return run


    def remove_not_HA_OU(self, match, now):
        """因為會有多天的資料,要把"2天"以後的賠率資料只保留HAOU即可,其餘刪除
        今天跟明天會有所有賠率,後天以後只有HAOU(現在4/1==>4/1~4/3全送, 4/4只送HAOU)
        """
        try:
            dct = match.odds
            if not dct: return
            game_date = match.game_date
            if not game_date: return
            game_date_time = datetime.strptime(game_date, "%Y-%m-%d")
            if (game_date_time-now).days >=2:
                for play_mode in list(dct.keys()):
                    if play_mode not in ["HA", "OU"]:
                        dct.pop(play_mode, None)
        except:
            self.send_msg()


    def check_each_cache(self):
        """當賠率是由多個頁面組成時,如果某個頁面超過3分鐘都沒接到,就將那一頁的賠率給空 由後續去關閉
        Returns:
            list: [match]
        """
        now = time.time()
        inplay_setting_time = 180
        not_inplay_setting_time = 600
        need_close = []
        if self.wait("3M", 180):
            for cache_id, cache in self.each_cache.items():
                if cache.game_status == "0":
                    if now - cache.receive_time >= inplay_setting_time:
                        new = copy.deepcopy(cache)
                        new.odds = {}
                        need_close.append(new)
                        self.each_game_id.add(cache_id)
                else:
                    if now - cache.receive_time >= not_inplay_setting_time:
                        new = copy.deepcopy(cache)
                        new.odds = {}
                        need_close.append(new)
                        self.each_game_id.add(cache_id)

            for merge_id, merge in self.merge_dct.items():
                if merge.game_status == "0":
                    if now - merge.receive_time >= inplay_setting_time:
                        self.merge_id.add(merge_id)
                else:
                    if now - merge.receive_time >= not_inplay_setting_time:
                        self.merge_id.add(merge_id)

        return need_close


