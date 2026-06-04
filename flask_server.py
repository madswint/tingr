from flask import Flask, render_template, request, redirect
from database import init_db
import main

init_db()
main.load_all_politicians()

app = Flask(__name__)


@app.route("/")
def starter():
    politicians = main.get_random_politicians(3)
    return render_template("starter.html", politicians=politicians)


@app.route("/choose", methods=["POST"])
def choose():
    politician_id = request.form.get("politician_id", type=int)
    if politician_id is not None:
        politician = next((p for p in main.politicians if p.id == politician_id), None)
        if politician:
            main.reset()
            main.swiped.append(politician)
            main.bag_add(politician)
    return redirect("/swipe")


@app.route("/swipe")
def swipe_page():
    politician = main.get_next_politician()
    news = main.fetch_news(politician.name) if politician else []
    return render_template("index.html", politician=politician, bag=main.bag, news=news)


@app.route("/swipe", methods=["POST"])
def swipe():
    politician_id = request.form.get("politician_id", type=int)
    direction = request.form.get("direction")
    if politician_id is not None:
        politician = next((p for p in main.politicians if p.id == politician_id), None)
        if politician:
            main.swiped.append(politician)
            if direction == "right":
                main.bag_add(politician)
    return redirect("/swipe")


@app.route("/bag/remove", methods=["POST"])
def bag_remove():
    politician_id = request.form.get("politician_id", type=int)
    if politician_id is not None:
        politician = next((p for p in main.bag if p.id == politician_id), None)
        if politician:
            main.bag.remove(politician)
                                        # originally placed politician bag into pool if removed from bag but removed this - reconsider?
            if main.bag:
                main.bag_update_score()
    return redirect("/swipe")


@app.route("/results")
def results():
    stats = main.build_end_stats()
    return render_template("results.html",
        bag=stats["bag"],
        top_party=stats["top_party"],
        party_color=stats["party_color"],
        party_logo=stats["party_logo"],
        swiped_right=stats["swiped_right"],
        swiped_left=stats["swiped_left"],
        total_swiped=stats["total_swiped"],
        like_rate=stats["like_rate"],
        avg_attendance=stats["avg_attendance"],
        scandals_total=stats["scandals_total"],
        most_scandalous=stats["most_scandalous"],
        axis_fordeling=stats["axis_fordeling"],
        axis_vaerdi=stats["axis_vaerdi"],
    )

@app.route("/reset")
def reset():
    main.reset()
    return redirect("/")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
