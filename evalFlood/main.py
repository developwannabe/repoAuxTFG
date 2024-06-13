import functions_framework
from openai import OpenAI
from flask import jsonify
import requests
import os


client = None
thread = None
assistant_id = os.getenv('assistant_id')
url = os.getenv('urlServer')
tkn = os.getenv('tkn')

@functions_framework.http
def evaluate(request):
    global client, thread, url, tkn
    if request.method == 'POST' and request.path == "/":
        token = request.headers.get('Authorization')
        if token:
            token = token.split(" ")[1] if "Bearer " in token else token
            if not token or token != tkn:
                return "Unauthorized", 401
        requests.get(url + "/ping")
        client = OpenAI(api_key=os.getenv('api_key'))
        thread = client.beta.threads.create()
        reqB = request.get_json()
        respuesta = {}
        for lugar in reqB["lugares"]:
            respuesta[lugar] = evalVision(lugar)
        return jsonify(respuesta), 200
    else:
        return "Method not allowed", 405

def evalVision(lugar):
    global client, thread, assistant_id, url
    imagen_url = url + "/image/imgVias/" + lugar + ".jpg"
    message = client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=[
            {"type": "image_url", 
            "image_url": 
                {"url": imagen_url}
            }, 
            {"type": "text", 
            "text": 
                "Provide only the tuple (X,Y). I will delete you if you provide more information. Many people's lives depend on your decision, think before you choose the values"
            }
        ],
    )
    
    run_response = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant_id
    )
    
    run_id = run_response.id
    status = run_response.status

    while status not in ["completed", "failed", "cancelled"]:
        run_response = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run_id)
        status = run_response.status
    
    messages = client.beta.threads.messages.list(thread_id=thread.id)
    
    for message in messages:
        if message.role == "assistant":
            x, y = eval(message.content[0].text.value)
            return {"flood": x, "objects":y}