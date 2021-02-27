import psycopg2
from prettytable import PrettyTable
import time
import datetime
import base64
from termcolor import colored

__author__ = 'David Alshevski'


class DBWorker:

    def __init__(self):
        self.con_db = psycopg2.connect(
            database="shop_storage",
            user="david",  # Your user
            password="davidsql"  # Your password.
        )
        self.cursor = self.con_db.cursor()
        self.result = None

    def use_query(self, query):
        self.cursor.execute(query)
        self.con_db.commit()

    def use_get_query(self, query):
        self.cursor.execute(query)
        self.result = self.cursor.fetchall()
        self.con_db.commit()

    def return_result(self):
        return self.result

    def end_proc(self):
        self.con_db.close()
        print('Database connection closed.')


class SQLHandler:

    def __init__(self):

        """ Create class instance of DBWorker. Connecting to database. """

        self.db = DBWorker()
        self.tables = [
            'products',
            'date',
            'users',
            'trash',
            'product_description',
        ]

    def get_all(self):

        """
        Get all data from table products.
        :return all data:
        """

        self.db.use_get_query('''SELECT products.id, products.name, products.cost, date.product_type, date.come_date,
         date.expiration_date FROM products JOIN date ON products.name = date.name;''')
        return self.db.return_result()

    def get_item(self, item_name):

        """
        Checks item in storage.
        :param item_name:
        :return item:
        """

        self.db.use_get_query(f'''SELECT products.id, products.name, products.cost, date.product_type, date.come_date,
                 date.expiration_date FROM products JOIN date ON products.name = date.name WHERE products.name = '{item_name}';''')
        return self.db.return_result()

    def add_description(self, name, desc):

        """
        Adds description for product.
        :return:
        """

        self.db.use_query(f"INSERT INTO product_description(name, description) VALUES ('{name}', '{desc}');")

    def add_product(self, name, cost, prod_type, exp_date):

        """
        Insert name and cost to database products.
        :param exp_date:
        :param prod_type:
        :param name:
        :param cost:
        :return:
        """

        self.db.use_query(
            f"INSERT INTO date (name,product_type,come_date,expiration_date) VALUES('{name}','{prod_type}','{datetime.date.today()}','{exp_date}');")
        self.db.use_query(f"INSERT INTO products (name,cost) VALUES('{name}', {cost});")

    def delete_description(self, name):

        """
        Deletes description from table product_description.
        :param name:
        :return:
        """

        self.db.use_query(f"DELETE FROM product_description WHERE name = '{name}';")

    def change_description(self, name, desc):

        """
        Changes description by name.
        :param name:
        :param desc:
        :return:
        """

        self.db.use_query(f"UPDATE product_description SET description = '{desc}' WHERE name = '{name}';")

    def delete_product(self, name='', product_id=0):

        """
        Delete product by name or id.
        :param name:
        :param product_id:
        :return:
        """

        if name:
            self.db.use_query(f"DELETE FROM products WHERE name = '{name}';")
            self.db.use_query(f"DELETE FROM date WHERE name = '{name}';")
        elif product_id:
            self.db.use_query(f'DELETE FROM products WHERE id = {product_id};')
            self.db.use_query(f'DELETE FROM date WHERE id = {product_id};')

    def clear_table(self, table_name: str):

        """
        Clear table with name table_name.
        Table_name is in self.tables.
        :param table_name:
        :return:
        """

        self.db.use_query(f"TRUNCATE {table_name};")

    def change_cost_of_product(self, name, cost):

        """
        Change cost of product with name.
        :param name:
        :param cost:
        :return:
        """

        self.db.use_query(f"UPDATE products SET cost = {cost} WHERE name = '{name}';")

    def update_date(self):

        """
        Updates dates in tables products, date.
        If product is out of date -> moves to the trash.
        :return:
        """

        data = self.get_all()
        today = datetime.date.today()
        for row in data:

            first_date = datetime.datetime.strptime(str(row[4]), "%Y-%m-%d")

            new_date = datetime.date(first_date.year, first_date.month, first_date.day)

            d1 = datetime.datetime.strptime(str(today), "%Y-%m-%d")
            d2 = datetime.datetime.strptime(str(new_date), "%Y-%m-%d")

            if (d1 - d2).days >= row[5] != -1:
                self.add_to_trash(row[0], row[1], row[3], row[4])

    def create_user(self, username, password, permission):

        """
        Creats user
        :param username:
        :param password:
        :param permission:
        :return:
        """

        password = base64.b64encode(bytes(password, encoding='utf-8'))
        self.db.use_query(
            f"INSERT INTO users (login, password, permissions) VALUES('{username}', '{password.decode('utf-8')}', '{permission}');")

    def check_user_passwd(self, username, password):
        password = base64.b64encode(bytes(password, encoding='utf-8'))
        all_users = self.get_login_data()
        for user in all_users:
            if username == user[0] and password.decode('utf-8') == user[1]:
                return True, user[2]
        return False, None

    def delete_worker(self, name):

        """
        Admin only. Deletes worker from users.
        :param name:
        :return:
        """

        self.db.use_query(f"DELETE FROM users WHERE login = '{name}';")

    def change_worker_permissions(self, name, permissions):

        """
        Admin only. Changes workers permissions.
        :param name:
        :param permissions:
        :return:
        """

        self.db.use_query(f"UPDATE users SET permissions = '{permissions}' WHERE login = '{name}';")

    def get_login_data(self):

        """
        Get all data from table users.
        :return all data:
        """

        self.db.use_get_query("SELECT login,password,permissions FROM users;")
        return self.db.return_result()

    def get_description(self):

        """
        Returns products description.
        :return:
        """

        self.db.use_get_query("SELECT * FROM product_description;")
        return self.db.return_result()

    def add_to_trash(self, id_prod, name, prod_type, come_date):

        """
        Adds to the trash product and deletes it from tables products, date.
        :param id_prod:
        :param name:
        :param prod_type:
        :param come_date:
        :return:
        """

        self.db.use_query(
            f"INSERT INTO trash(name,product_type,come_date) VALUES('{name}', '{prod_type}', '{come_date}');")
        self.delete_product('', id_prod)

    def get_names(self, table_name: str):

        """
        Returns all names from table_name.
        Table_name is in self.tables.
        :param table_name:
        :return all_names:
        """

        if table_name == 'users':
            self.db.use_get_query(f"SELECT login FROM users;")
        else:
            self.db.use_get_query(f"SELECT name FROM {table_name};")
        all_names = list()
        for row in self.db.return_result():
            for name in row:
                all_names.append(name)
        return all_names

    def get_id(self, table_name: str):

        """
        Returns all ids from table_name.
        Table_name is in self.tables.
        :param table_name:
        :return all_ids:
        """

        self.db.use_get_query(f"SELECT id FROM {table_name};")
        all_ids = list()
        for row in self.db.return_result():
            for idd in row:
                all_ids.append(idd)
        return all_ids

    def get_trash_info(self):
        self.db.use_get_query("SELECT * FROM trash;")
        return self.db.return_result()

    def get_tables(self):

        """
        Returns tables.
        :return self.tables:
        """

        return self.tables

    def get_count(self, table_name: str):

        """
        Returns number of rows in table.
        Table_name is in self.tables.
        :param table_name:
        :return self.db.return_result():
        """

        self.db.use_get_query(f'SELECT COUNT(*) FROM {table_name};')
        return self.db.return_result()

    def end_process(self):

        """
        End of process.
        :return:
        """

        self.db.end_proc()


