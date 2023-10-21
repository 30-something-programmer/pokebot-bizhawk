
import cv2

import logging

import flask
from flask import Flask, abort, jsonify, make_response, url_for, redirect, request
from flask_cors import CORS

from mmf.emu import GetEmu
from mmf.pokemon import GetParty
from mmf.screenshot import GetScreenshot
from mmf.trainer import GetTrainer
from mmf.bag import GetBag


def httpServer(self):
    """Run Flask server to make bot data available via HTTP GET"""
    try:
        log = logging.getLogger("werkzeug")
        log.setLevel(logging.ERROR)

        server = Flask(__name__, static_folder="./interface")
        CORS(server)

        @server.route("/")
        def Root():
            return redirect(url_for('Dashboard'))

        @server.route("/dashboard", methods=["GET"])
        def Dashboard():
            return flask.render_template("dashboard.html")

        @server.route("/dashboard/pokedex", methods=["GET"])
        def DashboardPokedex():
            return flask.render_template("pokedex.html")

        @server.route("/dashboard/debug", methods=["GET"])
        def DashboardDebug():
            return flask.render_template("debug.html")

        @server.route("/trainer", methods=["GET"])
        def Trainer():
            trainer = GetTrainer()
            if trainer:
                return jsonify(trainer)
            abort(503)

        @server.route("/bag", methods=["GET"])
        def Bag():
            bag = GetBag()
            if bag:
                return jsonify(bag)
            abort(503)

        @server.route("/party", methods=["GET"])
        def Party():
            party = GetParty()
            if party:
                return jsonify(party)
            abort(503)

        @server.route("/encounter", methods=["GET"])
        def Encounter(self):
            encounter_logs = self.GetEncounterLog()["encounter_log"]
            if len(encounter_logs) > 0 and encounter_logs[-1]["pokemon_obj"]:
                encounter = encounter_logs.pop()["pokemon_obj"]
                stats = self.GetStats()
                if stats:
                    try:
                        encounter["stats"] = stats["pokemon"][encounter["name"]]
                        return jsonify(encounter)
                    except:
                        abort(503)
                return jsonify(encounter)
            abort(503)

        @server.route("/encounter_rate", methods=["GET"])
        def EncounterRate(self):
            try:
                return jsonify({"encounter_rate": self.GetEncounterRate()})
            except:
                return jsonify({"encounter_rate": "-"})
            abort(503)

        @server.route("/emu", methods=["GET"])
        def Emu(self):
            emu = self.GetEmu()
            if emu:
                return jsonify(emu)
            abort(503)

        @server.route("/stats", methods=["GET"])
        def Stats(self):
            stats = self.GetStats()
            if stats:
                return jsonify(stats)
            abort(503)

        @server.route("/encounter_log", methods=["GET"])
        def EncounterLog(self):
            recent_encounter_log = self.GetEncounterLog()["encounter_log"][-25:]
            if recent_encounter_log:
                encounter_log = {"encounter_log": recent_encounter_log}
                return jsonify(encounter_log)
            abort(503)

        @server.route("/shiny_log", methods=["GET"])
        def ShinyLog(self):
            shiny_log = self.GetShinyLog(self)
            if shiny_log:
                return jsonify(shiny_log)
            abort(503)

        # TODO Missing route_list
        # @server.route("/routes", methods=["GET"])
        # def Routes():
        #     if route_list:
        #         return route_list
        #     else:
        #         abort(503)

        @server.route("/pokedex", methods=["GET"])
        def Pokedex(self):
            if self.PokedexList:
                return self.PokedexList
            abort(503)

        # @server.route("/config", methods=["POST"])
        # def Config():
        #    response = jsonify({})
        #    return response

        @server.route("/updateblocklist", methods=["POST"])
        def UpdateBlockList(self):
           data = request.json
           pkmName = data.get('pokemonName')
           sprite = data.get('spriteLoaded')
           catch = True
           if '-disabled' in sprite:
             catch = False
           else: catch = True
           self.BlockListManagement(pkmName, catch)
           return "OK", 200

        @server.route("/blocked", methods=["GET"])
        def Blocked(self):
            block_list = self.GetBlockList()
            return block_list

        @server.route("/screenshot.png", methods=["GET"])
        def Screenshot(self):
            screenshot = self.GetScreenshot()
            if screenshot.any():
                buffer = cv2.imencode('.png', screenshot)[1]
                response = make_response(buffer.tobytes())
                response.headers['Content-Type'] = 'image/png'
                return response
            abort(503)

        server.run(debug=False, threaded=True, host=self.config["server"]["ip"], port=self.config["server"]["port"])
    except Exception as e:
        log.debug(str(e))
