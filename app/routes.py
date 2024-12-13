from flask import jsonify, request
from app import server

@server.route("/")
def index():
  return "Hello World!"

# sanity check route
@server.route('/ping', methods=['GET'])
def ping_pong():
  response = {
    "message": "Pong!"
  }
  return jsonify({
    "message": "Pong!",
    "status": "success"
  })

@server.route('/q-param', methods=['GET'])
def q_param():
  year = request.args.get('year')
  return jsonify({
    "message": "Param is: " + year,
    "status": "success"
  })
  