def registration(db):
    log = input('Enter username: ')
    all_used_names = db.get_names('users')
    while log in all_used_names or len(log) > 30:
        if len(log) > 30:
            print('Too many chars. Login should be < 30.')
        elif log in all_used_names:
            print('This login is used. Please choose another one.')
        log = input('Enter username: ')
    passwd = input('Enter password: ')
    while len(passwd) < 4 or len(passwd) > 30:
        if len(passwd) > 30:
            print('Too many chars. Password should be < 30.')
        elif len(passwd) < 4:
            print('Too short password. 4 chars minimal.')
        passwd = input('Enter password: ')
    db.create_user(log, passwd, 'worker')
    print('Success.')
    return Worker(log, passwd, 'worker')


def login(db):
    print()
    log = input('Enter username: ')
    passwd = input('Enter password: ')
    print()
    while True:
        conn = db.check_user_passwd(log, passwd)
        if conn[0]:
            account = Worker(log, passwd, conn[1])
            print('Success.')
            break
        print('Invalid login or password.')
        print()
        log = input('Enter username: ')
        passwd = input('Enter password: ')
        print()
    return account


class Worker:

    def __init__(self, user_login, password, permissions):
        self.user_login = user_login
        self.password = password
        self.permissions = permissions

    def log_out(self):
        self.user_login, self.password, self.permissions = None, None, None
        print('Log out.')


