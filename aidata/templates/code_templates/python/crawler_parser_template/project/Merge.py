import copy
from collections import defaultdict
import json

class Merge(object):
    def __init__(self, send_msg):
        self.send_msg = send_msg
        self.change_status = {}
        self.send_close_count = defaultdict(int)


    def merge(self, merge_dct, match, new_odd):
        """
        將不同頁面的資料作合併
        merge_dct => 字典: key為gagme_id, value為 match物件
        match => 物件
        new_odd =>1.全新的賠率 2.經過Compair得到的新賠率(會有關閉的賠率)
        Args:
            merge_dct (dict): {'123': Match(league_id='NBA', league='NBA', team_home_id='道奇', team_home='道奇', team_away_id='紅襪', team_away='紅襪', game_date='2023-03-29', game_time='10:20', game_id='123', score_home='6', score_away='8', scores=[[0, 0]], game_status='1', double_header='N', playbyplay='', ResultInfo='', OtherInfo='', game_mode='Unknown', game_type='BS', need_send=False, score_count=0, send_time=1680142303.695221, receive_time=1680142303.6942213, odds={'RBHA': {'3': {'H': '0.5', 'A': '0.6'}}}, site='', country_code='', page_name='ha', only_merge=False)}
            match (obj): Match(league_id='CPBL', league='CPBL', team_home_id='統一', team_home='統一', team_away_id='兄弟', team_away='兄弟', game_date='2023-03-29', game_time='08:00', game_id='cpbl123', score_home='2', score_away='0', scores=[[0, 0], [2, 0]], game_status='1', double_header='N', playbyplay='', ResultInfo='', OtherInfo='', game_mode='Unknown', game_type='BS', need_send=False, score_count=0, send_time=0, receive_time=1680142303.6962252, odds={}, site='', country_code='', page_name='', only_merge=False)
            new_odd (dict): {'RBHA': {'4': {'H': '-1', 'A': '-1'}, '3': {'H': '0.5', 'A': '0.6'}}}
        """
        try:
            cache_data = ""
            game_id = match.game_id
            if game_id not in merge_dct:
                merge_dct[game_id] = copy.deepcopy(match)
            else:
                if game_id not in merge_dct: return
                if match.game_status != merge_dct[game_id].game_status:
                    merge_dct[game_id].odds = {}
                    merge_dct[game_id].score_home = match.score_home
                    merge_dct[game_id].score_away = match.score_away
                self.remove_close(merge_dct[game_id].odds, game_id)
                cache_data = merge_dct[game_id]
                if match.receive_time: cache_data.receive_time = match.receive_time
                if match.league_id: cache_data.league_id = match.league_id
                if match.league: cache_data.league = match.league
                if match.team_home_id: cache_data.team_home_id = match.team_home_id
                if match.team_home: cache_data.team_home = match.team_home
                if match.team_away_id: cache_data.team_away_id = match.team_away_id
                if match.team_away: cache_data.team_away = match.team_away
                if match.game_date: cache_data.game_date = match.game_date
                if match.game_time: cache_data.game_time = match.game_time
                if match.playbyplay: cache_data.playbyplay = match.playbyplay
                if match.game_type: cache_data.game_type = match.game_type
                if match.game_status: cache_data.game_status = match.game_status
                if match.ResultInfo: cache_data.ResultInfo = match.ResultInfo
                if match.OtherInfo: self.update_otherinfo(cache_data, match)
                # if match.game_status != "2": cache_data.OtherInfo = ""
                cache_data.odds = self.update_odds(cache_data.odds, new_odd)
                if cache_data.game_status == "0" and match.scores != []:
                    self.update_tesm_score(cache_data, match)
                    self.update_scores(cache_data, match)
                else:
                    if match.score_home and match.score_home != "-1": cache_data.score_home = match.score_home
                    if match.score_away and match.score_away != "-1": cache_data.score_away = match.score_away
                    if match.scores: cache_data.scores = match.scores
        except:
            msg = f"match: {match}, cache_data: {cache_data}"
            self.send_msg(msg=msg)

    def update_otherinfo(self, cache_data, match):
        #快取沒寫過就直接寫進去
        if cache_data.OtherInfo == '':
            cache_data.OtherInfo = match.OtherInfo
        elif cache_data.OtherInfo == match.OtherInfo:
            #跟快取的資料一樣就不做事情
            return
        else:
            #otherinfo有變化，就更新快取
            cache_data_dict = json.loads(cache_data.OtherInfo)
            match_data_dict = json.loads(match.OtherInfo)
            cache_data_dict.update(match_data_dict)
            cache_data.OtherInfo = json.dumps(cache_data_dict, ensure_ascii=False)

    def update_odds(self, cache_odd_data, new_odd):
        """舊的賠率保留,新的賠率加到cache裡面
        Args:
            cache_odd_data (dict): {'RBHA': {'2': {'H': '2.5', 'A': '2.6'}}}
            new_odd (dict): {'RBHA': {'4': {'H': '-1', 'A': '-1'}, '3': {'H': '3.5', 'A': '3.6'}}}

        Returns:
            dict: {'RBHA': {'2': {'H': '2.5', 'A': '2.6'}, '4': {'H': '-1', 'A': '-1'}, '3': {'H': '3.5', 'A': '3.6'}}}
        """
        new_odd = copy.deepcopy(new_odd)
        for play_mode, odd_datas in new_odd.items():
            if play_mode not in cache_odd_data:
                cache_odd_data[play_mode] = odd_datas
            else:
                for spread, price in odd_datas.items():
                    if spread in cache_odd_data[play_mode]:
                        cache_odd_data[play_mode][spread]=price
                    else:
                        for spread, price in odd_datas.items():
                            if spread in cache_odd_data[play_mode]:
                                cache_odd_data[play_mode][spread]=price
                            else:
                                cache_odd_data[play_mode].update(odd_datas)
        return cache_odd_data


    def update_tesm_score(self, merge_dct, match):
        if match.score_home != "-1" and  match.score_away != "-1":
            if (int(match.score_home) < int(merge_dct.score_home) or int(match.score_away) < int(merge_dct.score_away)):
                merge_dct.score_count = merge_dct.score_count + 1
                if merge_dct.score_count > 3:
                    merge_dct.score_home = match.score_home
                    merge_dct.score_away = match.score_away
                    merge_dct.score_count = 0
            else:
                merge_dct.score_count = 0
                merge_dct.score_home = match.score_home
                merge_dct.score_away = match.score_away


    def update_scores(self, merge_dct, match):
        if merge_dct.score_count == 0:
            merge_dct.scores = match.scores


    def remove_close(self, cache_odd, game_id):
        """賠率-1只有在第一次關閉時要送,之後就不要再送,所以要移除

        Args:
            dct (dict): {'OU': {'10.5': {'O': '0.5', 'U': '0.8', 'O-Spread': '10.5'}, '7.5': {'O': '-1', 'U': '-1', 'O-Spread': '7.5'}}, 'Others-Correct Score': {'3-0': {'Value': '-1','O-Spread': '3-1'}}}

        Returns:
            dict: {'OU': {'10.5': {'O': '0.5', 'U': '0.8', 'O-Spread': '10.5'}}}
        """
        try:
            for play_mode, price in dict(cache_odd).items():
                if all([set(odd.values())=={"-1"} for odd in price.values()]):
                    if self.send_close_count[game_id] >= 4:
                        cache_odd.pop(play_mode, None)
                        self.send_close_count.pop(game_id, None)
                    else:
                        self.send_close_count[game_id] += 1
                else:
                    for spread, odd in dict(price).items():
                        if set(odd.values()) == {"-1"}:
                            cache_odd[play_mode].pop(spread, None)
        except:
            self.send_msg()
