import os
import json
import requests
from pprint import pprint

def getWallets():
	"""
	Retrieve a list of wallets

	Returns:
		wallets (list) if error None
	"""

	# REQUIRED: replace environment variaables for your URL and ADMIN_API_KEY
	api = os.environ["LNBITS_URL"] + "/usermanager/api/v1/wallets"
	headers = {"X-Api-Key": os.environ["LNBITS_ADMIN_API_KEY"]} 

	resp = requests.get(api, headers=headers)

	if resp.status_code == 200:
		return json.loads(resp.text)
	else:
		print (f"Error code    : {resp.status_code}")
		print (f"Error message : {resp.text}")
		return None

def getWalletBalance(apikey):
	"""
	Retrieve a balance for a given user key

	Args:
		apikey (str): a user's api key
	Returns:
		sats (int) if error None
	"""

	api = os.environ["LNBITS_URL"] + "/api/v1/wallet"
	# REQUIRED: NOT ADMIN_API_KEY but USER_API_KEY for the user
	headers = {"X-Api-Key": apikey}

	resp = requests.get(api, headers=headers)

	if resp.status_code == 200:
		# returned value is msats, so covert it into sats
		return int(json.loads(resp.text)["balance"]/1000)
	else:
		print (f"Error code    : {resp.status_code}")
		print (f"Error message : {resp.text}")
		return None

def createInvoice(receiver, sats):
	"""
	Create an invoice for a given user key and msats

	Args:
		receiver (dict): a receiver's wallet name and apikey
		msats (int): milli sats (1 mats == 1000 msats)
	Returns:
		payment hash (str) if error None
	"""

	api = os.environ["LNBITS_URL"] + "/api/v1/payments"

	headers = {"X-Api-Key": receiver["apikey"]}
	memo = f"Created invoice from {receiver['walletname']}"

	params = {"out": False, "amount": sats, "memo": memo,
			"unit": "sat", "lnurl_callback": True}

	resp = requests.post(api, headers=headers, json=params)
	
	if resp.status_code == 201:
		return json.loads(resp.text)["payment_hash"]
	else:
		print (f"Error code    : {resp.status_code}")
		print (f"Error message : {resp.text}")
		return None

def getInvoice(receiver, paymentHash):
	"""
	Retrieve an invoice for a given payment hash and api key

	Args:
		receiver (dict): a receiver's wallet name and apikey
		msats (int): milli sats (1 mats == 1000 msats)
	Returns:
		bolt11 invoice (str) if error None
	"""

	api = os.environ["LNBITS_URL"] + "/api/v1/payments"
	headers = {"X-Api-Key": receiver["apikey"]}

	resp = requests.get(api + f"/{paymentHash}", headers=headers)

	if resp.status_code == 200:
		return json.loads(resp.text)["details"]["bolt11"]
	else:
		print (f"Error code    : {resp.status_code}")
		print (f"Error message : {resp.text}")
		return None

def payInvoice(sender, receiver, invoice, msats):
	"""
	Pay invoice from sender to receiver

	Args:
		sender (dict): a sender's wallet name and apikey
		receiver (dict): a receiver's wallet name and apikey
		invoice (str): bolt11 invoice
		msats (int): milli sats (1 mats == 1000 msats)
	Returns:
		bolt11 invoice (str) if error None
	"""
	api = os.environ["LNBITS_URL"] + "/api/v1/payments"

	headers = {"X-Api-Key": sender["apikey"]}
	sats = msats/1000
	memo = f"Sender ({sender['walletname']} sends {sats} sats to {receiver['walletname']})"


	params = {"out": True, "bolt11": invoice, "memo": memo}
	resp = requests.post(api, headers=headers, json=params)
	return resp.status_code == 201

def run():
	if os.environ["LNBITS_URL"] == "" or \
		os.environ["LNBITS_ADMIN_API_KEY"] == "" or \
		os.environ["LNBITS_USER_API_KEY"] == "":
		print ("Set variables first!")
		return

	SATS = 1

	#1. get wallets from LNbits
	wallets = getWallets()
	print ("wallets: ")
	pprint (wallets)

	#2. handle invoices
	sender = {"walletname": "Admin", "apikey": os.environ["LNBITS_ADMIN_API_KEY"]}
	receiver = {"walletname": "User", "apikey": os.environ["LNBITS_USER_API_KEY"]}

	balance = getWalletBalance(os.environ["LNBITS_USER_API_KEY"])
	print ("balance of user before receiving sats from admin: ", balance)
	paymentHash = createInvoice(receiver, SATS)
	print ("payment hash: ", paymentHash)
	invoice = getInvoice(receiver, paymentHash)
	print ("bolt11 invoice: ", invoice)
	isPaid = payInvoice(sender, receiver, invoice, SATS)
	print ("pay invoice result ", isPaid)
	balance = getWalletBalance(os.environ["LNBITS_USER_API_KEY"])
	print ("balance of user after receiving sats from admin: ", balance)
	
if __name__ == "__main__":
	os.environ["LNBITS_URL"] = "http://localhost:3007"
	os.environ["LNBITS_ADMIN_API_KEY"] = ""
	os.environ["LNBITS_USER_API_KEY"] = ""

	run()
