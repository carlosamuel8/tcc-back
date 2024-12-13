from flask import Flask, jsonify, request
from flask_cors import CORS

# instantiate the app
app = Flask(__name__)
app.config.from_object(__name__)

# enable CORS
CORS(app, resources={r'/*': {'origins': '*'}})

@app.route("/")
def index():
  return "Hello World!"

# sanity check route
@app.route('/ping', methods=['GET'])
def ping_pong():
  response = {
    "message": "Pong!"
  }
  return jsonify({
    "message": "Pong!",
    "status": "success"
  })

@app.route('/q-param', methods=['GET'])
def q_param():
  year = request.args.get('year')
  return jsonify({
    "message": "Param is: " + year,
    "status": "success"
  })

if __name__ == '__main__':
  app.run()
