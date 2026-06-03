import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

headers = {
    "User-Agent": "Mozilla/5.0",
    "Referer": "https://il.raceview.net/"
}

queries = [
    "https://il.raceview.net/search?q=בועז בילגורי",
    "https://il.raceview.net/api/search?q=בועז בילגורי",
    "https://il.raceview.net/query?q=בועז בילגורי",
]

for url in queries:
    try:
        r = requests.get(
            url,
            headers=headers,
            verify=False,   # <----
            timeout=20
        )

        print("\nURL:", url)
        print("STATUS:", r.status_code)
        print(r.text[:500])

    except Exception as e:
        print(e)