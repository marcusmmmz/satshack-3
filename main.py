import subprocess
import re
import time

def build_contract(entrypoint_file):
    result = subprocess.run([
        "simply", "build", "--entrypoint", entrypoint_file
    ], capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print("Error compiling contract:", result.stderr)
    cmr = None
    cost = None
    program_name = None
    for line in result.stdout.splitlines():
        if line.startswith("Compiled:"):
            program_name = line.split(":", 1)[1].strip()
        elif line.startswith("CMR:"):
            cmr = line.split(":", 1)[1].strip()
        elif line.startswith("Cost:"):
            cost = line.split(":", 1)[1].strip()
    return {
        "program_name": program_name,
        "cmr": cmr,
        "cost": cost
    }

def get_contract_address(entrypoint_file):
    """
    Generate a P2TR address for the contract using simply.
    """
    result = subprocess.run([
        "simply", "deposit", "--entrypoint", entrypoint_file
    ], capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print("Error generating address:", result.stderr)
    address = None
    for line in result.stdout.splitlines():
        if line.startswith("P2TR address:"):
            address = line.split(":", 1)[1].strip()
    return address

def request_faucet(address):
    """
    Request coins from the Liquid testnet faucet.
    """
    url = f"https://liquidtestnet.com/faucet?address={address}&action=lbtc"
    result = subprocess.run(["curl", url], capture_output=True, text=True)
    html = result.stdout
    txid = None
	# Try to extract the transaction id from the HTML response
    match = re.search(r"with transaction ([0-9a-fA-F]{64})", html)
    if match:
        txid = match.group(1).strip()
        print(f"Faucet TXID: '{txid}'")
    else:
        print("Could not find TXID in faucet response.")
    
    if result.stderr:
        print("Error from faucet:", result.stderr)
	
    return txid

def withdraw(entrypoint_file, txid, destination, witness_file=None):
    """
    Spend from a contract UTXO using simply withdraw.
    """
    command = [
        "simply", "withdraw", "--entrypoint", entrypoint_file,
        "--txid", txid,
        "--destination", destination
    ]
    if witness_file:
        command += ["--witness", witness_file]
    result = subprocess.run(command, capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print("Error withdrawing:", result.stderr)
    # Output includes broadcast result
    return result.stdout

if __name__ == "__main__":
    # Example usage for always_true contract
    entrypoint = "ja.simf"
    # Step 1: Compile contract
    build_info = build_contract(entrypoint)
    print(build_info)
    # Step 2: Get contract address
    address = get_contract_address(entrypoint)
    print(f"Contract address: {address}")
    # Step 3: Request faucet
    txid = request_faucet(address)
    
	# Step 3.5 sleep is needed here.
    # without it, you may get Error: Odd number of digits
    time.sleep(15)
    
    # Step 4: Spend from contract (replace txid and destination with actual values)
    destination = "tlq1qq2g07nju42l0nlx0erqa3wsel2l8prnq96rlnhml262mcj7pe8w6ndvvyg237japt83z24m8gu4v3yfhaqvrqxydadc9scsmw" # back to faucet
    withdraw(entrypoint, txid, destination)
    # For contracts needing witness data:
    # witness_file = "witness.wit"
    # withdraw(entrypoint, txid, destination, witness_file)
