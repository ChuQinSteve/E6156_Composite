from flask import Flask, Response, session, abort, redirect, request
import requests
import os

app = Flask("Composite Service")

@app.route("/comments/create", methods=["POST"])
def create_comment():
    # check request type
    content_type = request.headers.get('Content-Type')
    if (content_type != 'application/json'):
        return Response('Content-Type Not Supported', status=400, content_type="text/plain")
    
    # get request body
    body = request.json

    # if there is no user id or song id, return 400
    if body["uid"] is None or body["sid"] is None:
        return Response("Invalid Request", status=400, content_type="text/plain")

    # check if the user id and user name are valid
    url = "https://" + target + "/users/query/" + str(body["uid"])
    resp = requests.get(url)

    if resp.status_code == 200:
        resp = resp.json()
        if resp['id'] != body['uid'] or resp['username'] != body['username']:
            return Response("Invalid Request", status=400, content_type="text/plain")
    else:
        return Response("Invalid Request", status=400, content_type="text/plain")

    # check if the song id are valid
    url = "https://" + target + "/songs/query/" + str(body["sid"])
    resp = requests.get(url)

    if resp.status_code == 200:
        resp = resp.json()
        if resp['sid'] != body['sid']:
            return Response("Invalid Request", status=400, content_type="text/plain")
    else:
        return Response("Invalid Request", status=400, content_type="text/plain")

    # save the comment to the database
    url = "https://" + target + "/comments/create"
    resp = requests.post(url, json=body)

    return Response("Create Successfully", status=200, content_type="text/plain")

@app.route("/songs/delete/<sid>", methods=["POST"])
def update_song(sid):
    # check request type
    content_type = request.headers.get('Content-Type')
    if (content_type != 'application/json'):
        return Response('Content-Type Not Supported', status=400, content_type="text/plain")

    # delete the songs to the database
    url = "https://" + target + "/songs/delete/" + sid
    resp = requests.post(url, json=())
    if resp.status_code != 200:
        return Response("Invalid Request", status=400, content_type="text/plain")

    # delete the comments in the database
    url = "https://" + target + "/comments/delete/" + sid
    resp = requests.post(url, json=())
    if resp.status_code != 200:
        return Response("Invalid Request", status=400, content_type="text/plain")

    # delete the song in the database
    url = "https://" + target + "/collections/delete/" + sid
    resp = requests.post(url, json=())
    if resp.status_code != 200:
        return Response("Invalid Request", status=400, content_type="text/plain")

    return Response("Delete Successfully", status=200, content_type="text/plain")

if __name__ == "__main__":
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", 5000))
    target = os.environ.get("TARGET")
    app.run(host, port)