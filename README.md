# Healthcare Blockchain System with TLS

A secure, blockchain-based patient record system built with Flask, featuring:

- ⛓️ Custom Blockchain with Proof-of-Work
- 🔐 RSA Digital Signatures for block validation
- 🛡️ TLS Encryption using self-signed certificates
- ⚒️ Parallelized Mining Simulation
- 🧮 Miner Wallets & Leaderboards
- 🔍 Blockchain Explorer

---

## Project Structure
```
blockchain/
├── app.py # Main Flask application
├── templates/ # HTML templates (UI)
│ ├── index.html
│ └── miners.html
| |__ explorer.html
├── static/ # Optional static files (CSS/JS)
├── chain.json # Stores the blockchain data
├── miners.json # Tracks miner stats and rewards
├── private_key.pem # RSA private key
├── public_key.pem # RSA public key
├── cert.pem # TLS certificate (self-signed)
└── key.pem # TLS private key
```

---

## Setup Instructions

### 1. Clone this repository

```bash
git clone https://github.com/89P13-24/TLS-Implementation.git
cd TLS-Implementation/blockchain
```

### 2. Create a virtual environment and install dependencies
```bash
python -m venv venv
source venv/bin/activate    # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Generate TLS certificates (if not already present)
```bash
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes
```

### 4. Run the application
```bash
python app.py
```
### 5. Then open your browser and navigate to:

```bash
https://localhost:5000
```

 You may see a browser warning due to the self-signed certificate. Accept the warning to proceed locally.

## Features
- Add Patient Records: Immutable medical entries tied to patient IDs.

- Search History: Query all blockchain entries by patient ID.

- RSA-Signed Blocks: Every block is cryptographically signed and verifiable.

- Mining Simulation: Parallel mining processes simulate real-world consensus.

- Reward System: Miners earn variable rewards based on block difficulty.

- Blockchain Explorer: View recent blocks, miner stats, and signatures.

- TLS Encryption: Ensures secure HTTPS communication.
  
## Developer Tools

- /miners – View recent blocks, wallet balances, and miner leaderboard.

- /wallets – View current wallet balances.

- /miner_stats – View raw JSON stats for all miners.

- /get_chain – Get the full blockchain JSON.

- /explorer – Blockchain Explorer UI route.

##  Notes
- RSA keys and TLS certs are generated once and reused.

- Make sure multiprocessing.set_start_method("fork") is used only inside if __name__ == "__main__" on macOS/Linux.

- All data is stored in local JSON files – easy to inspect and portable

## Future possible improvements

- Deploy publicly using NGINX + Let’s Encrypt for real TLS

- Role-based login (e.g., doctor vs. admin)

- Blockchain Explorer search, filter, and pagination

- Encryption for patient records at rest







