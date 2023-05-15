from skywalking import agent, config

config.init(agent_collector_backend_services='localhost:11800')

agent.start()
from flask import Flask, jsonify
import logging

app = Flask(__name__)

# benchmarking: sw-python run python flask_single.py

@app.route('/cat', methods=['POST', 'GET'])
def cat():
    try:
        logging.critical('fun cat got a request')
        return jsonify({'Cat Fun Fact': 'Fact is cat, cat is fat'})
    except Exception as e:  # noqa
        return jsonify({'message': str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9999, debug=False, use_reloader=False)
