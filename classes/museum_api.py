import requests
from flask import abort
class Museum_api():
    def get_uri(self):
        return 'https://collectionapi.metmuseum.org/public/collection/v1/'

    def get_departments(self):
        try:
            r = requests.get(self.get_uri() + 'departments')
            #r.raise_for_status()
            return r
        except requests.exceptions.HTTPError as errh:
            abort(500, description=f"Http Error: {errh}")
        except requests.exceptions.ConnectionError as errc:
            abort(500, description=f"Error Connecting: {errc}")
        except requests.exceptions.Timeout as errt:
            abort(500, description=f"Timeout Error: {errt}")
        except requests.exceptions.RequestException as err:
            abort(500, description=f"OOps: Something Else: {err}")

    def get_objects(self, departmentIds=None):
        try:
            query = {}
            if departmentIds:
                query['departmentIds'] = departmentIds
            r = requests.get(self.get_uri() + 'objects', params=query)
            #r.raise_for_status()
            return r
        except requests.exceptions.HTTPError as errh:
            abort(500, description=f"Http Error: {errh}")
        except requests.exceptions.ConnectionError as errc:
            abort(500, description=f"Error Connecting: {errc}")
        except requests.exceptions.Timeout as errt:
            abort(500, description=f"Timeout Error: {errt}")
        except requests.exceptions.RequestException as err:
            abort(500, description=f"OOps: Something Else: {err}")

    def get_object(self, id):
        try:
            r =  requests.get(self.get_uri() + 'objects/' + str(id))
            #r.raise_for_status()
            return r
        except requests.exceptions.HTTPError as errh:
            abort(500, description=f"Http Error: {errh}")
        except requests.exceptions.ConnectionError as errc:
            abort(500, description=f"Error Connecting: {errc}")
        except requests.exceptions.Timeout as errt:
            abort(500, description=f"Timeout Error: {errt}")
        except requests.exceptions.RequestException as err:
            abort(500, description=f"OOps: Something Else: {err}")








