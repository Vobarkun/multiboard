import requests, base64, json, re, sys
from datetime import datetime

def getGames():
    response = requests.get("https://www.chessbomb.com/arena/")
    source = response.text
    source = source[source.find("cbConfigData") + len('cbConfigData="'):]
    source = source[:source.find('"')]
    data = json.loads(base64.b64decode(source).decode("utf-8"))

    events = []
    weights = []
    for room in data["indexData"]["rooms"]:
        d = datetime.strptime(room["endAt"], "%Y-%m-%dT%H:%M:%S.%fZ")
        if d > datetime.now():
            events.append(room["slug"])
            weights.append(room["weight"])

    perm = list(range(0, len(events)))
    perm.sort(key=lambda i:weights[i],reverse=True)    
    events = [events[p] for p in perm]

    paths = []
    for event in events:
        try: 
            response = requests.get("https://www.chessbomb.com/arena/" + event)
            source = response.text
            source = source[source.find("cbConfigData") + len('cbConfigData="'):]
            source = source[:source.find('"')]
            data = json.loads(base64.b64decode(source).decode("utf-8"))
            games = data["roomData"]["games"]
            mr = 0
            for game in games:
                r = int(re.sub("\D", "", game["roundSlug"]))
                if r > mr:
                    mr = r
            games = [game for game in games if int(re.sub("\D", "", game["roundSlug"])) == mr or game["result"] == "*"]
            games = sorted(games, key=(lambda j: int(j["board"])))
            paths.append([event + "/" + game["roundSlug"] + "-" + game["slug"] for game in games])
            print(str(event) + ": " + str(len(games)) + " games added")
        except Exception as e:
            print(event, e)

    # with open("paths.js", "w") as f:
    #     f.write("paths = " + repr(paths) + ";")
    return "paths = " + repr(paths) + ";"


from bottle import route, static_file, run, response

@route("/")
def mainsite():
    return static_file("chessbomb.html", "")

@route('/paths.js')
def paths():
    response.content_type = 'text/javascript; charset=utf8'
    return getGames()

run(host='0.0.0.0', port=10001)
