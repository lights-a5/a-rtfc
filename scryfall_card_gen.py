import os, json, zlib, csv, copy, datetime
import re
import requests
from urllib.request import urlretrieve


# Download the latest cards.json from wizards

CDN_URL = "https://assets.mtgarena.wizards.com"
VERSION_URL = "https://mtgarena.downloads.wizards.com/Live/Windows32/version"

def get_arena_version():
    """
    This function is used to get the current arena version from 
    Wizards.
    :returns Latest version of Arena. 0.0.0.0 if there is an error.
    """
    print("Getting Version Info from {}".format(VERSION_URL))
    version_info_response = requests.get(VERSION_URL)
    if not version_info_response:
        print("Failure! Could not get info from {}".format \
          (VERSION_URL))
        print("Status Code: {}".format \
          (version_info_response.status_code))
        return "0.0.0.0"
    version_info = version_info_response.json()
    latest_date = datetime.datetime(2010, 1, 1)
    latest_version = "0"
    for version, release_date in version_info["Versions"].items():
        release_date = datetime.datetime.strptime \
            (release_date, "%m/%d/%y")
        if release_date > latest_date:
            latest_version = version
            latest_date = release_date
    return latest_version

def get_json_asset(asset_url, asset_name = "file"):
    """
    This function takes a URL of a JSON asset that would return a
    compressed file, decompresses it, and returns it.
    :param asset_url: URL of the compressed JSON asset.
    :returns The JSON asset as a dict. In case of error, it will be
    {"error_message": "string" , "status_code": int}
    """
    print("Getting {} at {}".format(asset_name, asset_url))
    asset_response = requests.get(asset_url)
    if asset_response:
        try:
            decompressed_file = zlib.decompress( \
            asset_response.content, 16+zlib.MAX_WBITS) \
            .decode('utf-8')
            json_asset = json.loads(decompressed_file)
            print("Success")
            return json_asset
        except zlib.error:
          return {"error_message": "Problems decompressing" \
                  , "status_code": asset_response.status_code}
        except json.JSONDecodeError:
          return {"error_message": "Problems decoding from JSON" \
                  , "status_code": asset_response.status_code}
        except:
            return {"error_message": "Unknown Error" \
                  , "status_code": asset_response.status_code}
    return {"error_message": "Error getting from URL" \
            ,"status_code": asset_response.status_code}

def get_manifest(version):
    """
    This function is used to get the manifest of the assets available
    from the Wizards API.
    :param version: The current version of Arena.
    :returns Uncompressed Dictionary of the Manifest. If errors occur,
    a dictionary with {"error_message": string, "Code": int} is returned.
    """
    #Need to format the version to XXXX_XXXXXX
    version = re.search(r'\d{4}.\d{6}', version).group()
    version = version.replace(".", "_")
    manifest_info_url = "{}/External_{}.mtga".format(CDN_URL, version)
    print("Getting Manifest info from {}".format(manifest_info_url))
    external_mtga = requests.get(manifest_info_url)
    if not external_mtga:
        print("Failure! Could not get manifest info from {}".format \
          (manifest_info_url))
        print("Status Code: {}".format(external_mtga.status_code))
        return {"Error": "Could not get manifest info",
                "Code": external_mtga.status_code}
    manifest_text = external_mtga.text.strip()
    manifest_url = "{}/Manifest_{}.mtga".format(CDN_URL, manifest_text)
    manifest_mtga_json = get_json_asset(manifest_url)
    return manifest_mtga_json



VERSION = get_arena_version()
MANIFEST = get_manifest(VERSION)
ASSETS_NEEDED = ["data_cards", "data_loc"]

for asset in MANIFEST ["Assets"]:
    if not ASSETS_NEEDED:
        break
    if asset["Name"].startswith("data_cards"):
        cards_url ="{}/{}".format(CDN_URL, asset["Name"])
        cards_list = get_json_asset(cards_url)
        if "error_message" in cards_list:
            print(cards_list)
        ASSETS_NEEDED.remove("data_cards")
    if asset["Name"].startswith("data_loc"):
        loc_url = "{}/{}".format(CDN_URL, asset["Name"])
        loc_list = get_json_asset(loc_url)
        if "error_message" in loc_list:
            print(loc_list)
        ASSETS_NEEDED.remove("data_loc")

