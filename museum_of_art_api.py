import requests
class Museum_api:
    def get_uri(self):
        return 'https://collectionapi.metmuseum.org/public/collection/v1/'

    def get_departments(self):
        print(self.get_uri())
        return requests.get(self.get_uri() + 'departments')

    def get_objects(self, departmentIds=None):
        query = {}
        if departmentIds:
            query['departmentIds'] = departmentIds
        return requests.get(self.get_uri() + 'objects', params=query)

    def get_object(self, id):
        return requests.get(self.get_uri() + 'objects/' + str(id))




if __name__ == '__main__':
    museum_api = Museum_api()
    #r = museum_api.get_departments()
    #r = museum_api.get_objects(1)
    r = museum_api.get_object(214)


    print(r.url)
    print(r.text)
    print(r.status_code)




