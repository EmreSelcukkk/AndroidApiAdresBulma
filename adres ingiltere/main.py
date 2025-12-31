import requests, pandas as pd, time
from concurrent.futures import ThreadPoolExecutor, as_completed

API_KEY = "AIzaSyDGUc8tjuIR7xL66jxGDI6BRcSSGI3rDIw"

df = pd.read_excel("adres.xlsx")
companies = df["sirket"].dropna().tolist()

def process_company(c):
    queries = [
        c + " UK",
        c.replace(" LTD", "") + " UK",
        c.split("-")[0] + " UK",
        c
    ]

    found = None
    for q in queries:
        s = requests.get("https://maps.googleapis.com/maps/api/place/textsearch/json",
                         params={"query": q, "key": API_KEY}).json()
        if s["results"]:
            found = s["results"][0]
            break

    if not found:
        return None

    pid = found["place_id"]

    d = requests.get("https://maps.googleapis.com/maps/api/place/details/json",
                     params={
                         "place_id": pid,
                         "fields": "name,formatted_address,formatted_phone_number,geometry,address_components,website",
                         "key": API_KEY
                     }).json()["result"]

    city = ""
    for comp in d.get("address_components", []):
        if "postal_town" in comp["types"] or "locality" in comp["types"]:
            city = comp["long_name"]

    lat = "{:.7f}".format(d["geometry"]["location"]["lat"])
    lng = "{:.7f}".format(d["geometry"]["location"]["lng"])

    return {
        "Aranan": c,
        "Bulunan": d.get("name"),
        "Adres": d.get("formatted_address"),
        "Sehir": city,
        "Telefon": d.get("formatted_phone_number"),
        "Website": d.get("website"),
        "Enlem": lat.replace(",", "."),
        "Boylam": lng.replace(",", ".")
    }

print("Toplam:", len(companies), "firma taraniyor...\n")

results = []
with ThreadPoolExecutor(max_workers=5) as executor:
    futures = [executor.submit(process_company, c) for c in companies]
    for f in as_completed(futures):
        r = f.result()
        if r:
            results.append(r)

pd.DataFrame(results).to_excel("sonuc.xlsx", index=False)
print("\nBITTI -> sonuc.xlsx hazir (HIZLI + WEBSITELI)")