with open('cards.json', 'w+') as outfile:
    json.dump(cards_list, outfile)

with open('loc.json', 'w+') as outfile:
    json.dump(loc_list, outfile)
    
"""
loc = {}
for l in loc_list:
  if l["isoCode"] == "en-US":
    for v in l["keys"]:
      loc[v["id"]] = v["text"]
  else:
    print(l["isoCode"])

toPrint = []
for c in cards_list:
  if c["set"] == "ANA":
    toPrint.append(c)
toPrint.sort(key=lambda c: int(c["CollectorNumber"] or "0"))

for c in toPrint:
  typ = loc[c["cardTypeTextId"]]
  if c["subtypeTextId"] != 0:
    typ += " - " + loc[c["subtypeTextId"]]
  print(c["CollectorNumber"],":", loc[c["titleId"]], "---", typ)
  for a in c["abilities"]:
    print("\t", loc[a["textId"]])
"""

# Map from Arena set name -> Scryfall set name
set_overrides = {"DAR": "dom"}

# Map from Scryfall language code -> Twitch language code
languages = {
    "en": "en",  # English
    "es": "es",  # Spanish
    "fr": "fr",  # French
    "de": "de",  # German
    "it": "it",  # Italian
    "pt": "pt",  # Portuguese
    "ja": "ja",  # Japanese
    "ko": "ko",  # Korean
    "ru": "ru",  # Russian
    # Twitch just gives us "zh" for both, so just use Simplified
    "zhs": "zh",  # Simplified Chinese
    # #"zht": "zh", # Traditional Chinese
}


def convert(o):
    image_uris = ""
    if "image_uris" in o:
        image_uris = [o["image_uris"]]
    elif "card_faces" not in o:
        image_uris = ""
    else:
        image_uris = [cf["image_uris"] for cf in o["card_faces"]]
    return {
        "ScryfallID": o["id"],
        "Set": o["set"],
        "CollectorNumber": o["collector_number"],
        "Name": o["name"],
        "Rarity": o["rarity"],
        "CMC": str(int(o["cmc"])),
        "Colors": "".join(o["color_identity"]),
        "DualSided": str(o["layout"] in ("transform",)).lower(),
        "Images": image_uris
    }


# Load data about cards we've seen before
cards_db = {}
scryfall_data = requests.get(
    "https://archive.scryfall.com/json/scryfall-all-cards.json?{}".format(
        datetime.datetime.today().timestamp()
    )
).json()
for o in scryfall_data:
    if o["object"] != "card" or "arena_id" not in o:
        continue
    cards_db[(o["set"], o["collector_number"], o["lang"])] = convert(o)

# Download the latest cards.json from wizards
""" CDN_URL = "http://mtga-assets.dl.wizards.com"

version = sys.argv[1].strip("v")
if version == "":
    sys.exit("usage: python cards.py <mtga version>")

external_mtga = requests.get("{}/External_{}.mtga".format(CDN_URL, version))
manifest_mtga = requests.get(
    "{}/Manifest_{}.mtga".format(CDN_URL, external_mtga.text.strip())
)
manifest_mtga_json = json.loads(
    zlib.decompress(manifest_mtga.content, 16 + zlib.MAX_WBITS).decode("utf-8")
)

bundles = {"data_cards": None, "data_loc": None}

for a in manifest_mtga_json["Assets"]:
    for k in bundles.keys():
        if a["Name"].startswith(k):
            d = requests.get("{}/{}".format(CDN_URL, a["Name"]))
            buf = io.BytesIO(zlib.decompress(d.content, 16 + zlib.MAX_WBITS))
            buf.name = a["Name"]
            bundles[k] = unitypack.load(buf)

for (k, v) in bundles.items():
    if v is None:
        sys.exit("Could not find {} bundle".format(k))

cards_list = json.loads(
    list(bundles["data_cards"].assets[0].objects.values())[1].read().bytes
)
loc_list = json.loads(
    list(bundles["data_loc"].assets[0].objects.values())[0].read().bytes
)

with open("cards.json", "w") as f:
    f.write(json.dumps(cards_list)) """

