from flask import Flask, Response, Response, session, abort, redirect, request
import os
import requests
import requests
import os

app = Flask("Composite Service")

users_url = "http://" + os.environ.get("USERS_HOST")
collections_url = "http://" + os.environ.get("COLLECTIONS_HOST")
songs_url = "http://" + os.environ.get("SONGS_HOST")
comments_url = "http://" + os.environ.get("COMMENTS_HOST")

@app.route("/collections/create", methods=["post"])
def collections_create():
    content_type = request.headers.get('Content-Type')
    if (content_type != 'application/json'):
        return Response('Content-Type Not Supported', status=400, content_type="text/plain")

    # get request body
    body = request.json

    # check if song_id is a valid id in song and song name is a valid song name
    if ("sid" in body):
        sid = str(body["sid"])
        response = requests.get(songs_url + "/songs/query/sid/" + sid)
        print(response.text)
        if (response.status_code != 200):
            # error
            return Response("Get error from API Gateway", status=500, content_type="text/plain")
        else:
            # check if id is not found
            if (response.text == 'Not Found'):
                return Response("Invalid Song ID", status=400, content_type="text/plain")

    response = requests.post(collections_url + "/collections/create", json=body)
    if (response.text == "Creation is successful"):
        return Response(response.text, status=200, content_type="text/plain")
    else:
        return Response(response.text, status=200, content_type="text/plain")


@app.route("/users/update/<uid>", methods=["post"])
def users_update(uid):
    content_type = request.headers.get('Content-Type')
    if (content_type != 'application/json'):
        return Response('Content-Type Not Supported', status=400, content_type="text/plain")

    # get request body
    body = request.json

    if ("username" in body):
        username = body["username"]
        # update username
        # get comments by uid first
        response = requests.get(comments_url + "/comments/query/uid/" + uid)

        if (response.status_code != 200):
            # error
            return Response("Get error from API Gateway", status=500, content_type="text/plain")
        else:
            if (response.text == 'Not Found'):
                # no comments are associated with this user
                # do nothing
                pass
            else:
                # traverse through comments and change username in these comments
                data = response.json()
                json = {
                    "username": username
                }
                response = requests.post(comments_url + "/comments/update/uid/" + uid, json=json)
                    
    # not updating username
    response = requests.post(users_url + "/users/update/" + uid, json = body)
    try:
        json = response.json()
        return Response(json.dump(json), status=200, content_type="application.json")
    except Exception:
        return Response(response.text, status=200, content_type="application.json")

@app.route("/users/delete/<uid>", methods=["post"])
def users_delete(uid):
    content_type = request.headers.get('Content-Type')
    if (content_type != 'application/json'):
        return Response('Content-Type Not Supported', status=400, content_type="text/plain")

    # delete all the comments of the deleted use
    response = requests.post(comments_url + "/comments/delete/uid/" + uid)
    
    # delete user
    resp = requests.post(users_url + "/users/delete/" + uid)

    return Response("Succeed!", status=200, content_type="text/plain")
        
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
    url = users_url + "/users/query/" + str(body["uid"])
    resp = requests.get(url)

    if resp.status_code == 200:
        resp = resp.json()
        if resp['id'] != body['uid'] or resp['username'] != body['username']:
            return Response("Invalid Request", status=400, content_type="text/plain")
    else:
        return Response("Invalid Request", status=400, content_type="text/plain")

    # check if the song id are valid
    url = songs_url + "/songs/query/sid/" + str(body["sid"])
    resp = requests.get(url)

    if resp.status_code == 200:
        resp = resp.json()
        if resp['sid'] != body['sid']:
            return Response("Invalid Request", status=400, content_type="text/plain")
    else:
        return Response("Invalid Request", status=400, content_type="text/plain")

    # save the comment to the database
    url = comments_url + "/comments/create"
    print(body)
    resp = requests.post(url, json=body)
    
    if resp.status_code == 200:
        return Response("Create Successfully", status=200, content_type="text/plain")
    else:
        print(resp.json)
        return Response("Create error", status=400, content_type="text/plain")

@app.route("/songs/delete/<sid>", methods=["POST"])
def delete_song(sid):
    # check request type
    content_type = request.headers.get('Content-Type')
    if (content_type != 'application/json'):
        return Response('Content-Type Not Supported', status=400, content_type="text/plain")

    # delete the songs to the database
    url = songs_url + "/songs/delete/" + sid
    resp = requests.post(url)
    
    # delete the comments in the database
    url = comments_url + "/comments/delete/sid/" + sid
    resp = requests.post(url)
    
    # delete the song in the database
    url = collections_url + "/collections/delete/sid/" + sid
    resp = requests.post(url)

    return Response("Delete Successfully", status=200, content_type="text/plain")

@app.route("/health", methods=["get"])
def get_health():
    return Response("OK", status=200, content_type="text/plain")

if __name__ == "__main__":
    host = "0.0.0.0"
    port = 9001
    app.run(host, port)