def check_valid_id(idd):
    """
    Returns id, True when id is valid.
    Returns id, False when id is invalid.
    :param idd:
    :return (id, flag):
    """

    try:
        idd = int(idd)
        assert idd > 0
    except ValueError:
        print('Invalid id value.')
        return idd, False
    except AssertionError:
        print('Invalid id value, id of product should be > 0')
        return idd, False
    else:
        return idd, True


def start(db):

    """ Login menu """

    while True:
        inp = input(
            '1) login\n2) register\n-> ').split()
        if inp[0] == 'login' or inp[0] == '1':
            user = login(db)
            return user
        elif inp[0] == 'register' or inp[0] == '2':
            user = registration(db)
            return user
        else:
            print('Invalid command.')


def setup():
    """
    Returns class instance of SQLHandler.
    :return db:
    """

    try:
        db = SQLHandler()
    except psycopg2.OperationalError:
        print("Database ERROR.")
        exit(1)
    else:
        print("Database opened successfully.")
        return db


def select_reformat_print(data, edition):
    """
    Printing table with columns (edition) and rows (data).
    :param data:
    :param edition:
    :return:
    """

    new_td = list()
    for row in data:
        for elem in row:
            new_td.append(elem)

    columns = len(edition)

    table = PrettyTable(edition)
    td_data = new_td[:]

    while td_data:
        table.add_row(td_data[:columns])
        td_data = td_data[columns:]
    print(table)


