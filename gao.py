from urllib.parse import urljoin
import requests
import json


API_URL = "https://api.travis-ci.org/"
HEADERS = {
    "Travis-API-Version": "3",
    "User-Agent": "API Explorer",
    "Authorization": "token N9tSAOr_nt4TjbsRId_ddA"
}


def main():
    sess = requests.Session()
    resp = sess.get(urljoin(API_URL, "builds"), headers=HEADERS)
    print(resp.status_code)
    if resp.status_code == 200:
        resp_json = json.loads(resp.text)
        print(resp_json)


if __name__ == '__main__':
    main()
