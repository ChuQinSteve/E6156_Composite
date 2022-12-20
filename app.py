from flask import Flask, Response, session, abort, redirect, request
import os
import requests

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
                
    
    #  delete all the collections of the deleted user is handled by delete cascade
    response = requests.post(target + "/users/delete/" + uid)
    if (response.text == "Delete Successfully"):
        return Response(response.text, status=200, content_type="text/plain")
    else:
        return Response(response.text, status=400, content_type="text/plain")


if __name__ == "__main__":
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", 5000))
    app.run(host, port)