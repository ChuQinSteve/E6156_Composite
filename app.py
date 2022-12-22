from flask import Flask, Response, Response, session, abort, redirect, request
import os
import requests
import requests
import os

app = Flask("Composite Service")
target = "https://" + os.environ.get("TARGET")

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
        response = requests.get(target + "/songs/query/sid/" + sid)
        print(response.text)
        if (response.status_code != 200):
            # error
            return Response("Get error from API Gateway", status=500, content_type="text/plain")
        else:
            # check if id is not found
            if (response.text == 'Not Found'):
                return Response("Invalid Song ID", status=400, content_type="text/plain")

    response = requests.post(target + "/collections/create", json=body)
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

    if ("user_name" in body):
        user_name = body["user_name"]
        # update username
        # get comments by uid first
        response = requests.get(target + "/comments/query/uid/" + uid)
        print(target + "/comments/query/uid/" + uid)
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
                for item in data:
                    json = {
                        "user_name": user_name
                    }
                    cid = item["cid"]
                    response = requests.post(target + "/comments/update/" + cid, json=json)
    
    # not updating username
    response = requests.post(target + "/users/update/" + uid, json = body)
    try:
        json = response.json()
        return Response(json.dump(json), status=200, content_type="application.json")
    except Exception:
        return Response(response.text, status=200, content_type="application.json")

@app.route("/delete/user/<uid>", methods=["post"])
def users_delete(uid):
    content_type = request.headers.get('Content-Type')
    if (content_type != 'application/json'):
        return Response('Content-Type Not Supported', status=400, content_type="text/plain")

    # delete all the comments of the deleted user
    response = requests.get(target + "/comments/query/uid/" + uid)
    if (response.status_code != 200):
        # error
        return Response("Get error from API Gateway", status=500, content_type="text/plain")
    else:
        if (response.text == 'Not Found'):
            # no comments are associated with the user
            # do nothing
            pass
        else:
            data = response.json()
            for item in data:
                cid = str(item["cid"])
                response = requests.post(target + "/comments/delete/" + cid)
                print(target + "/comments/delete/cid/" + cid)
                print(response)
                
    @app.route("/comments/create", methods=["POST"])
def create_comment():
    # check request type
    content_type = request.headers.get('Content-Type')
    if (content_type != 'application/json'):
        return Response('Content-Type Not Supported', status=400, content_type="text/plain")
    
    #  delete all the collections of the deleted user is handled by delete cascade
    response = requests.post(target + "/users/delete/" + uid)
    if (response.text == "Delete Successfully"):
        return Response(response.text, status=200, content_type="text/plain")
    else:
        return Response(response.text, status=400, content_type="text/plain")
        
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
def delete_song(sid):
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