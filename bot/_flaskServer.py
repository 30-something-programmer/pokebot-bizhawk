
def httpServer(self):
    """Run Flask server to make bot data available via HTTP GET"""
    import flask
    from flask import Flask, abort, jsonify, make_response, url_for, redirect, request
    try:
        self.logger.info("Running HTTP server")
        server = Flask(__name__, static_folder=self.interface_folder)
        self.CORS(server)

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
            trainer = self.GetTrainer()
            if trainer:
                return jsonify(trainer)
            self.abort(503)

        @server.route("/bag", methods=["GET"])
        def Bag():
            bag = self.GetBag()
            if bag:
                return jsonify(bag)
            self.abort(503)

        @server.route("/party", methods=["GET"])
        def Party():
            party = self.GetParty()
            if party:
                return jsonify(party)
            self.abort(503)

        @server.route("/encounter", methods=["GET"])
        def Encounter():
            encounter_logs = self.GetEncounterLog()["encounter_log"]
            if len(encounter_logs) > 0 and encounter_logs[-1]["pokemon_obj"]:
                encounter = encounter_logs.pop()["pokemon_obj"]
                stats = self.GetStats()
                if stats:
                    try:
                        encounter["stats"] = stats["pokemon"][encounter["name"]]
                        return jsonify(encounter)
                    except:
                        self.abort(503)
                return jsonify(encounter)
            self.abort(503)

        @server.route("/encounter_rate", methods=["GET"])
        def EncounterRate():
            try:
                return jsonify({"encounter_rate": self.GetEncounterRate()})
            except:
                return jsonify({"encounter_rate": "-"})
            abort(503)

        @server.route("/emu", methods=["GET"])
        def Emu():
            emu = self.GetEmu()
            if emu:
                return jsonify(emu)
            self.abort(503)

        @server.route("/stats", methods=["GET"])
        
        def Stats():
            stats = self.GetStats()
            if stats:
                return jsonify(stats)
            self.abort(503)

        @server.route("/encounter_log", methods=["GET"])
        def EncounterLog():
            recent_encounter_log = self.GetEncounterLog()["encounter_log"][-25:]
            if recent_encounter_log:
                encounter_log = {"encounter_log": recent_encounter_log}
                return jsonify(encounter_log)
            self.abort(503)

        @server.route("/shiny_log", methods=["GET"])
        def ShinyLog():
            shiny_log = self.GetShinyLog()
            if shiny_log:
                return jsonify(shiny_log)
            self.abort(503)

        # TODO Missing route_list
        # @server.route("/routes", methods=["GET"])
        # def Routes():
        #     if route_list:
        #         return route_list
        #     else:
        #         abort(503)

        @server.route("/pokedex", methods=["GET"])
        def Pokedex():
            if self.PokedexList:
                return self.PokedexList
            self.abort(503)

        # @server.route("/config", methods=["POST"])
        # def Config():
        #    response = jsonify({})
        #    return response

        @server.route("/updateblocklist", methods=["POST"])
        def UpdateBlockList():
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
        def Blocked():
            block_list = self.GetBlockList()
            return block_list

        @server.route("/screenshot.png", methods=["GET"])
        def Screenshot():
            screenshot = self.GetScreenshot()
            if screenshot.any():
                buffer = self.cv2.imencode('.png', screenshot)[1]
                response = make_response(buffer.tobytes())
                response.headers['Content-Type'] = 'image/png'
                return response
            self.abort(503)

        server.run(debug=False, threaded=True, host=self.config["server"]["ip"], port=self.config["server"]["port"])
    except Exception as e:
        self.logger.error("Hit an error in _flaskServer.py:")
        self.logger.error(str(e))
