import time
from datetime import datetime
from collections import defaultdict

class Heart_beat(object):
    def __init__(self, send_msg, site_type):
        self.send_msg = send_msg
        self.site_type = site_type  #Appsetting設置scor或odd,沒有賠率的比分站台用score, 有賠率的用odd
        self.running_time = time.time()


    def heart_beat(self, merge):
        """整理需要送出去的資料
        1.change_datas 有變動的資料  一律送
        下面234都是沒有變動的資料 為了讓後續的服務判定賽事還存在 必須強制送出去的資料
        2.result_force_beat 已結束,或取消的賽事資料 會強制送10次 之後不再送
        3.pregame_force_beat  賽前的賽事資料 會一直送值到超過10分鐘都沒資料
        4.inplay_force_beat   進行中的賽事資料 會一直送值到超過10分鐘都沒資料

        Args:
            merge (dict): 將3個組合
        """
        now = time.time()
        datetime_now = datetime.now()
        run_heart_beat = self.run_heart_beat()
        change_datas = defaultdict(list)
        result_force_beat = defaultdict(list)
        pregame_force_beat = defaultdict(list)
        inplay_force_beat = defaultdict(list)
        for cache_data in merge.values():
            cache_game_status = cache_data.game_status
            try:
                if cache_data.need_send:
                    cache_data.need_send = False
                    cache_data.send_time = now
                    self.append_data(cache_data, change_datas, datetime_now, now)
                else:
                    if run_heart_beat:
                        last_send_time_diff = now - cache_data.send_time
                        last_receive_time_diff = now - cache_data.receive_time
                        if last_send_time_diff >= 55 and last_receive_time_diff <= 600:
                            if cache_game_status in ["0"]:
                                self.append_data(cache_data, inplay_force_beat, datetime_now, now)
                            elif cache_game_status in ["2"]:
                                if self.site_type == "score":
                                    pregame_force_len = sum([len(data) for data in pregame_force_beat.values()])
                                    if pregame_force_len == 0:
                                        self.append_data(cache_data, pregame_force_beat, datetime_now, now)
                                    else:
                                        if pregame_force_len <= 50 and last_send_time_diff >= 480:
                                            self.append_data(cache_data, pregame_force_beat, datetime_now, now)
                                else:
                                    self.append_data(cache_data, pregame_force_beat, datetime_now, now)

                            elif cache_game_status in ["1", "3", "4"] and cache_data.send_result_count < 10:
                                cache_data.send_result_count = cache_data.send_result_count +1
                                self.append_data(cache_data, result_force_beat, datetime_now, now)
            except:
                self.send_msg()
        send_data = defaultdict(list)
        for datas in [change_datas, result_force_beat, pregame_force_beat, inplay_force_beat]:
            for game_type, data in datas.items():
                send_data[game_type].extend(data)
        return send_data


    def append_data(self, cache_data, send_game, datetime_now, now):
        if not self.check_status(cache_data, datetime_now):return
        cache_data.send_time = now
        game_type = cache_data.game_type
        send_game[game_type].append(cache_data.change_match())


    def run_heart_beat(self):
        run = False
        now = time.time()
        if (now - self.running_time) > 60:
            run = True
            self.running_time = now
        return run


    def check_status(self, cache_data, datetime_now):
        need_send = False
        if all([cache_data.league,
                cache_data.league_id,
                cache_data.team_home,
                cache_data.team_home_id,
                cache_data.team_away,
                cache_data.team_away_id,
                cache_data.game_type,
                cache_data.game_date,
                cache_data.game_time,
                cache_data.score_home,
                cache_data.score_away,
                ]):
            if cache_data.game_status == "2":
                game_date_time = datetime.strptime(cache_data.game_date+cache_data.game_time, "%Y-%m-%d%H:%M")
                if game_date_time >= datetime_now:
                    need_send = True
            elif cache_data.game_status in ["1", "0"]:
                if cache_data.scores != [] or (cache_data.scores == [] and cache_data.score_home == "-1"):
                    need_send = True
            else:
                cache_data.odds = {}
                need_send = True
        return need_send