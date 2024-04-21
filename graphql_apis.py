# Copyright 2023 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Code that uses JustWatch's API.

There doesn't seem to be much documentation of the API, but
https://github.com/dawoudt/JustWatchAPI shows some ways it can be used. This
file does not use that library because 1) the library doesn't seem to add much
value over doing plain REST calls, so it's probably not worth the extra
dependency, and 2) the library doesn't give enough control over the HTTP calls
to enable useful things like caching and retrying specific errors.
"""

import collections
from collections.abc import Collection, Generator, Iterable, Mapping, Set
from typing import Any

import dateutil.parser
import requests


_GRAPHQL_URL = "https://apis.justwatch.com/graphql"

class Api:
    """Wrapper around JustWatch's GraphQL API."""

    def __init__(
        self,
        *,
        session: requests.Session,
    ) -> None:
        self._session = session

        # While this cache *might* help with performance, the main reason to use
        # one here is to avoid race conditions. Without this, if a report were
        # generated around the time that data was expiring from the requests
        # cache, it would be possible for a section with {"justwatch": ...} and
        # another with {"not": {"justwatch": ...}} to either both match the same
        # media item or neither match the item. This cache makes sure that those
        # two filters see identical data, so that the mutual exclusion can be
        # preserved. NOTE: If this code is ever used in a long-running process,
        # this might need more work to avoid stale data.
        self._node_id_by_url_path: dict[str, str] = {}
        self._node_by_id_by_country: (
            dict[str, dict[str, Any]]
        ) = collections.defaultdict(dict)

    def query(
        self,
        document: str,
        *,
        operation_name: str,
        variables: Mapping[str, Any],
    ) -> Any:
        """Returns the result of a GraphQL query operation.

        Args:
            document: GraphQL document with at least one query.
            operation_name: Name of the query in the document to use.
            variables: Variables for the query.
        """
        response = self._session.post(
            _GRAPHQL_URL,
            json={
                "query": document,
                "operationName": operation_name,
                "variables": variables,
            },
        )
#        with exceptions.add_note(f"Response body: {response.text}"):
#            response.raise_for_status()
        response_json = response.json()
        if "errors" in response_json:
            print(f"GraphQL query failed: {response_json}")
        return response_json

    def providers(self, *, country: str) -> Mapping[str, str]:
        """Returns a mapping from technical name to human-readable name."""
        result = self.query(
            """
            query GetProviders($country: Country!) {
                packages(
                    country: $country
                    platform: WEB
                    includeAddons: true
                ) {
                    technicalName
                    clearName
                }
            }
            """,
            operation_name="GetProviders",
            variables={"country": country},
        )
        return {
            package["technicalName"]: package["clearName"]
            for package in result["data"]["packages"]
        }

    def monetization_types(self, *, country: str) -> Collection[str]:
        """Returns the monetization types."""
        result = self.query(
            """
            query GetMonetizationTypes($country: Country!) {
                packages(
                    country: $country
                    platform: WEB
                    includeAddons: true
                ) {
                    monetizationTypes
                }
            }
            """,
            operation_name="GetMonetizationTypes",
            variables={"country": country},
        )
        monetization_types: set[str] = set()
        for package in result["data"]["packages"]:
            monetization_types.update(
                monetization_type.lower()
                for monetization_type in package["monetizationTypes"]
            )
        return monetization_types

    def get_movie_node(self, node_id: str, country: str) -> Any:
        """Returns a node (e.g., movie or TV show)."""
        query_document = """
        fragment Movie on Movie {
            __typename
            id
            offers(country: $country, platform: WEB) {
                monetizationType
                availableToTime
                availableFromTime
                package {
                    clearName
                    technicalName
                }
            }
        }

        fragment Node on Node {
            __typename
            id
            ...Movie
        }

        query GetNodeById($nodeId: ID!, $country: Country!) {
            node(id: $nodeId) {
                ...Node
            }
        }
        """
        
        node = self.query(
            query_document,
            operation_name="GetNodeById",
            variables={
                "nodeId": node_id,
                "country": country,
            },
        )["data"]["node"]
        return node

    # new functionalities

    def get_url(self, search_term: str, country: str):
        """Returns the url of a movie or TV show."""
        query_document = """
            query GetSuggestedTitles($country: Country!, $first: Int!, $filter: TitleFilter) {
            popularTitles(country: $country, first: $first, filter: $filter) {
                edges {
                node {
                    ...SuggestedTitle
                    __typename
                }
                __typename
                }
                __typename
            }
            }

            fragment SuggestedTitle on MovieOrShow {
            id
            objectType
            objectId
            content(country: $country, language: "it") { #TODO: language
                fullPath
                title
                # originalReleaseYear
                # posterUrl
                # fullPath
                __typename
            }
            __typename
            }
        """
        result = self.query(
            query_document,
            operation_name="GetSuggestedTitles",
            variables={
                "country": country,
                "first": 1, # only return the first result
                "filter": {"searchQuery": search_term},
            },
        )

        node = None
        try:
            node = result['data']['popularTitles']['edges'][0]['node']
        except Exception as e:
            return None
        return node