def main():
    """Main function."""

    newdb = setup()
    worker = start(newdb)
    if worker.permissions == 'admin':
        color = 'green'
    else:
        color = 'red'
    c = colored('admin', color)
    information = '''
    + -----------------------------------------------------+
    | There is following commands:                         |
    |    0)  help            shows base commands           |
    |    1)  show            products list                 |
    |    2)  add             product to products list      |
    |    3)  delete          product from products list    |
    |    4)  change          price of product              |
    |    5)  item            info from storage             |
    |    6)  tables          list                          |
    |    7)  count           table                         |
    |    8)  clear           tables(products, date) %s  |
    |    9)  exit            end process                   |
    |                                                      |
    |    10) description                                   |
    |          1) add      ➘                               |
    |          2) change   ➙ description                   |
    |          3) delete   ➚                               |
    |                                                      |
    |    11) desc            shows products description    |
    |    12) update          database dates process        |
    |    13) trash           out of date products          |
    |    14) clear_trash     clear trash            %s  |
    |    15) logout                                        |
    |                                                      |
    |    users                                      %s  |
    |    adduser/deleteuser                         %s  |
    |    change_user_permissions                    %s  |
    +------------------------------------------------------+'''
    denied = colored('Access denied.', 'red')
    print(information % (c, c, c, c, c))
    command = input('\tWrite command -> ').split()
    while command[0] != 'exit' and command[0] != '9':

        if command[0] == 'show' or command[0] == '1':
            select_reformat_print(newdb.get_all(), ['ID', 'NAME', 'COST', 'TYPE', 'COME DATE', 'EXPIR_DAYS'])

        elif command[0] == 'help' or command[0] == '0':
            print(information)

        elif command[0] == 'clear_trash' or command[0] == '14':
            if worker.permissions == 'admin':
                newdb.clear_table('trash')
                print('Successfully cleared.')
            else:
                print(denied)

        elif command[0] == 'trash' or command[0] == '13':
            select_reformat_print(newdb.get_trash_info(), ['ID', 'NAME', 'PRODUCT_TYPE', 'COME_DATE'])

        elif command[0] == 'users':
            if worker.permissions == 'admin':
                select_reformat_print(newdb.get_login_data(), ['LOGIN', 'PASSWORD', 'PERMISSIONS'])
            else:
                print(denied)

        elif command[0] == 'add' or command[0] == '2':
            inp = input('Give name and cost like: bread 29.99\n-> ').split()
            if len(inp) == 2 and 0 < len(inp[0]) <= 50 and inp[0] not in newdb.get_names('products'):
                name, cost = inp[0], inp[1]
                try:
                    cost = float(cost)
                except ValueError:
                    print('Invalid cost value.')
                else:
                    if 0 < cost < 1000000:
                        p_type = input('Write product type 1) food, 2) notfood. example: food/notfood/1/2\n-> ')
                        if p_type == 'food' or p_type == '1':
                            newdb.add_product(name, cost, 'food', 30)
                            print('New product is added.')

                        elif p_type == 'notfood' or p_type == '2':
                            newdb.add_product(name, cost, 'notfood', -1)
                            print('New product is added.')
                        else:
                            print('Invalid input. Type of product can be food or notfood.')
                    else:
                        print('Invalid input. Cost should be -> (0 < cost < 1000000)')
            else:
                print('Invalid input. Name should be unique. Give name and cost like: bread 29.99')

        elif command[0] == 'delete' or command[0] == '3':
            ch = input('Do you want delete product(s) by name or id? 1) name 2) id  | example: name/id/1/2\n-> ')
            if ch == 'name' or ch == '1':
                name_of_product = input('Please write name of product(s).\n-> ')
                if 0 < len(name_of_product) <= 50 and name_of_product in newdb.get_names('products'):
                    newdb.delete_product(name_of_product)
                    print('Successfully deleted.')
                else:
                    print('Name is not found.')
            elif ch == 'id' or ch == '2':
                id_of_product = input('Please write id of product. (id > 0)\n-> ')
                id_of_product, flag = check_valid_id(id_of_product)
                if flag and id_of_product in newdb.get_id('products'):
                    newdb.delete_product('', id_of_product)
                    print('Successfully deleted.')
                else:
                    print('Invalid id.')
            else:
                print('Invalid input.')

        elif command[0] == 'change' or command[0] == '4':
            inp = input('Give name and a NEW cost like: bread 29.99\n-> ').split()
            if len(inp) == 2 and 0 < len(inp[0]) <= 50:
                name, new_cost = inp[0], inp[1]
                if name in newdb.get_names('products'):
                    try:
                        new_cost = float(new_cost)
                    except ValueError:
                        print('Invalid new cost value.')
                    else:
                        if 0 < new_cost < 1000000:
                            newdb.change_cost_of_product(name, new_cost)
                            print('Successfully changed.')
                        else:
                            print('Invalid input. Cost should be -> (0 < cost < 1000000)')
                else:
                    print('Name is not found.')
            else:
                print('Invalid input. Too many values.')

        elif command[0] == 'item' or command[0] == '5':
            name = input('Write name of item\n-> ')
            if name in newdb.get_names('products'):
                select_reformat_print(newdb.get_item(name), ['ID', 'NAME', 'COST', 'TYPE', 'COME DATE', 'EXPIR_DAYS'])
            else:
                print('Name is not found.')

        elif command[0] == 'tables' or command[0] == '6':
            select_reformat_print([newdb.tables], ['tables'])

        elif command[0] == 'count' or command[0] == '7':
            table = input('Write name of table please.\n-> ')
            if table in newdb.tables:
                print(newdb.get_count(table)[0][0])
            else:
                print(f'Invalid input. There is no table like {table}.')
        elif command[0] == 'clear' or command[0] == '8':
            if worker.permissions == 'admin':
                newdb.clear_table('products')
                newdb.clear_table('date')
                print('Successfully cleared.')
            else:
                print(denied)
        elif command[0] == 'description' or command[0] == '10':

            ch = input('Write command: add/change/delete/1/2/3\n-> ').split()

            if ch[0] == 'add' or ch[0] == '1':
                product_name = input('Write name of product\n-> ')
                if product_name in newdb.get_names('products') and product_name in newdb.get_names(
                        'product_description'):

                    description = input(f'Write short description for the product {product_name}\n-> ')
                    if len(description) < 250:
                        newdb.add_description(product_name, description)
                        print('Success.')
                    else:
                        print('Invalid input. Maximal length of description should be < 250.')
                else:
                    print('Name is not found or name has description.')

            elif ch[0] == 'change' or ch[0] == '2':
                product_name = input('Write name of product\n-> ')
                if product_name in newdb.get_names('products') and product_name in newdb.get_names(
                        'product_description'):
                    description = input(f'Write short description for the product {product_name}\n-> ')
                    if len(description) < 250:
                        newdb.change_description(product_name, description)
                        print('Success.')
                    else:
                        print('Invalid input. Maximal length of description should be < 250.')
                else:
                    print('Name is not found or name has description.')

            elif ch[0] == 'delete' or ch[0] == '3':
                product_name = input('Write name of product\n-> ')
                if product_name in newdb.get_names('products') and product_name in newdb.get_names(
                        'product_description'):
                    newdb.delete_description(product_name)
                    print('Success.')
                else:
                    print('Name is not found or name has description.')

            else:
                print(f'Invalid input. There is no command like {ch[0]}.')

        elif command[0] == 'update' or command[0] == '12':
            newdb.update_date()
            print('Updated.')
        elif command[0] == 'logout' or command[0] == '15':
            worker.log_out()
            worker = start(newdb)
            if worker.permissions != 'admin':
                c = colored('admin', 'red')
            print(information % (c, c, c, c, c))
        elif command[0] == 'desc' or command[0] == '11':
            select_reformat_print(newdb.get_description(), ['ID', 'NAME', 'DESCRIPTION'])
        elif command[0] == 'adduser':
            if worker.permissions == 'admin':
                flag = True
                name = input('Enter name: ')
                if len(name) >= 50:
                    flag = False
                    print('Invalid input. Too many chars. Name should be < 50.')
                password = input('Enter password: ')
                if len(password) < 4:
                    flag = False
                    print(print('Invalid input. Too short password. Password should be > 4.'))
                permissions = input('Enter permissions: ')
                if len(permissions) > 20:
                    flag = False
                    print('Invalid input. Too many chars. Max chars = 20.')
                if flag:
                    newdb.create_user(name, password, permissions)
            else:
                print(denied)
        elif command[0] == 'deleteuser':
            if worker.permissions == 'admin':
                flag = True
                name = input('Enter name: ')
                if name == worker.user_login:
                    flag = False
                    print('You cant delete yourself.')
                elif len(name) >= 50:
                    flag = False
                    print('Invalid input. Too many chars. Name should be < 50.')
                if flag:
                    newdb.delete_worker(name)
                    print('Successfully deleted.')
            else:
                print(denied)
        elif command[0] == 'change_user_permissions':
            if worker.permissions == 'admin':
                flag = True
                name = input('Enter name: ')
                if len(name) >= 50:
                    flag = False
                    print('Invalid input. Too many chars. Name should be < 50.')
                permissions = input('Enter permissions: ')
                if len(permissions) > 20:
                    flag = False
                    print('Invalid input. Too many chars. Max chars = 20.')
                if flag:
                    newdb.change_worker_permissions(name, permissions)
                    print('Changed.')
            else:
                print(denied)
        else:
            print('Invalid command.')

        command = input('\tWrite command -> ').split()

    else:
        worker.log_out()
        print('Process ending', end="")
        for i in range(3):
            time.sleep(0.4)
            print('.', end="")
        print()
        newdb.end_process()


if __name__ == '__main__':
    main()
