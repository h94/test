import time
from collections import defaultdict
import threading
from flask import Flask, render_template
from flask_socketio import SocketIO

class Debug(object):
    def __init__(self, send_msg, crawlerService):
        self.send_msg = send_msg
        self.crawlerService = crawlerService


    def main(self):
        app = Flask(__name__, template_folder=r'./templates')

        @app.route('/')
        def index():
            return render_template('display.html')

        socketio = SocketIO(app)
        threading.Thread(target=self.read_game_data, args=(socketio, )).start()
        socketio.run(app, debug=False)



    def read_game_data(self, socketio):
        cache = defaultdict(dict)
        while True:
            game_data = self.crawlerService.game_data_queue.get()
            gametype = game_data["gametype"]
            send_time = time.strftime("%H:%M:%S", time.localtime(game_data["send_time"]/1000))
            provider_name = game_data["provider_name"]
            for match in game_data["matches"]:
                cache[match["game_id"]] = {
                    "game_type": gametype,
                    "provider_name": provider_name,
                    "send_time": send_time,
                    "league": match["league"],
                    "team_home": match["team_home"],
                    "team_away": match["team_away"],
                    "game_date": match["game_date"],
                    "game_time": match["game_time"],
                    "game_id": match["game_id"],
                    "game_status": match["game_status"],
                    "score_home": match["score_home"],
                    "score_away": match["score_away"],
                    "scores": str(match["scores"]),
                    "playbyplay": match["playbyplay"],
                    "otherinfo": match["OtherInfo"],
                    "odds": "<br>".join(sorted([str(odd) for odd in match["odds"]]))
                }
            rows = [data for data in cache.values()]
            socketio.emit('update_data', {'rows': rows})