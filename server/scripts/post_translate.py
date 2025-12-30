import urllib.request, json, urllib.error, sys

data = json.dumps({"text": "h3Llo"}).encode()
req = urllib.request.Request(
    "http://localhost:5000/api/translate",
    data=data,
    headers={"Content-Type": "application/json"}
)

try:
    res = urllib.request.urlopen(req)
    print(res.read().decode())
except urllib.error.HTTPError as e:
    print("HTTP", e.code)
    print(e.read().decode())
except Exception as e:
    print("ERROR:", e)
    sys.exit(1)