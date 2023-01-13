import requests
from flask import abort
class Museum_api():
    def get_uri(self):
        """
        Get uri for Museum Api
        :return: string
        """
        return 'https://collectionapi.metmuseum.org/public/collection/v1/'


    def get_departments(self):
        """
        Get all departments available in Metropolitan Museum of Arts NY
        :return: dict
        """
        try:
            r = requests.get(self.get_uri() + 'departments')
            return r
        except requests.exceptions.Timeout:
            abort(408, 'Museum Api - Timeout Error')
        except requests.exceptions.ConnectionError:
            abort(504, 'Museum Api - Error Connection')
        except requests.exceptions.HTTPError:
            abort(504, 'Museum Api - Http Error')
        except requests.exceptions.RequestException:
            abort(504, 'Museum Api - Other Error')


    def get_objects(self, departmentIds=None):
        """
        Get all id of arts for selected department id
        :param departmentIds: Integer
        :return: list
        """
        try:
            query = {}
            if departmentIds:
                query['departmentIds'] = departmentIds
            r = requests.get(self.get_uri() + 'objects', params=query)
            return r
        except requests.exceptions.Timeout:
            abort(408, 'Museum Api - Timeout Error')
        except requests.exceptions.ConnectionError:
            abort(504, 'Museum Api - Error Connection')
        except requests.exceptions.HTTPError:
            abort(504, 'Museum Api - Http Error')
        except requests.exceptions.RequestException:
            abort(504, 'Museum Api - Other Error')


    def get_object(self, id):
        """
        Get all information about selected art id
        :param id: integer
        :return: dict
        """
        try:
            r =  requests.get(self.get_uri() + 'objects/' + str(id))
            return r
        except requests.exceptions.Timeout:
            abort(408, 'Museum Api - Timeout Error')
        except requests.exceptions.ConnectionError:
            abort(504, 'Museum Api - Error Connection')
        except requests.exceptions.HTTPError:
            abort(504, 'Museum Api - Http Error')
        except requests.exceptions.RequestException:
            abort(504, 'Museum Api - Other Error')
