import csv
import sys
import requests
import argparse
from graphql_apis import Api

def get_offers_from_node(node, monetization_types: list[str] = None) -> dict:
    """Returns a dictionary of offers from a node, keyed by streaming service."""
    if node["__typename"] != "Movie":
        print("Not a movie node, unsupported", file=sys.stderr)
        return {}
    
    offers = node["offers"]
    if monetization_types:
        offers = [offer for offer in offers if offer["monetizationType"] in monetization_types]

    # Organize offers by streaming service
    service_offers = {}
    for offer in offers:
        service_name = offer["package"]["clearName"]
        service_offers.setdefault(service_name, []).append(offer["package"]["clearName"])

    return service_offers

def get_watchlist_names(file_path: str):
    with open(file_path, 'r') as csv_file:
        csv_reader = csv.reader(csv_file)
        return [row[1] for row in csv_reader]  # Assumes movie names are in the second column

def output_data(data, output=None):
    if output:
        with open(output, 'a') as f:
            f.write(data + "\n")
    else:
        print(data)

def main(args):
    watchlist = get_watchlist_names(args.file_path)
    api = Api(session=requests.Session())
    country = args.country.upper()
    specified_services = args.streaming_services.split(',') if args.streaming_services else []

    service_dict = {}
    for movie_name in watchlist:
        url = api.get_url(movie_name, country=country)
        if url is None:
            continue
        id = url['id']
        node = api.get_movie_node(id, country=country)
        offers = get_offers_from_node(node, args.monetization_types.split(","))
        
        if args.by_service:
            for service in offers:
                if not specified_services or service in specified_services:
                    service_dict.setdefault(service, []).append(movie_name)
        else:
            output_data(f"{movie_name}: {[o for o in offers.keys()]}", args.output)

    if args.by_service:
        for service, movies in service_dict.items():
            output_data(f"{service}: {movies}", args.output)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Check movie availability on streaming services.")
    parser.add_argument("file_path", type=str, help="Path to the CSV file containing the watchlist")
    parser.add_argument("--country", type=str, default="IT", help="Country code to check availability (default: IT)")
    parser.add_argument("--monetization_types", type=str, default="FLATRATE,ADS", help="Comma-separated monetization types to filter offers (default: FLATRATE,ADS)")
    parser.add_argument("--output", type=str, help="File path to write the output to. If not specified, output will be printed to stdout.")
    parser.add_argument("--streaming_services", type=str, default="", help="Comma-separated list of streaming services to check. If empty, checks all found services.")
    parser.add_argument("--by_service", action='store_true', help="Output availability grouped by streaming service instead of by movie.")
    args = parser.parse_args()

    main(args)
