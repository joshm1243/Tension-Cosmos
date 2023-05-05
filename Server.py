from flask import Flask, request, jsonify
import json

from services.scripts.cleaning import PLM_SC_CLEAN
from services.scripts.tagging import PLM_SC_TAG
from services.scripts.block import PLM_SC_BLOCK
from services.scripts.extraction import *
from services.scripts.routing import PLM_SC_ROUTE_BLOCKS

from services.samples.render import PLM_SA_RENDER
from services.samples.train_vae import PLM_SA_TRAIN_VAE
from services.samples.train_dalle import PLM_SA_TRAIN_DALLE
from services.samples.generate import PLM_SA_GENERATE
from services.samples.sample import PLM_SA_SAMPLE




## Script API Endpoint - Used For Posting New Scripts
app = Flask(__name__)

@app.route("/api/samples/render", methods=["POST"])
def Render():

    request_data = request.get_json()
    samples = json.loads(request_data["samples"])

    PLM_SA_RENDER(samples)
    PLM_SA_TRAIN_VAE()
    PLM_SA_TRAIN_DALLE()
    
    return {"this" : "test"}

@app.route("/api/designs/generate", methods=["POST"])
def GenerateDesign():
    request_data = request.get_json()
    prompt = request_data["prompt"][1:-1]
    PLM_SA_GENERATE(prompt)
    hex_codes = PLM_SA_SAMPLE(prompt)
    return {"sample_values" : hex_codes}

@app.route("/api/script", methods=["POST"])
def Script():

    request_data = request.get_json()
    script_content = request_data["script"]

    #script_content = open("script.txt").read()

    raw_script = PLM_SC_CLEAN(script_content)
    tagged_script = PLM_SC_TAG(raw_script)

    tagged_script = PLM_SC_EXT_PREPARE(tagged_script)
    tagged_script = PLM_SC_EXT_CHARACTER(tagged_script)
    tagged_script = PLM_SC_EXT_LOCATION(tagged_script)
    tagged_script = PLM_SC_EXT_TOD(tagged_script)
    tagged_script = PLM_SC_EXT_ENVIRONMENT(tagged_script)
    tagged_script = PLM_SC_EXT_EMOTION(tagged_script)
    
    tagged_script = PLM_SC_EXT_CREATE_TRACK(tagged_script)

    blocked_script = PLM_SC_BLOCK(tagged_script)
    blocked_script = PLM_SC_ROUTE_BLOCKS(blocked_script)

    return blocked_script

app.run(port=3001)
#Script()