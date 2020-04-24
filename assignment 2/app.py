import os
import requests
from requests.exceptions import Timeout
from sanic import Sanic
from sanic.response import json
from sanic import response
from sanic import request

forwarding = os.environ.get('FORWARDING_ADDRESS') #Checks if current instance is a slave or main

app = Sanic(name='your_application_name')

key_value_dict = {} #Dictionary containing key and values of server

#Function preforms PUT operations
def puts(key, value):
    #Checks if key is correct length
    if len(key) > 50:
        return response.json({"error":"Key is too long","message":"Error in PUT"},status=400)

    replace = key in key_value_dict #Checks for key in dictionary
    if replace: #If key is in Dictionary replace
        key_value_dict[key] = value
        return response.json({"message":"Updated successfully","replaced":replace},status=200)
    else: #If key is not in Dict add
        key_value_dict[key] = value
        return response.json({"message":"Added successfully","replaced":replace},status=201)

#Function preforms GET operations
def gets(key):
    exist = key in key_value_dict #Checks if key is in Dict
    if exist: #If key is in Dict returns value
        value = key_value_dict.get(key)
        return response.json({"doesExist":exist,"message":"Retrieved successfully","value": value},status=200)
    return response.json({"doesExist":exist,"error":"Key does not exist","message":"Error in GET"},status=404) #If not in Dict return Error

#Function preforms DELETE operations samething as GET but is deleting key/value instead
def delete(key):
    exist = key in key_value_dict
    if exist:
        del key_value_dict[key]
        return response.json({"doesExist":exist,"message":"Deleted successfully"},status=200)
    return response.json({"doesExist":exist,"error":"Key does not exist","message":"Error in DELETE"},status=404)


@app.route("/key-value-store/<key>", methods=['GET','PUT', 'DELETE'])
async def key_value(request, key):
    if request.method == "PUT":
        if forwarding: #Checks if slave instance
            try:
                done = requests.put(url=f"http://{forwarding}/key-value-store/{key}", json=request.json, timeout=0.1) #Uses requests library to forward to main instance
            except Timeout:
                return response.json({"error":"Main instance is down","message":"Error in PUT"},status=503)
            return response.json(done.json(),status=done.status_code) #Converts requests reponse to sanic response
        if not request.json: #Checks if a value was passed given in request
            return response.json({"error":"Value is missing","message":"Error in PUT"},status=400)
        return puts(key, request.json["value"])

    if request.method == "GET":
        if forwarding:
            try: #Tries to contact main 
                done = requests.get(url=f"http://{forwarding}/key-value-store/{key}", timeout=0.1)
            except Timeout: #if it timesout throw status 503 and error msg
                return response.json({"error":"Main instance is down","message":"Error in GET"},status=503)
            return response.json(done.json(),status=done.status_code)
        return gets(key)

    if request.method == "DELETE":
        if forwarding:
            try:
                done = requests.delete(url=f"http://{forwarding}/key-value-store/{key}", timeout=0.1)
            except Timeout:
                return response.json({"error":"Main instance is down","message":"Error in DELETE"},status=503)
            return response.json(done.json(),status=done.status_code)
        return delete(key)

if __name__ == "__main__":
  app.run(host="0.0.0.0", port=8085)
