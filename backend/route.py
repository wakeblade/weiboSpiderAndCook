# -*- coding: utf-8 -*-

from flask import Flask,jsonify,request
from flask_cors import CORS

api = Flask('backend')
CORS(api)

config={
    'min_fans':5000,
    'min_ids':2000
}

@api.route("/config",methods=["GET"])
def getConfig():
    print(config)
    return jsonify({'config':config})

@api.route("/config",methods=["POST"])
def setConfig():
    global config
    print("before",config)
    config = request.get_json(silent=True)
    print("end",config)
    return jsonify({'message':'配置参数保存成功！'})