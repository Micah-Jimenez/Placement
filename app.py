from flask import Flask, render_template, request, redirect, jsonify, session
from datetime import datetime
import urllib.parse
import requests
import random
from threading import Thread


app = Flask(__name__)
app.secret_key = "dev"
 

CLIENT_ID = "18c79a90b0a647009e6a2c6141a152bb"
CLIENT_SECRET = "f1254334aca24b86a82cd67c6670c294"
REDIRECT_URI = "http://localhost:5000/callback"

AUTH_URL = "https://accounts.spotify.com/authorize"
TOKEN_URL = "https://accounts.spotify.com/api/token"
API_BASE_URL = "https://api.spotify.com/v1/"

USER_PLAYLISTS = []
CAN_RUN = False
FINAL_RESULT = []

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/login")
def login():
    scope = "user-read-private user-read-email"

    params = {
        "client_id": CLIENT_ID,
        "response_type": "code",
        "scope": scope,
        "redirect_uri": REDIRECT_URI,
        "show_dialog": True,
    }

    auth_url = f"{AUTH_URL}?{urllib.parse.urlencode(params)}"
    return redirect(auth_url)


@app.route("/callback")
def callback():
    if "error" in request.args:
        return redirect("/")
    
    if "code" in request.args:
        req_body = {
            "code": request.args["code"],
            "grant_type": "authorization_code",
            "redirect_uri": REDIRECT_URI,
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
        }

        response = requests.post(TOKEN_URL, data=req_body)
        token_info = response.json()

        session["access_token"] = token_info["access_token"]
        session["refresh_token"] = token_info["refresh_token"]
        session["expires_at"] = datetime.now().timestamp() + token_info["expires_in"]

        return redirect("/playlists")


@app.route("/playlists", methods=["GET", "POST"])
def get_playlist():
    if "access_token" not in session:
        return redirect("/login")
    elif datetime.now().timestamp() > session["expires_at"]:
        return redirect("/refresh_token")
    else:
        if request.method == "POST":
            song_input = get_song_genres()
            if song_input == 1:
                global FINAL_RESULT
                FINAL_RESULT.append("ERROR: Couldn't find song placement due to lack of data")
                return ('', 204)
            
            while True:
                if CAN_RUN:
                    FINAL_RESULT = get_song_placement(USER_PLAYLISTS, song_input)
                    break

            return ('', 204)
        else:
            Thread(target=get_users_playlists_genres, args=[50, session["access_token"]]).start()
            return render_template("finder.html", answer='')
        

@app.route("/refresh_token")
def refresh_token():
    if not session["refresh_token"]:
         return redirect("/login")
    elif datetime.now().timestamp() > session["expires_at"]:
        req_body = {
            "grant_type": "refresh_token",
            "refresh_token": session["refresh_token"],
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
        }

        response = requests.post(TOKEN_URL, data=req_body)
        new_token_info = response.json()
        session["access_token"] = new_token_info["access_token"]
        session["expires_at"] = datetime.now().timestamp() + new_token_info["expires_in"]

        return redirect("/playlists")
    
@app.route("/add")
def add():
    global FINAL_RESULT
    while True:
        if len(FINAL_RESULT) != 0:
            result = FINAL_RESULT
            FINAL_RESULT = []
            return jsonify(result)
    

def get_song_genres():            
    form_song = clean_input(request.form.get("song"))
    form_artist = clean_input(request.form.get("artist"))

    headers = {
        "Authorization": f'Bearer {session["access_token"]}',
    }
    track_response = requests.get(API_BASE_URL + f"search?q=artist:{form_artist}%20track:{form_song}&type=track", headers=headers)
    track = track_response.json()
    if track["tracks"]["items"]:
        artist_id = track["tracks"]["items"][0]["album"]["artists"][0]["id"]
    else: return 1 

    artist_response = requests.get(API_BASE_URL + f"artists/{artist_id}", headers=headers)
    artist = artist_response.json()
    genres = []

    for entry in artist["genres"]:
        genres.append(entry)

    if len(genres) == 0:
        return 1
    else:
        return genres


def get_users_playlists_genres(n, token):
    if n < 1 or n > 50:
        limit = 20
    else:
        limit = n

    headers = {
        "Authorization": f'Bearer {token}',
    }
    user_playlists_response = requests.get(API_BASE_URL + "me/playlists", headers=headers).json()
    user_playlists = user_playlists_response["items"]
    playlists = []


    for i in range(len(user_playlists)):
        track_genres = []

        while len(track_genres) == 0:
            track_count = int(user_playlists[i]["tracks"]["total"])

            if track_count >= limit:
                upper_limit = track_count - limit
                loop_limit = limit
            else:
                upper_limit = 0
                loop_limit = track_count

            offset = random.randint(0, abs(upper_limit))
            playlist_href = user_playlists[i]["tracks"]["href"]
            playlist_response = requests.get(playlist_href+f"?limit={limit}&offset={offset}", headers=headers).json()
            playlist_response = playlist_response["items"]
            name = user_playlists[i]["name"]
            ids = []
            for j in range(loop_limit):
                curr_artist_id = playlist_response[j]["track"]["album"]["artists"][0]["id"]
                ids.append(curr_artist_id)

            ids = ",".join(ids)
            artist_response = requests.get(API_BASE_URL + f"artists?ids={ids}", headers=headers)
            artist = artist_response.json()

            for j in range(loop_limit):
                artist_genres = artist["artists"][j]["genres"]

                for genre in artist_genres:
                    if genre not in track_genres:
                        track_genres.append(genre)

            if len(track_genres) > 0:
                playlists.append({name: sorted(track_genres)})

    global USER_PLAYLISTS
    global CAN_RUN
    USER_PLAYLISTS = playlists
    CAN_RUN = True
    return


def get_song_placement(playlist, song):
    totals = []
    for i in range(len(song)):
        for count, playlist_genre in enumerate(playlist):
            try:
                x = totals[count]
            except IndexError:
                totals.append(0)

            playlist_values = list(playlist_genre.values())
            if song[i] in playlist_values[0]:
                totals[count]+= 1

    result = []
    top = max(totals)

    if top == 0:
        new_songs = split_text(song)
        for i in range(len(new_songs)):
            for count, playlist_genre in enumerate(playlist):
                playlist_values = list(playlist_genre.values())
                playlist_values = split_text(playlist_values[0])
                if new_songs[i] in playlist_values:
                    totals[count]+= 1

        top = max(totals)

    for j in range(len(totals)):
        if totals[j] == top:
            result.append(list(playlist[j].keys())[0])

    if len(result) > 3:
        return result[:3]
    return result


def split_text(arr):
    new_songs = []

    for element in arr:
        new_genres = element.split()
        for genre in new_genres:
            if genre not in new_songs:
                new_songs.append(genre)
    return new_songs


def clean_input(input):
    return input.lower().strip().replace("'", "")


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)