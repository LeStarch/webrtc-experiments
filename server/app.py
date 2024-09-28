from flask import Flask
from flask import request

def create_app():
    """ Create the flask application """
    offers_db = {}
    ice_db = {}

    app = Flask(__name__, static_url_path="", static_folder="../html", instance_relative_config=True)

    @app.before_request
    def log_request():
        pass
        #print(request.headers)
        #print(request.get_data())

    @app.route("/")
    def index():
        """ Specifically handle the index.html """
        return app.send_static_file("index.html")

    @app.route("/offers", methods=("GET", ))
    def get_offers():
        """ GET to see current offers """
        return {
            "status": "Yehaw",
            "offers": [{
                    "label": data["label"], "offerer": offerer, "offer": data["offer"]
                } for offerer, data in offers_db.items()]
        }, 200

    @app.route("/answer/<offerer>", methods=("GET", ))
    def get_answer(offerer):
        """ GET to see current offers """
        answer = offers_db.get(offerer, {}).get("answer", None)
        answerer = offers_db.get(offerer, {}).get("answerer", None)

        if answer is None or answerer is None:
            return {"status": "No answer available"}, 200
        return {
            "status": "Yehaw",
            "answer": answer,
            "answerer": answerer
        }, 200

    @app.route("/make-offer", methods=("POST",))
    def make_offer():
        """ POST to handle a client making an offer """
        offer_package = request.get_json()
        offerer = offer_package.get("offerer", None)
        offer = offer_package.get("offer", None)
        label = offer_package.get("label", None)
        ice_db[offerer] = []
        if offerer is None or offer is None or label is None:
            return {"status": "Offer must supply 'label', 'offerer' and 'offer' data"}, 500
        offers_db[offerer] = {"offer": offer, "label": label, "answer": None, "answerer": None}
        return {"status": "Yehaw"}, 200

    @app.route("/make-answer", methods=("POST",))
    def make_answer():
        """ POST to handle a client making an offer """
        answer_package = request.get_json()
        offerer = answer_package.get("offerer", None)
        answer = answer_package.get("answer", None)
        answerer = answer_package.get("answerer", None)

        if offerer is None or answer is None or answerer is None:
            return {"status": "Answer must supply 'answerer', 'offerer', and 'answer' data"}, 500
        offers_db[offerer].update({"answer": answer, "answerer": answerer})
        return {"status": "Yehaw"}, 200

    @app.route("/ice/<ice_id>", methods=("POST", "GET"))
    def ice(ice_id):
        """ POST and GET ICE coordination requests """
        if request.method == "GET":
            return {"status": "Yehaw", "messages": ice_db.get(ice_id, [])}, 200
        elif request.method == "POST":
            candidate = request.get_json()
            ice_db[ice_id] = ice_db.get(ice_id, [])
            ice_db[ice_id].append(candidate)
            return {"status": "Yehaw"}, 200
    return app