cards_list = []
with open("cards.json", "r") as f:
    cards_list = json.load(f)

loc_list = []
with open("loc.json", "r") as f:
    loc_list = json.load(f)

loc = {}
for l in loc_list:
    if l["isoCode"] == "en-US":
        for v in l["keys"]:
            loc[v["id"]] = v["text"]

# Download images
failed = []
all_cards = []
all_all_cards = []


def dl(url, path):
    return
    try:
        urlretrieve(url, path)
        print("{} => {}".format(url, path))
    except:
        print("{} ... FAILED!".format(url))


for card in cards_list:
    id = str(card["grpid"])
    if card["CollectorNumber"] != "":
        _set = ("t" if card["isToken"] else "") + set_overrides.get(
            card["set"], card["set"].lower()
        )
        _num = card["CollectorNumber"]
        if _set == "tana":
            _set = "ana"
            _num = "T" + _num
        if _num.startswith("GR"):
            _set = "med"

        for [slang, tlang] in languages.items():
            c = cards_db.get((_set, _num, slang))
            if c is None:
                if slang != "en":
                    failed.append((slang, _set, _num, card["titleId"]))
                    continue

                print(
                    "{}/{}/{} isn't in the database, fetching from the API...".format(
                        _set, _num, slang
                    )
                )
                r = requests.get(
                    "https://api.scryfall.com/cards/{}/{}/{}".format(_set, _num, slang),
                    timeout=10,
                )
                if r.status_code == requests.codes.ok:
                    c = convert(r.json())
                else:
                    failed.append((slang, _set, _num, card["titleId"]))
                    continue

            cc = copy.copy(c)
            cc["ArenaID"] = id
            cc["lang"] = tlang
            all_all_cards.append(cc)
            if tlang == "en":
                all_cards.append(cc)

            folder = "cards/{}/{:02d}".format(tlang, int(id) % 20)
            if not os.path.exists(folder):
                os.makedirs(folder)

            for (images, path) in zip(
                c["Images"],
                ["{}/{}.jpg".format(folder, id), "{}/{}_back.jpg".format(folder, id)],
            ):
                if not os.path.exists(path):
                    dl(images["normal"], path)


# Update card db in client application
with open("client/src/main/cards.js", "w") as f:
    f.write("const AllCards = new Map([\n")
    for d in sorted(all_cards, key=lambda c: c["ArenaID"]):
        f.write(
            '\t[{ArenaID}, {{ID: "{ArenaID}", name: "{Name}", set: "{Set}", number: "{CollectorNumber}", color: "{Colors}", rarity: "{Rarity}", cmc: {CMC}, dualSided: {DualSided}}}],\n'.format(
                **d
            )
        )
    f.write("])\n\nexport default AllCards\n")

with open("api/cards.js", "w") as f:
    f.write("const Cards = new Map([\n")
    for d in sorted(all_all_cards, key=lambda c: c["ArenaID"]):
        f.write(
            '\t["{ArenaID}-{lang}", {{ID: "{ArenaID}", name: "{Name}", set: "{Set}", number: "{CollectorNumber}", color: "{Colors}", rarity: "{Rarity}", cmc: {CMC}, dualSided: {DualSided}, images: {Images}}}],\n'.format(
                **d
            )
        )
    f.write("])\n\nmodule.exports = Cards\n")

from collections import defaultdict

failedcsv = defaultdict(list)
for (lang, set, cid, tid) in failed:
    failedcsv[(set, cid, tid)].append(lang)

with open("cards.missing.csv", "w") as f:
    w = csv.writer(f)
    w.writerow(["set", "cid", "languages"])
    for k, v in failedcsv.items():
        w.writerow([k[0], k[1], " ".join(v)])
        if "en" in v:
            print("Missing card in english:", k[0], k[1], loc[k[2]])