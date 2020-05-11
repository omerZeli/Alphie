import sqlite3
import os


class create:

    def __init__(self, data_base_path, files_path, add=""):
        self.data_base_path = data_base_path
        self.keys_table_name = "KEYS"
        self.users_table_name = "USERS"
        self.history_table_name = "HIST"
        self.files_path = files_path
        self.add = add

    # create data base table
    def create_table(self, table_path, table_name, column1, column2):
        conn = sqlite3.connect(table_path)
        st = '''CREATE TABLE {}
                        (
                        {}  TEXT    NOT NULL,
                        {}   TEXT    NOT NULL
                        );'''.format(table_name, column1, column2)
        conn.execute(st)
        conn.close()

    # find all the file in the data base
    def find_files(self, path):
        files_list = []
        self.open(path, files_list)
        return files_list

    # recursion
    def open(self, path, files_list):
        if self.empty(path):
            files_list.append(path)
        else:
            for i in os.listdir(path):
                self.open(path + "\\" + i, files_list)

    def empty(self, path):
        try:
            os.listdir(path)
            return False
        except:
            return True

    # find the lines keys in the files
    def find_keys(self, special):
        files_list = self.find_files(self.files_path)
        lines_list = []
        for path in files_list:
            try:
                # read the current file
                file = open(path, "r")
                contents = file.read()
                lines = contents.split("\n")
                # find the imports from file
                imports = []
                for line in lines:
                    spl_line = line.split(" ")
                    if "import" in line:
                        for word in spl_line:
                            try:
                                dir(__import__(word))
                                if word not in imports:
                                    imports.append(word)
                            except:
                                pass
                for imp in imports:
                    methods = dir(__import__(imp))
                    for method in methods:
                        the_method = "{}.".format(method)
                        if the_method in contents:
                            method_name = "{}.{}()".format(imp, method)
                            lines_list.append((method_name, path))
                file.close()
            except:
                pass
        return lines_list

    # insert data to data base table
    def insert(self, table_name, column1, column2, data):
        conn = sqlite3.connect(self.data_base_path)
        st = "INSERT INTO {} ({},{}) VALUES ('{}', '{}')".format(table_name, column1, column2, data[0], data[1])
        try:
            conn.execute(st)
        except:
            pass
        conn.commit()
        conn.close()

    # insert the keys to the data base after they were found
    def insert_keys(self, column1, column2, special=""):
        lines_list = self.find_keys(special)
        for data in lines_list:
            self.insert(self.keys_table_name, column1, column2, data)

    def main(self):
        keys_column1 = 'the_key'
        keys_column2 = 'the_file'
        users_column1 = 'user_name'
        users_column2 = 'password'
        history_column1 = 'user_name'
        history_column2 = 'search'
        if self.add != "":
            try:
                save_path = self.files_path
                self.files_path = self.add
                self.insert_keys(keys_column1, keys_column2)
                print(self.files_path + " added")
                self.files_path = save_path
            except:
                pass
        else:
            try:
                self.create_table(self.data_base_path, self.users_table_name, users_column1, users_column2)
                print("Users data base created")
                self.create_table(self.data_base_path, self.keys_table_name, keys_column1, keys_column2)
                self.insert_keys(keys_column1, keys_column2)
                print("Keys data base created")
                self.create_table(self.data_base_path, self.history_table_name, history_column1, history_column2)
                print("History data base created")
            except:
                pass


data_base_path = 'data_base.db'
files_path = 'files_data'
create(data_base_path, files_path).main()
