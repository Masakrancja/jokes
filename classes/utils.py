import datetime, hashlib, sqlite3, json, re
from flask import abort
class Utils():
    def __init__(self, conn, museum_api):
        self.conn = conn
        self.museum_api = museum_api


    #Content






    def get_contents(self, objects):
        result = []
        tables_to_get = self.tables_to_content()
        try:
            cursor = self.conn.cursor()
            for object in objects:
                sql = "SELECT " + ', '.join(tables_to_get) + " FROM arts_content WHERE art_id = ?"
                sql_data = (object,)
                cursor.execute(sql, sql_data)
                row = cursor.fetchone()
                if row:
                    row = dict(row)

                    #Dodanie nazwy depatramentu
                    row['department'] = self.get_department_name_from_id(row['department_id'])

                    #dodanie hasha
                    row['hash'] = self.get_hash_art(object, row['department_id'])

                    result.append(row)
            return result
        except sqlite3.Error as err:
            abort(500, description="Error database - get_contents")

    def tables_to_content(self):
        return ['isHighlight', 'accessionYear', 'primaryImageSmall', 'objectName', 'title', 'culture',
                'period', 'dynasty', 'reign', 'portfolio', 'artistRole', 'artistDisplayName',
                'artistDisplayBio', 'artistNationality', 'artistBeginDate', 'artistEndDate',
                'artistGender', 'artistWikidata_URL', 'artistULAN_URL', 'medium', 'dimensions',
                'creditLine', 'city', 'state', 'county', 'country', 'classification',
                'linkResource', 'repository', 'objectURL', 'department_id', 'art_id']

    def tables_which_need_names(self):
        tables = self.tables_to_content()
        del tables[tables.index('isHighlight')]
        del tables[tables.index('title')]
        del tables[tables.index('department_id')]
        del tables[tables.index('primaryImageSmall')]
        del tables[tables.index('art_id')]
        return tables

    def tables_to_update(self):
        return ['isHighlight', 'accessionYear', 'primaryImage', 'primaryImageSmall', 'additionalImages',
                'objectName', 'title', 'culture', 'period', 'dynasty', 'reign', 'portfolio', 'artistRole',
                'artistDisplayName', 'artistDisplayBio', 'artistNationality', 'artistBeginDate',
                'artistEndDate', 'artistGender', 'artistWikidata_URL', 'artistULAN_URL', 'medium',
                'dimensions', 'creditLine', 'city', 'state', 'county', 'country', 'classification',
                'linkResource', 'metadataDate', 'repository', 'objectURL', 'department_id', 'updated_at']

    def get_human_name(self, name):
        name = re.sub(r'([a-z])([A-Z])', r'\1 \2', name)
        return name[0:1].upper() + name[1:] + ':'

    def is_link(self, text):
        result = re.match(r'^https?://', str(text))
        if result and result.span():
            return True
        return False



    def get_pages_count(self, department_id, max_for_page):
        try:
            cursor = self.conn.cursor()
            sql = "SELECT COUNT(id) AS c FROM arts WHERE department_id = ?"
            sql_data = (department_id,)
            cursor.execute(sql, sql_data)
            result = cursor.fetchone()
            if max_for_page == 0:
               max_for_page = 10
            pages =  result['c'] // max_for_page
            if (result['c'] % max_for_page) > 0:
                pages += 1
            return pages
        except sqlite3.Error as err:
            abort(500, description="Error database - get_pages_count")

    def get_pagination(self, dep_uri, page, pages, max_pages):
        pagination = {}
        if page > 0:
            pagination['prev'] = {'dep_uri': dep_uri, 'page': page - 1, 'disable': 0}
        else:
            pagination['prev'] = {'dep_uri': dep_uri, 'page': None, 'disable': 1}
        if page < pages:
            pagination['next'] = {'dep_uri': dep_uri, 'page': page + 1, 'disable':0}
        else:
            pagination['next'] = {'dep_uri': dep_uri, 'page': None, 'disable':1}
        if pages < max_pages:
            tab_range = range(1, pages + 1)
        else:
            if (pages - page) > max_pages:
                tab_range = range(page, max_pages + page + 1)
            else:
                tab_range = range(page, pages + 1)
        for item in tab_range:
            pagination[item] = {'dep_uri': dep_uri, 'page':item, 'disable': 0}
        return pagination

    def get_contents_from_user(self, objects, user_id):
        pass