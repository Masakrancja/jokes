import requests
class Museum_api():
    def get_uri(self):
        return 'https://collectionapi.metmuseum.org/public/collection/v1/'

    def get_departments(self):
        return requests.get(self.get_uri() + 'departments')

    def get_objects(self, departmentIds=None):
        query = {}
        if departmentIds:
            query['departmentIds'] = departmentIds
        return requests.get(self.get_uri() + 'objects', params=query)

    def get_object(self, id):
        return requests.get(self.get_uri() + 'objects/' + str(id))




