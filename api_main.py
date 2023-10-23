# %%
import pickle

countries_list = pickle.load(open("prefixes.p", 'rb'))

print(countries_list)

# %%
def get_offers(entry: dict, country: str) -> list:
    """ 
    Get the offers from the dictionary of the show
    """
    if 'offers' in entry:
        res = entry['offers']
        for el in res:
            el['country'] = country
        return res
    return []

# %% 
from justwatch import JustWatch

just_watch = JustWatch(country='IT')
providers_list = just_watch.get_providers()
providers = dict()
for provider in providers_list:
    providers[provider['id']] = provider['clear_name']
providers
# %%
countries_list = [el[1:].upper() for el in countries_list]


# %%
results = []
for c in countries_list:
    just_watch = JustWatch(country=c)
    res = just_watch.search_for_item(query="Grey's Anatomy")['items']
    if len(res) > 0:
        res = res[0]
        offers = get_offers(res, c)
        for offer in offers:
            results.append(offer)
# %%
results[1]
# %%
available_providers = dict()
for el in results:
        if el['provider_id'] in providers and el['monetization_type'] == 'flatrate':
            if el['provider_id'] not in available_providers:
                available_providers[providers[el['provider_id']]] = [el['country']]
            else:
                available_providers[providers[el['provider_id']]].append(el['country'])
available_providers
# %%
