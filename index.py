from flask import Flask, redirect, render_template, request
from drawFans import *
import os, time, random

app = Flask(__name__)


@app.route("/")
def index():
    saveLog(0, 0)
    return render_template("aya.html")


@app.route("/log")
def log():
    return render_template("log.html")


def saveLog(x, uid):
    userIP = request.remote_addr
    os.chdir("/home/aya/serverFans/templates/")
    his = ["index", "view", "force", "error", "aya", "ip", "kemo"]
    tTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
    with open("log.html", "a+") as f:
        f.write(f"{his[x]}, {uid}, {userIP}, {tTime} <br>\n")


# @app.route("/search")
# def search():
#    saveLog(6)
#    return render_template("search.html")


@app.route("/uid<uid>")
def userInfo(uid):
    if os.path.exists(uid):
        saveLog(1, uid)
        return render_template(f"{uid}/index.html")
    if n > 19:
        saveLog(3, uid)
        return render_template("ayaerror.html")
    return reflashInfo(uid)


@app.route("/f<uid>")
def reflashInfo(uid):
    if not uid.isnumeric():
        return "Null"
    global n
    n += 1
    os.chdir("/home/aya/serverFans/templates/")
    if n > 20:
        saveLog(3, uid)
        return render_template("ayaerror.html")
    saveLog(2, uid)
    # try:
    Spyder(uid).run()
    return render_template(f"{uid}/index.html")
    # except:
    #    return "Failed"


@app.route("/aya<uid>")
def forceInfo(uid):
    saveLog(4, uid)
    os.chdir("/home/aya/serverFans/templates/")
    try:
        fans = drawFans.Spyder(uid)
        fans.run()
        return render_template(f"{uid}/index.html")
    except:
        return "Failed"


@app.route("/reset")
def reset():
    global n
    n = 0
    return "Reseted!"


@app.route("/times")
def times():
    return {"Times": 20 - n, "Proxy": Proxy().t()}


@app.route("/ip")
def getIP():
    saveLog(5, 0)
    return {"IP": request.remote_addr}


@app.route("/kemo")
def kemo():
    saveLog(6, 0)
    return redirect(
        f"https://ayatale.coding.net/p/picbed/d/kemo/git/raw/master/{random.randint(1,549)}.jpg"
    )


if __name__ == "__main__":
    n = 0
    app.run(host="0.0.0.0", port=10, debug=0, threaded=0)

