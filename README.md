# Python Blockchain Implementation

A modular blockchain implementation in Python with Flask REST API, focusing on security, scalability, and proper logging.

## 🚀 Features

- Proof of Work (PoW) consensus mechanism with configurable difficulty
- Transaction management with gas fees (0.01 per transaction)
- Mempool for pending transactions
- Node networking and chain synchronization
- Custom secure hashing algorithm using dynamic primes
- Comprehensive logging system with rotation
- RESTful API interface
- Automated testing suite with pytest

## 📋 Prerequisites

- Python 3.8+
- pip (Python package manager)
- Virtual environment (recommended)

## 🛠️ Installation

1. Clone the repository:
```bash
git clone https://github.com/GekixD/blockchain-flask.git
cd blockchain-flask
```

2. Create and activate a virtual environment:
```bash
python -m venv venv

# On Windows
.\venv\Scripts\activate

# On Unix/MacOS
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## 📦 Dependencies

Core dependencies are defined in `requirements.txt`:
```python:requirements.txt
startLine: 1
endLine: 5
```

## 🚀 Running the Application

Start the blockchain node:
```bash
python run.py --host 127.0.0.1 --port 5000 --debug
```

## 🔧 Configuration

### Blockchain Configuration
```python:src/config/config.py
startLine: 25
endLine: 48
```

### Logging Configuration
```python:src/config/config.py
startLine: 3
endLine: 22
```

## 📡 API Endpoints

### Mining
- `POST /mine_block`
  ```json
  {
    "miner_address": "your_address"
  }
  ```
  Implementation: 
  ```python:src/api/routes.py
  startLine: 20
  endLine: 58
  ```

### Transactions
- `POST /add_transaction`
  ```json
  {
    "sender": "sender_address",
    "receiver": "receiver_address",
    "amount": 10
  }
  ```
  Implementation:
  ```python:src/blockchain/blockchain.py
  startLine: 115
  endLine: 133
  ```

## 🧪 Testing

Test suite implementation:
```python:tests/test_blockchain.py
startLine: 1
endLine: 33
```

Run tests:
```bash
pytest
pytest --cov=src tests/
```

## 📝 Logging

Logging is implemented across all major components:

1. API Routes: _didn't have time to check if finished_
```python:src/api/routes.py
startLine: 9
endLine: 10
```

2. Blockchain Core:
```python:src/blockchain/blockchain.py
startLine: 10
endLine: 11
```

3. Hashing Module: _incomplete and not used_
```python:src/blockchain/hashing.py
startLine: 7
endLine: 8
```

## 🔒 Security Features

1. Custom Hashing Algorithm: _incomplete and not used_
```python:src/blockchain/hashing.py
startLine: 12
endLine: 38
```

2. Transaction Validation:
```python:src/blockchain/helpers.py
startLine: 10
endLine: 14
```

## 🗄️ Project Structure
```
blockchain-project/
├── src/
│   ├── api/            # API implementation
│   ├── blockchain/     # Core blockchain logic
│   ├── config/         # Configuration files
│   └── utils/          # Utility functions
├── tests/              # Test suite
├── logs/               # Log files
├── requirements.txt    # Dependencies
└── run.py             # Application entry point
```

## 🔍 Development Tools

1. Git Ignore Configuration:
```gitignore
startLine: 1
endLine: 42
```

2. Setup Configuration:
```python:setup.py
startLine: 1
endLine: 14
```

## 📝 TODO List Generator

The project includes a TODO list generator:
```shell:src/todos.sh
startLine: 1
endLine: 4
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📞 Contact

Project Link: [https://github.com/GekixD/blockchain-flask](https://github.com/GekixD/blockchain-flask)
