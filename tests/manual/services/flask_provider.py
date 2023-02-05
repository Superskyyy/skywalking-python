import time


if __name__ == '__main__':
    from flask import Flask, jsonify

    app = Flask(__name__)

    @app.route('/users', methods=['POST', 'GET'])
    def application():
        return jsonify({'status': 'ok'})

    PORT = 9091
    app.run(host='0.0.0.0', port=PORT, debug=True)