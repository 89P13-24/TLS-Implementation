from flask import Flask, request, jsonify, render_template
import hashlib
import json
from time import time
import os
import multiprocessing
import random
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.exceptions import InvalidSignature

### openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes for creating self-signed certs


app = Flask(__name__)

def generate_keys():
    if not os.path.exists("private_key.pem") or not os.path.exists("public_key.pem"):
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
        public_key = private_key.public_key()

        with open("private_key.pem", "wb") as f:
            f.write(private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            ))

        with open("public_key.pem", "wb") as f:
            f.write(public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            ))

def load_private_key():
    with open("private_key.pem", "rb") as f:
        return serialization.load_pem_private_key(f.read(), password=None)

def load_public_key():
    with open("public_key.pem", "rb") as f:
        return serialization.load_pem_public_key(f.read())

def sign_data(data, private_key):
    return private_key.sign(
        data,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )

def verify_signature(data, signature, public_key):
    try:
        public_key.verify(
            signature,
            data,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return True
    except InvalidSignature:
        return False

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
        generate_keys()
        self.private_key = load_private_key()
        self.public_key = load_public_key()
        self.chain_file = chain_file
        self.miner_file = "miners.json"
        self.difficulty = 4
        self.reward_per_block = 10
        self.chain = self.load_chain()
        self.wallets = {}
        self.miners = self.load_miners()
        if not self.chain:
            print("No chain file found. Creating Genesis Block.")
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
        self.reward_per_block = 10 ** (self.difficulty - 3)
        print(f"\nStarting mining for block {block['index']} with difficulty {self.difficulty}...")
        start_time = time()
        block = self.proof_of_work(block)
        end_time = time()
        print(f"Block {block['index']} mined by {block['miner']} in {end_time - start_time:.2f}s")

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

        block_data = json.dumps(block, sort_keys=True).encode()
        block['signature'] = sign_data(block_data, self.private_key).hex()

        self.chain.append(block)
        self.save_chain()
        return block

    def proof_of_work(self, block):
        manager = multiprocessing.Manager()
        result_dict = manager.dict()
        result_dict['winner'] = False
        processes = []
        block_data = {k: v for k, v in block.items() if k != 'hash'}
        for i in range(4):
            p = multiprocessing.Process(target=miner_worker, args=(block_data, self.difficulty, result_dict, f"Miner_{i+1}"))
            p.start()
            processes.append(p)
        for p in processes:
            p.join()
        block['nonce'] = result_dict['nonce']
        block['hash'] = result_dict['hash']
        block['miner'] = result_dict['miner_id']
        return block

    def is_valid_block(self, block):
        signature = bytes.fromhex(block['signature'])
        block_copy = block.copy()
        del block_copy['signature']
        block_data = json.dumps(block_copy, sort_keys=True).encode()
        return verify_signature(block_data, signature, self.public_key)

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
    app.run(
        host='0.0.0.0',
        port=8080,
        debug=True,
        ssl_context=('cert.pem', 'key.pem')  # 👈 Enables HTTPS
    )

