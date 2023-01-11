import sqlite3
from flask import abort
class Pages:
    def __init__(self, conn):
        self.conn = conn


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
            abort(500, description=f"Error database - get_pages_count {err}")


    def get_user_pages_count(self, user_id, department_id, max_for_page):
        try:
            cursor = self.conn.cursor()
            sql = "SELECT COUNT(user_arts.id) as c FROM user_arts LEFT JOIN arts ON user_arts.art_id = arts.art_id " \
                  "WHERE user_arts.user_id = ? and arts.department_id = ?"
            sql_data = (user_id, department_id)
            cursor.execute(sql, sql_data)
            result = cursor.fetchone()
            if max_for_page == 0:
                max_for_page = 10
            pages = result['c'] // max_for_page
            if (result['c'] % max_for_page) > 0:
                pages += 1
            return pages
        except sqlite3.Error as err:
            abort(500, description=f"Error database - get_user_pages_count {err}")


    def get_pagination(self, dep_uri, page, pages, max_pages, me):
        pagination = {}
        if pages <= 1:
            return pagination
        #prev
        if page > 1:
            pagination['prev'] = {'dep_uri': dep_uri, 'page': page - 1, 'disable': 0, 'me': me}
        else:
            pagination['prev'] = {'dep_uri': dep_uri, 'page': 1, 'disable': 1, 'me': me}

        #next
        if page < pages:
            pagination['next'] = {'dep_uri': dep_uri, 'page': page + 1, 'disable': 0, 'me': me}
        else:
            pagination['next'] = {'dep_uri': dep_uri, 'page': pages, 'disable': 1, 'me': me}

        if pages <= max_pages:
            tab_range = range(1, pages + 1)
        else:
            if (pages - page) > max_pages:
                tab_range = range(page, max_pages + page)
            else:
                tab_range = range(page, pages + 1)
        for item in tab_range:
            pagination[item] = {'dep_uri': dep_uri, 'page': item, 'disable': 0, 'me': me}

        return pagination

