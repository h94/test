from TCZB import Globals
import threading
import queue
import time

class NameMapService(object):
    def __init__(self, provider, source, send_msg):
        self.provider = provider
        self.source = source
        self.send_msg = send_msg
        self.namemap_url = Globals.Globals.CrawlerData["namemap_url"]
        self.name_map_cache = {}
        self.run_time = time.time()
        self.save_lang = queue.Queue()


    def name_map_service(self, matches):
        now = time.time()
        for match in matches:
            match.site = self.source
            cache_key = f"{match.country_code}{match.game_type}{match.league_id}{match.team_home_id}{match.team_away_id}"
            if cache_key not in self.name_map_cache:
                self.name_map_cache[cache_key] = now
                self.save_lang.put(match.change_namemap())
        if self.need_run(now):
            send_lang = []
            while not self.save_lang.empty():
                send_lang+=self.save_lang.get()
            if send_lang:
                threading.Thread(target=self.provider.requests_data, kwargs={"url":self.namemap_url, "method": "post", "post_data": send_lang}).start()
            msg = f"send name map in the last minute, length is {len(send_lang)}"
            self.send_msg(msg=msg, level="Information")
            self.remove_cache(now)


    def remove_cache(self, now):
        try:
            need_remove = set()
            for cache_key, cache_time in self.name_map_cache.items():
                if now-cache_time >= 172800:
                    need_remove.add(cache_key)
            for remove_key in need_remove:
                self.name_map_cache.pop(remove_key, None)
        except:
            self.send_msg()


    def need_run(self, now):
        need_run = False
        if now - self.run_time > 300:
            self.run_time = now
            need_run = True
        return need_run