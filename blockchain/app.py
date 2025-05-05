from flask import Flask, request, jsonify, render_template
import hashlib
import json
from time import time

app = Flask(__name__)

class Blockchain:
    def __init__(self):
        self.chain = []
        self.create_block(data='Genesis Block')

    def create_block(self, data):
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'data': data,
            'previous_hash': self.chain[-1]['hash'] if self.chain else '0',
        }
        block['hash'] = self.hash(block)
        self.chain.append(block)
        return block

    def hash(self, block):
        block_copy = block.copy()
        block_copy.pop('hash', None)
        return hashlib.sha256(json.dumps(block_copy, sort_keys=True).encode()).hexdigest()

    def get_chain(self):
        return self.chain

    def get_by_patient(self, patient_id):
        return [blk for blk in self.chain if blk['data'].get('patient_id') == patient_id]

blockchain = Blockchain()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add_record', methods=['POST'])
def add_record():
    data = request.json
    if 'patient_id' not in data or 'record' not in data:
        return jsonify({'error': 'Missing data'}), 400
    block = blockchain.create_block(data)
    return jsonify(block), 201

@app.route('/get_chain', methods=['GET'])
def get_chain():
    print (blockchain.get_chain())
    return jsonify(blockchain.get_chain())

@app.route('/get_patient/<patient_id>', methods=['GET'])
def get_patient(patient_id):
    records = blockchain.get_by_patient(patient_id)
    return jsonify(records)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
