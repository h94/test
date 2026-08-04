class Compair(object):
    def __init__(self, send_msg):
        self.send_msg = send_msg

    def compair_odd(self, cache, match, merge):
        """
        比對賽事狀態變化,有變化時值接送出新的賽事狀態的賠率(賽前變賽中, 直接送賽中的資料)
        比對賠率變化,相同玩法,不同球頭, 關閉cache(舊)的球頭,補上match(新)的球頭
            cache1 = {'HA': {'1+50': {'H': '6.9', 'A': '1.07'}}}
            match1 = {'HA': {'1X2': {'H': '1.77', 'T': '3', 'A': '4.6'}}}
            ans1 = {'HA': {'1X2': {'H': '1.77', 'T': '3', 'A': '4.6'},'1+50': {'H': '-1', 'A': '-1'}}}
        """
        try:
            if match.game_status != cache.game_status:
                return match.odds
            cache_odds = cache.odds
            match_odds = match.odds
            merge_odds = merge.odds if merge else {}
            new_odd = self.get_new_odd(cache_odds, match_odds, merge_odds)
            return new_odd
        except:
            msg = f"cache: {cache}, match: {match}, merge: {merge}"
            self.send_msg(msg=msg)
            return {}

    def get_new_odd(self, cache_odds, match_odds, merge_odds):
        """比對賠率變化 可看UT的範例
        """
        new_odd = {}
        only_one_play_mode = []
        for play_mode, spread_data in merge_odds.items():
            if play_mode not in match_odds:continue
            if len([spread for spread in spread_data.keys() if spread != "1X2"]) == 1:
                only_one_play_mode.append(play_mode)

        for play_mode in only_one_play_mode:
            merge_odds.pop(play_mode, None)

        for play_mode, spread_data in cache_odds.items():
            if play_mode not in match_odds:
                self.update(new_odd,{play_mode:self.close_odd(spread_data)})
            else:
                if play_mode not in only_one_play_mode:
                    for spread, odd_data in spread_data.items():
                        if spread not in match_odds[play_mode]:
                            self.update(new_odd,{play_mode:self.close_odd({spread:odd_data})})


        for play_mode, spread_data in match_odds.items():
            if play_mode not in cache_odds:
                self.update(new_odd,{play_mode:spread_data})
            else:
                for spread, odd_data in spread_data.items():
                    self.update(new_odd,{play_mode:{spread:odd_data}})
        return new_odd


    def close_odd(self, spread_data):
        """關閉不在cahhe的

        Args:
            spread_data (dict): {'9.5': {'O': '1.74', 'U': '1.98', 'O-Spread': '9.5'}}

        Returns:
            dict: {'9.5': {'O': '-1', 'U': '-1', 'O-Spread': '9.5'}}
        """
        try:
            close = {}
            for spread, odd_value in spread_data.items():
                close[spread] = {key:"-1" if key!= "O-Spread" else value for key, value in odd_value.items()}
            return close
        except:
            msg = f"spread_data: {spread_data}"
            self.send_msg(msg=msg)
            return {}


    def update(self, new_odd, match):
        """更新賠率,若是新的play_moded 直接新增整筆
           若play_moded已存在,新增或更新spread的值

        Args:
            新增play_moded
            new_odd (dict): {'OU': {'9.5': {'O': '1.74', 'U': '1.98', 'O-Spread': '9.5'}}}
            match (dict):   {'Others-Correct Score': {'3-0': {'Value': '9.0'}}}
            new_odd=>       {'OU': {'7.5': {'O': '1.23', 'U': '3.75', 'O-Spread': '7.5'}},'Others-Correct Score': {'3-0': {'Value': '9.0'}}}
            新增spread
            new_odd (dict): {'OU': {'9.5': {'O': '1.74', 'U': '1.98', 'O-Spread': '9.5'}}}
            match (dict):   {'OU': {'7.5': {'O': '1.23', 'U': '3.75', 'O-Spread': '7.5'}}}
            new_odd=>       {'OU': {'9.5': {'O': '1.74', 'U': '1.98', 'O-Spread': '9.5'}, '7.5': {'O': '1.23', 'U': '3.75', 'O-Spread': '7.5'}}}
            更新spread裡的賠率
            new_odd (dict): {'OU': {'9.5': {'O': '1.74', 'U': '1.98', 'O-Spread': '9.5'}}}
            match (dict):   {'OU': {'9.5': {'O': '9999', 'U': '8888', 'O-Spread': '9.5'}}}
            new_odd=>       {'OU': {'9.5': {'O': '9999', 'U': '8888', 'O-Spread': '9.5'}}}
        """
        try:
            for play_mode, spread_data in match.items():
                if play_mode in new_odd:
                    new_odd[play_mode].update(spread_data)
                else:
                    new_odd.update({play_mode:spread_data})
        except:
            msg = f"new_odd: {new_odd}, match: {match}"
            self.send_msg(msg=msg)