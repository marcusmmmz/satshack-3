import json
import requests
import subprocess
import base64
import json
import re

def compile_simplicity(file_path):
	command = ["simc", file_path]
	result = subprocess.run(command, capture_output=True, text=True)
	if result.stderr:
		print("Error:", result.stderr)
		return None

	# Extract base64 after 'Program:'
	match = re.search(r"Program:\s*([A-Za-z0-9+/=]+)", result.stdout)
	if match:
		program_b64 = match.group(1).strip()
	else:
		# fallback: get last non-empty line
		lines = result.stdout.splitlines()
		program_b64 = next((line.strip() for line in reversed(lines) if line.strip()), "")
	print(f"Program (base64): {program_b64}")

	command = ["hal-simplicity", "simplicity", "info", program_b64]
	result = subprocess.run(command, capture_output=True, text=True)
	if result.stderr:
		print("Error:", result.stderr)
		return None
	try:
		info = json.loads(result.stdout)
	except Exception as e:
		print("Error parsing JSON output from hal-simplicity:", e)
		return None

	cmr = info.get("cmr", "")
	address = info.get("liquid_testnet_address_unconf", "")
	print(f"CMR: {cmr}")
	print(f"Address: {address}")

	try:
		program_hex = base64.b64decode(program_b64).hex()
	except Exception as e:
		print("Error decoding base64:", e)
		program_hex = ""
	print(f"Program (hex): {program_hex}")

	control_block = "bef5919fa64ce45f8306849072b26c1bfdd2937e6b81774796ff372bd1eb5362d2"
	print(f"Control Block: {control_block}")

	return {
		"program_b64": program_b64,
		"cmr": cmr,
		"address": address,
		"program_hex": program_hex,
		"control_block": control_block
	}

def pay_from_faucet(address):
	result = subprocess.run([
		"curl",
		f"https://liquidtestnet.com/faucet?address={address}&action=lbtc"
	], capture_output=True, text=True)
	print(result.stdout)
	if result.stderr:
		print("Error:", result.stderr)

def get_utxo_details(address):
	"""
	Fetch UTXO details for a Liquid testnet address and set variables for txid, vout, input_value, fee, amount, asset_id, and destination.
	"""
	url = f"https://blockstream.info/liquidtestnet/api/address/{address}/utxo"
	response = requests.get(url)
	utxos = response.json()
	if not utxos:
		print("No UTXOs found for this address.")
		return None
	utxo = utxos[0]
	txid = utxo.get('txid', '')
	vout = utxo.get('vout', 0)
	input_value = utxo.get('value', 0)
	fee = 500
	amount = input_value - fee
	asset_id = "144c654344aa716d6f3abcc1ca90e5641e4e2a7f633bc09fe3baf64585819a49"
	destination = "tex1qjnr7j6u7tzh4q7djumh9rtldv5q7yllxuhaasp"
	print(f"TXID: {txid}")
	print(f"VOUT: {vout}")
	print(f"INPUT_VALUE: {input_value}")
	print(f"FEE: {fee}")
	print(f"AMOUNT: {amount}")
	print(f"ASSET_ID: {asset_id}")
	print(f"DESTINATION: {destination}")
	return {
		'txid': txid,
		'vout': vout,
		'input_value': input_value,
		'fee': fee,
		'amount': amount,
		'asset_id': asset_id,
		'destination': destination
	}

def create_transaction(txid, vout, program_hex, cmr, control_block, asset_id, destination, amount, fee):
	"""
	Create a transaction JSON and write it to transaction.json.
	"""
	tx_json = {
		"version": 2,
		"locktime": {"Blocks": 0},
		"inputs": [{
			"txid": txid,
			"vout": vout,
			"script_sig": {"hex": ""},
			"sequence": 0,
			"is_pegin": False,
			"has_issuance": False,
			"witness": {
				"script_witness": [
					"",
					program_hex,
					cmr,
					control_block
				]
			}
		}],
		"outputs": [
			{
				"script_pub_key": {"address": destination},
				"asset": {"type": "explicit", "asset": asset_id},
				"value": {"type": "explicit", "value": amount},
				"nonce": {"type": "null"}
			},
			{
				"script_pub_key": {"hex": ""},
				"asset": {"type": "explicit", "asset": asset_id},
				"value": {"type": "explicit", "value": fee},
				"nonce": {"type": "null"}
			}
		]
	}
	with open("transaction.json", "w") as f:
		json.dump(tx_json, f, indent=2)
	print("transaction.json created.")

	import subprocess
	with open("transaction.json", "r") as f:
		tx_json_str = f.read()
	result = subprocess.run([
		"hal-simplicity", "tx", "create"
	], input=tx_json_str, capture_output=True, text=True)
	if result.stderr:
		print("Error creating transaction hex:", result.stderr)
	else:
		tx_hex = result.stdout.strip()
		print(f"TX_HEX: {tx_hex}")
	return tx_hex

def broadcast_transaction(tx_hex):
	"""
	Broadcast a transaction hex to the Liquid testnet using curl and print the result.
	"""
	import subprocess
	result = subprocess.run([
		"curl", "-s", "-X", "POST", "https://blockstream.info/liquidtestnet/api/tx", "-d", "@-"
	], input=tx_hex, capture_output=True, text=True)
	print(result.stdout)
	if result.stderr:
		print("Error broadcasting transaction:", result.stderr)

def main():
	result = compile_simplicity("contract.simf")

	if result and result["address"]:
		# pay_from_faucet(address)

		utxo_info = get_utxo_details(result["address"])
		if utxo_info:
			tx_hex = create_transaction(
				txid=utxo_info["txid"],
				vout=utxo_info["vout"],
				program_hex=result["program_hex"],
				cmr=result["cmr"],
				control_block=result["control_block"],
				asset_id=utxo_info["asset_id"],
				destination=utxo_info["destination"],
				amount=utxo_info["amount"],
				fee=utxo_info["fee"]
			)
		
		broadcast_transaction(tx_hex)
	


if __name__ == "__main__":
	main()