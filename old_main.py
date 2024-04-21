# %%
import pickle

countries_suffixes = pickle.load(open("prefixes.p", 'rb'))

# %% 
from graphql_apis import Api
import requests
import sys

def get_offers_from_node(node, monetization_types: list[str] = None) -> list:
    """Returns a list of offers from a node."""
    if node["__typename"] != "Movie":
        print("Not a movie node, unsupported", file=sys.stderr)
        return []
    
    offers = node["offers"]
    if monetization_types:
        offers = [offer['package'] for offer in offers if offer["monetizationType"] in monetization_types]

    # remove duplicate packages
    packages = set()
    final_offers = []
    for offer in offers:
        package_id = offer["technicalName"]
        if package_id not in packages:
            final_offers.append(offer)
        packages.add(package_id)
    
    return [final_offers['clearName'] for final_offers in final_offers]
        


api = Api(session=requests.Session())
country = "IT"
id = api.get_url("Molly's game", country=country)['id']
node = api.get_movie_node(id, country=country)
get_offers_from_node(node, ["FLATRATE", "ADS"])
# %%

selected_countries = ["DE", "FR", "GB", "IT", "ES", "US", "NL", "CH", "PT"]
countries_list = [c.split("/")[1].upper() for c in countries_suffixes]
movie_name = "Spotlight"
for country in selected_countries:
    url = api.get_url(movie_name, country=country)
    if url is None:
        continue
    id = url['id']
    node = api.get_movie_node(id, country=country)
    print(f'{country}: {get_offers_from_node(node, "FLATRATE")}')
# %%
for country in countries_list:
    url = api.get_url(movie_name, country=country)
    if url is None:
        continue
    id = url['id']
    node = api.get_movie_node(id, country=country)
    print(f'{country}: {get_offers_from_node(node, "FLATRATE")}')
# %%
import csv

file_path = "watchlist.csv"
with open(file_path, 'r') as csv_file:
    csv_reader = csv.reader(csv_file)
    i = 0
    for row in csv_reader:
        if i > 5:
            break
        print(row)
        i += 1

# %%
def get_watchlist_names(file_path: str):
    with open(file_path, 'r') as csv_file:
        csv_reader = csv.reader(csv_file)
        return [row[1] for row in csv_reader][1:]
    
watchlist = get_watchlist_names(file_path)

# %%
import time

with open("availability.txt", 'w') as availability_file:
    for movie_name in watchlist:
        availability_file.write(f"{movie_name}: ")
        # here we search only in Italy
        url = api.get_url(movie_name, country="IT")
        if url is None:
            availability_file.write("not found\n")
            continue
        id = url['id']
        node = api.get_movie_node(id, country="IT")
        # print(get_offers_from_node(node, "FLATRATE"))
        availability_file.write(f"{get_offers_from_node(node, ['FLATRATE', 'ADS'])}\n")
        time.sleep(0.5)

# %%
node
# %%
