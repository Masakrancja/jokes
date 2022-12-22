import requests

class Humor_api:
    def __init__(self, token):
        self.token = token

    def get_uri(self):
        return 'https://api.humorapi.com/'

    def get_jokes(self, offset=0, include_tags=None, exclude_tags=None, keywords=None):
        query = {}
        query['api-key'] = self.token
        query['offset'] = offset
        if include_tags:
            query['include-tags'] = include_tags
        if exclude_tags:
            query['exclude-tags'] = exclude_tags
        if keywords:
            query['keywords'] = keywords
        return requests.get(self.get_uri, params=query)


