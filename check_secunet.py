#!/usr/bin/env python3

import requests, sys, datetime, getopt, json, urllib3, base64

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

eligibleCardTypes = ['HBA', 'SMC_KT', 'SMC_B', 'SMC_K']

def main(argv):
    verify = True
    url = ""
    key = ""
    username = ""
    password = ""

    opts, args = getopt.getopt(argv, "hk:", ["url=", "username=", "password=", "disable-cert-verify"])

    for opt, arg in opts:
        if opt == '-h':
            print('check.py --url=<url> --username=<username> --password=<password> -k <key>')
            sys.exit()
        elif opt in '-k':
            eligibleKeys = ['status', 'cards', 'version', 'update-status']

            if arg not in eligibleKeys:
                print("Unknown key: " + arg)
                sys.exit()

            key = arg
        elif opt in ("--url"):
            url = arg
        elif opt in ("--username"):
            username = arg
        elif opt in ("--password "):
            password = arg
        elif opt in ("--disable-cert-verify"):
            verify = False

    token = login(url, username, password, verify)

    match key:
        case "status":
            print(json.dumps(getStatus(url, token, verify)))
        case "cards":
            print(json.dumps(getCards(url, token, verify)))
        case "version":
            print(json.dumps(getVersion(url, token, verify)))
        case "update-status":
            print(json.dumps(getUpdateStatus(url, token, verify)))

    logout(url, token, verify)

def login(url, username, password, verify):
    headers = {"Content-Type": "application/json"}

    r = requests.post(url + '/rest/mgmt/ak/konten/login', json={'username': username, 'password': password}, verify=verify, headers=headers, timeout=10)

    if r.status_code == 204:
        return r.headers.get('Authorization')

    raise Exception('Unknown error')

def logout(url, token, verify):
    headers = {"Content-Type": "application/json", "Authorization": token}

    requests.delete(url + '/rest/mgmt/ak/konten/profil/logout', verify=verify, headers=headers, timeout=10)

def getStatus(url, token, verify):
    headers = {'Authorization': token}

    r = requests.get(url + '/rest/mgmt/ak/dienste/status', headers=headers, verify=verify, timeout=10)

    if r.status_code == 200:
        json = r.json()

        return {
            "vpnTiConnected": json['vpnTiConnected'],
            "vpnTiConnectionStateDate": datetime.datetime.fromtimestamp(json['vpnTiConnectionStateDate'] / 1000).strftime('%Y-%m-%d %H:%M:%S'),
            "connectorStarted": datetime.datetime.fromtimestamp(json['connectorStarted'] / 1000).strftime('%Y-%m-%d %H:%M:%S'),
            "restartRequired": json['restartRequired'],
        }

    raise Exception('Unknown error')

def getUpdateStatus(url, token, verify):
    headers = {'Authorization': token}

    r = requests.get(url + '/rest/mgmt/ak/dienste/ksr/informationen/updates-konnektor', headers=headers, verify=verify, timeout=10)

    if r.status_code == 200:
        json = r.json()

        return {
            "lastUpdateCheck": datetime.datetime.fromtimestamp(json['lastUpdate'] / 1000).strftime('%Y-%m-%d %H:%M:%S'),
        }

    raise Exception('Unknown error')

def getVersion(url, token, verify):
    headers = {'Authorization': token}

    r = requests.get(url + '/rest/mgmt/ak/dienste/status/version', headers=headers, verify=verify, timeout=10)

    if r.status_code == 200:
        json = r.json()

        return {
            "fwVersion": json['fwVersion'],
            "hwVersion": json['hwVersion'],
            "productName": json['productName'],
            "productType": json['productType'],
            "serialNumber": json['serialNumber'],
            "buildTime": json['buildTime'],
        }

    raise Exception('Unknown error')

def getCards(url, token, verify):
    headers = {'Authorization': token}

    r = requests.get(url + '/rest/mgmt/ak/dienste/karten', headers=headers, verify=verify, timeout=10)

    if r.status_code == 200:
        cards = r.json()

        eligibleCards = []

        for card in cards:
            if card['type'] in eligibleCardTypes:
                eligibleCards.append({
                    "cardhandle": card['cardhandle'],
                    "insertTime": datetime.datetime.fromtimestamp(card['insertTime'] / 1000).strftime('%Y-%m-%d %H:%M:%S'),
                    "expirationDate": datetime.datetime.fromtimestamp(card['expirationDate'] / 1000).strftime('%Y-%m-%d %H:%M:%S'),
                    "type": card['type'],
                    "commonName": card['commonName']
                })

        return eligibleCards

    raise Exception('Unknown error')

if __name__ == "__main__":
    main(sys.argv[1:])
