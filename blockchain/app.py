from flask import Flask, request, jsonify, render_template
import hashlib
import json
from time import time
import os
import multiprocessing
import random

app = Flask(__name__)

def miner_worker(block_data, difficulty, result_dict, miner_id):
    nonce = random.randint(0, 1_000_000)
    while not result_dict.get("winner"):
        candidate_block = block_data.copy()
        candidate_block['nonce'] = nonce
        block_string = json.dumps(candidate_block, sort_keys=True).encode()
        block_hash = hashlib.sha256(block_string).hexdigest()

        if block_hash.startswith('0' * difficulty):
            result_dict['winner'] = True
            result_dict['nonce'] = nonce
            result_dict['hash'] = block_hash
            result_dict['miner_id'] = miner_id
            return
        nonce += 1

class Blockchain:
    def __init__(self, chain_file="chain.json"):
        self.chain_file = chain_file
        self.miner_file = "miners.json"
        self.difficulty = 4
        self.reward_per_block = 10

        self.chain = self.load_chain()
        self.wallets = {}  # miner_id -> reward balance
        self.miners = self.load_miners()

        if not self.chain:
            print(" No chain file found. Creating Genesis Block.")
            self.create_block(data='Genesis Block')
            self.save_chain()

    def create_block(self, data):
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'data': data,
            'previous_hash': self.chain[-1]['hash'] if self.chain else '0',
            'nonce': 0
        }


        self.difficulty = random.randint(4, 5)
        self.reward_per_block = 10 ** (self.difficulty-3) 
        print(f"\n Starting mining for block {block['index']} with difficulty {self.difficulty}...")

        start_time = time()
        block = self.proof_of_work(block)
        end_time = time()
        print(f" Block {block['index']} mined by {block['miner']} "
              f"in {end_time - start_time:.2f}s with nonce {block['nonce']}")

        miner_id = block['miner']
        self.wallets[miner_id] = self.wallets.get(miner_id, 0) + self.reward_per_block

        if miner_id not in self.miners:
            self.miners[miner_id] = {
                "blocks_mined": 0,
                "total_rewards": 0,
                "joined_at": time()
            }
        self.miners[miner_id]["blocks_mined"] += 1
        self.miners[miner_id]["total_rewards"] += self.reward_per_block
        self.save_miners()

        self.chain.append(block)
        self.save_chain()
        return block

    def proof_of_work(self, block):
        manager = multiprocessing.Manager()
        result_dict = manager.dict()
        result_dict['winner'] = False

        processes = []
        num_miners = 4

        block_data = {k: v for k, v in block.items() if k != 'hash'}

        for i in range(num_miners):
            p = multiprocessing.Process(target=miner_worker,
                                        args=(block_data, self.difficulty, result_dict, f"Miner_{i+1}"))
            p.start()
            processes.append(p)

        for p in processes:
            p.join()

        block['nonce'] = result_dict['nonce']
        block['hash'] = result_dict['hash']
        block['miner'] = result_dict['miner_id']
        return block

    def hash(self, block):
        block_copy = block.copy()
        block_copy.pop('hash', None)
        encoded_block = json.dumps(block_copy, sort_keys=True).encode()
        return hashlib.sha256(encoded_block).hexdigest()

    def get_chain(self):
        return self.chain

    def get_by_patient(self, patient_id):
        return [blk for blk in self.chain if isinstance(blk['data'], dict) and blk['data'].get('patient_id') == patient_id]

    def save_chain(self):
        with open(self.chain_file, 'w') as f:
            json.dump(self.chain, f, indent=4)

    def load_chain(self):
        if os.path.exists(self.chain_file):
            with open(self.chain_file, 'r') as f:
                return json.load(f)
        return []

    def load_miners(self):
        if os.path.exists(self.miner_file):
            with open(self.miner_file, 'r') as f:
                return json.load(f)
        return {}

    def save_miners(self):
        with open(self.miner_file, 'w') as f:
            json.dump(self.miners, f, indent=4)


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
    return jsonify(blockchain.get_chain())

@app.route('/get_patient/<patient_id>', methods=['GET'])
def get_patient(patient_id):
    records = blockchain.get_by_patient(patient_id)
    return jsonify(records)

@app.route('/wallets', methods=['GET'])
def get_wallets():
    return jsonify(blockchain.wallets)

@app.route('/miner_stats', methods=['GET'])
def get_miner_stats():
    return jsonify(blockchain.miners)

@app.route('/miners', methods=['GET'])
def miners_page():
    chain = blockchain.get_chain()
    wallets = blockchain.wallets
    miners = blockchain.miners
    return render_template('miners.html', chain=chain[-10:], wallets=wallets, miners=miners)



if __name__ == '__main__':
    multiprocessing.set_start_method("fork")
    app.run(host='0.0.0.0', debug=True)
