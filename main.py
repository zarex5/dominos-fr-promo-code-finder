import requests
from time import sleep
import json
import sys
import yaml


def execute_request(code):
	req = requests.post(URL + code, headers=HEADERS)
	content = json.loads(req.text)["Messages"]
	sleep(INTERVAL)
	return content


def display_results(found_codes):
	if not found_codes:
		print("§ Recherche terminée, aucun code trouvé.")
	else:
		print("§ Recherche terminée, codes trouvés:")
		print(", ".join(found_codes))


def search_within(file):
	file = open(file, "r")
	lines = file.read().count('\n') + 1
	file.seek(0, 0)
	i = 0
	found_codes = []
	actual_category = "default"
	for code in file:
		i += 1
		if code.startswith("#"):
			actual_category = code[1:].rstrip().lower()
			continue

		code = code.rstrip()
		content = execute_request(code)

		if (content is None) or ("trop de coupons" in content[0]):
			print("+ " + code + "(from " + actual_category + ")")
			found_codes.append(code)
		if i != 0 and i % STEP == 0:
			print("# " + str(i) + "/" + str(lines))

	display_results(found_codes)


def test_all():
	found_codes = []
	for i in range(10000):
		code = '{0:04}'.format(i)
		content = execute_request(code)

		if (content is None) or ("trop de coupons" in content[0]):
			print("+ " + code)
			found_codes.append(code)
		if i != 0 and i % STEP == 0:
			print("# " + str(i) + "/9999")

	display_results(found_codes)


def verify_cookie():
	must_contain = ["StoreNumber", "ServiceMethod", "Language", "OrderTime", "MenuHash", "Menus", "OfferHash", "SeenOffers"]
	for item in must_contain:
		if item not in COOKIE:
			sys.exit("Cookie invalide")

	store = COOKIE.split('StoreNumber=')[1].split(';')[0]
	method = COOKIE.split('ServiceMethod=')[1].split(';')[0]
	time = COOKIE.split('OrderTime=')[1].split(';')[0]

	print("Cookie valide (StoreNumber: {0}, ServiceMethod: {1}, OrderTime: {2})".format(store, method, time))


if __name__ == '__main__':
	print("###############################################################")
	print("#                dominos-fr-promo-code-finder                 #")
	print("###############################################################")

	with open("config.yml", 'r') as ymlfile:
		cfg = yaml.load(ymlfile, Loader=yaml.SafeLoader)
		URL = cfg['url']
		INTERVAL = cfg['parameters']['time_between_requests']
		STEP = cfg['parameters']['display_interval']
		CODES_FILE = cfg['filenames']['codes']
		DICTIONARY_FILE = cfg['filenames']['dictionary']

	print("Saisisez votre cookie (effectuez une requete pour l'obtenir)")
	COOKIE = input(">")

	verify_cookie()

	HEADERS = {
		'accept': '*/*',
		'accept-language': 'en-AU,en;q=0.9,fr-FR;q=0.8,fr;q=0.7,en-US;q=0.6,la;q=0.5',
		'content-length': '0',
		'origin': 'https://commande.dominos.fr',
		'referer': 'https://commande.dominos.fr/eStore/fr/ProductMenu',
		'request-context': 'appId=cid-v1:834638b4-e5f3-44d9-bcb9-441adf77abb4',
		'request-id': '|gEQTD.nf5Gc',
		'user-agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:13.0) Gecko/20100101 Firefox/13.0.1',
		'x-requested-with': 'XMLHttpRequest',
		'cookie': COOKIE
	}

	while True:
		print("Menu :")
		print("1 - Recherche via liste des codes publiés sur internet")
		print("2 - Recherche via dictionaire de mots potentiels")
		print("3 - Recherche par tentative de tous les codes possibles")
		print("Q - Quitter")
		mode = input(">")

		if mode is "1":
			search_within(CODES_FILE)
		elif mode is "2":
			search_within(DICTIONARY_FILE)
		elif mode is "3":
			test_all()
		elif mode is "Q":
			sys.exit("Bye!")
		else:
			print("Mode inconnu")
