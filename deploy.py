import os
import json
from web3 import Web3
from solcx import compile_standard, install_solc
from dotenv import load_dotenv

load_dotenv()

# Read Solidity file
with open("./SimpleStorage.sol") as file:
    simple_storage_file = file.read()

install_solc("0.8.0")

# Compile Solidity file
compiled_sol = compile_standard(
    {
        "language": "Solidity",
        "sources": {"SimpleStorage.sol": {"content": simple_storage_file}},
        "settings": {
            "outputSelection": {
                "*": {
                    "*": ["abi", "metadata", "evm.bytecode", "evm.bytecode.sourceMap"]
                }
            }
        },
    },
    solc_version="0.8.0",
)

# Write to JSON file
with open("compiled_code.json", "w") as file:
    json.dump(compiled_sol, file)

# Get bytecode
bytecode = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["evm"][
    "bytecode"
]["object"]

# Get ABI
abi = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["abi"]

# Connect to ganache/rinkeby
w3 = Web3(Web3.HTTPProvider(os.getenv("BLOCKCHAIN_NETWORK")))
chain_id = int(os.getenv("CHAIN_ID"))
my_address = os.getenv("PUBLIC_KEY")
private_key = os.getenv("PRIVATE_KEY")

# Create the contract in python
Simple_Storage = w3.eth.contract(abi=abi, bytecode=bytecode)

# Get the latest transaction
nonce = w3.eth.get_transaction_count(my_address)

# Deploy contract
print("Deploying contract...")
# Build transaction
txn = Simple_Storage.constructor().buildTransaction(
    {"chainId": chain_id, "from": my_address, "nonce": nonce}
)

# Sign transaction
signed_txn = w3.eth.account.sign_transaction(txn, private_key=private_key)

# Send transaction
txn_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
txn_receipt = w3.eth.wait_for_transaction_receipt(txn_hash)
print("Deployed!")

# Working with contract, you need:
# Contract address
# Contract ABI
simple_storage = w3.eth.contract(address=txn_receipt.contractAddress, abi=abi)

print(simple_storage.functions.retrieve().call())

# Update contract
print("Updating contract...")
# Create store transaction
store_txn = simple_storage.functions.store(5).buildTransaction(
    {"from": my_address, "chainId": chain_id, "nonce": nonce + 1}
)

# Sign store transaction
signed_store_txn = w3.eth.account.sign_transaction(store_txn, private_key=private_key)

# Send store transaction
store_txn_hash = w3.eth.send_raw_transaction(signed_store_txn.rawTransaction)
store_txn_receipt = w3.eth.wait_for_transaction_receipt(store_txn_hash)

print("Updated!")

print(simple_storage.functions.retrieve().call())
