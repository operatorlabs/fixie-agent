from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
import requests
import json
from dotenv import load_dotenv
import os

class Entry(BaseModel):
    message: str

app = FastAPI()
load_dotenv()

@app.post("/entry")
def entry(entry: Entry):
    url = f"{os.environ.get('FIXIE_URL')}"
    headers = {"Content-Type": "application/json"}
    data = {"message": entry.message}
    response = requests.post(url, headers=headers, data=json.dumps(data), stream=True)

    if response.status_code == 200:
        for line in response.iter_lines():
            # filter out keep-alive new lines
            if line:
                decoded_line = line.decode('utf-8')
                json_response = json.loads(decoded_line)
                for turn in json_response['turns']:
                    if turn['role'] == 'assistant' and turn['state'] == 'done':
                        for message in turn['messages']:
                            if message['state'] == 'done':
                                return {"response": message['content']}
    return {"response": "Error in processing request"}