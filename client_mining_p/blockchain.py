import hashlib
import json
from time import time
from uuid import uuid4

from flask import Flask, jsonify, request

class Blockchain(object):
    def __init__(self):
        self.chain = []
        self.current_transactions = []

        # create the genesis block
        self.new_block(previous_hash=1, proof=100)

    def new_transaction(self, sender, recipient, amount):
        """
        Creates a new transaction to go into the next mined block

        :param sender: <str> Address of the recipient
        :param recipient: <str> Address of the recipient
        :return: <int>
        """

    def new_block(self, proof, previous_hash=None):
        """
        Create a new Block in the Blockchain

        A block should have:
        * Index
        * Timestamp
        * List of current transactions
        * The proof used to mine this block
        * The hash of the previous block

        :param proof: <int> The proof given by the Proof of Work Algorithm
        :param previous_hash: (Optional) <str> Hash of the previous Block
        :return: <dict> New Block
        """

        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.last_block),
        }

        self.current_transactions = []
        self.chain.append(block)

        return block

    def hash(self, block):
        """
        Creates a SHA-256 hash of a Block

        :param block: <dict> Block
        :return: <str>
        """
        # Use json.dumps to convert json into a string
        # Use hashlib.sha256 to create a hash
        # It requires a `bytes-like` object, whish is what .enchode() does.
        # It conervts the Python string into a byte string.
        # We must make sure that the dictionary is ordered,
        # or we'll have inconsistent hashes

        # TODO: Create the block_string
        string_object = json.dumps(block, sort_keys=True)
        block_string = string_object.encode()

        # TODO: hash this string using sha256
        raw_hash = hashlib.sha256(block_string)

        # By itself, the sha256 functino returns the hash in a raw string that
        # will likely include escaped characters. This can be hard to read, but
        # .hexdigest() converts the hash to a string of hexadecimal characters,
        # which is easier to work with and understand
        hash_string = raw_hash.hexdigest()
        # TODO: return the hashed blocke string in hexadecimal format
        return hash_string

    @property
    def last_block(self):
        return self.chain[-1]

    @staticmethod
    def valid_proof(block_string, proof):
        """
        Validates the proof: Does hash(block_string, proof) contain 3 leading
        zeroes? Return true if the proof is valid
        :param block_string: <string> The stringified block to use to check in
        combinatino with `proof`
        :param proof: <int?> The value that when combined with the stringified
        previous block results in a hash that has the correct number of leading
        zeroes.
        :return: True if the resulting hash is a valid proof, False otherwise
        """

        # TODO
        # print(f"i will now check if {proof} is valid")
        guess = block_string + str(proof)
        guess = guess.encode()

        hash_value = hashlib.sha256(guess).hexdigest()

        return hash_value[:6] == '000000'


# Instantiate our Node
app = Flask(__name__)

# Generate a globally unique address for this node
node_identifier = str(uuid4()).replace('-', '')

# Instantiate the Blockchain
blockchain = Blockchain()


@app.route('/', methods=['GET'])
def hello_world():
    response = {
        'text': 'hello world',
    }

    return jsonify(response), 200


@app.route('/mine', methods=['POST'])
def mine():
    data = request.get_json()

    if 'id' not in data or 'proof' not in data:
        res = {'message': 'missing values'}
        return jsonify(res), 400

    proof = data['proof']
    last_block = blockchain.last_block
    block_string = json.dumps(last_block, sort_keys=True)

    if blockchain.valid_proof(block_string, proof):
        blockchain.new_transaction(
            sender="0",
            recipient=data['id'],
            amount=1
        )

        new_block = blockchain.new_block(proof)
        response = {
            'block': new_block
        }

        return jsonify(response), 200

    response = {
        'message': 'Proof is invalid',
    }

    return jsonify(response), 200


@app.route('/chain', methods=['GET'])
def full_chain():
    res = {
        'len': len(blockchain.chain),
        'chain': blockchain.chain,
    }

    return jsonify(res), 200


@app.route('/last_block', methods=['GET'])
def last_block():
    res = {
        'last_block': blockchain.last_block
    }

    return jsonify(res), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
