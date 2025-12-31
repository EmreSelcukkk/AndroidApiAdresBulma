import pandas as pd, requests, re

API_KEY = "AIzaSyDGUc8tjuIR7xL66jxGDI6BRcSSGI3rDIw"

df = pd.read_excel("sonuc.xlsx")

def reverse_area_ok(lat, lng, adres):
    try:
        r = requests.get(
            "https://maps.googleapis.com/maps/api/geocode/json",
            params={"latlng": f"{lat},{lng}", "key": API_KEY}
        ).json()

        if not r["results"]:
            return False

        real = r["results"][0]["formatted_address"].lower()
        src  = adres.lower()

        # aynı şehir veya aynı postcode bölgesi yeterli kabul edilir
        postcode_real = re.search(r"[a-z]{1,2}\d[a-z\d]?\s*\d[a-z]{2}", real)
        postcode_src  = re.search(r"[a-z]{1,2}\d[a-z\d]?\s*\d[a-z]{2}", src)

        if postcode_real and postcode_src:
            if postcode_real.group(0).replace(" ","") == postcode_src.group(0).replace(" ",""):
                return True

        # şehir tutuyorsa da doğru say
        city = src.split(",")[-2].strip()
        if city and city in real:
            return True

        return False
    except:
        return False


def score(row):
    s = 100

    sehir = str(row.get("Sehir","")).lower()
    adres = str(row.get("Adres","")).lower()
    tel   = str(row.get("Telefon",""))
    web   = str(row.get("Website","")).lower()
    name  = str(row.get("Bulunan","")).lower()
    lat   = str(row.get("Enlem")).replace(",",".")
    lng   = str(row.get("Boylam")).replace(",",".")

    if not tel.startswith(("0","44","+44")):
        s -= 10

    if sehir and sehir not in adres:
        s -= 10

    if web and not any(x in web for x in ["instagram","facebook","goo.gl","g.co"]):
        key = name.split()[0]
        if key not in web:
            s -= 10

    # GERÇEK HARİTA BÖLGE KONTROLÜ
    if not reverse_area_ok(lat, lng, adres):
        s -= 25

    return max(0, s)


def label(s):
    if s >= 75:
        return "DOGRU"
    elif s >= 50:
        return "SUPHELI"
    else:
        return "YANLIS"


df["Guven_Skoru"] = df.apply(score, axis=1)
df["Durum"] = df["Guven_Skoru"].apply(label)

df.to_excel("sonuc_kontrollu.xlsx", index=False)
print("AKILLI HARITA DOGRULAMA BITTI")
