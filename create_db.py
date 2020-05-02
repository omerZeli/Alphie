import sqlite3
import os


class create:

    def __init__(self, data_base_path, files_path):
        self.data_base_path = data_base_path
        self.keys_table_name = "KEYS"
        self.users_table_name = "USERS"
        self.history_table_name = "HIST"
        self.files_path = files_path

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
                # the keys
                general_keys = ["import"]
                python_keys = ["import", "def"]
                java_keys = ["import", "public"]
                # add word that client searched
                if special != "":
                    keys = [special]
                # add keys that known to me
                elif ".py" in path:
                    keys = python_keys
                elif ".java" in path:
                    keys = java_keys
                else:
                    keys = general_keys
                # find the keys in the current file
                for line in lines:
                    for key in keys:
                        if key in line:
                            tup = (line, path)
                            lines_list.append(tup)
                # add the last name of the file
                last_path = path.split("\\")[-1]
                lines_list.append((last_path, path))
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
            print("the line " + st + " can't be in the db")
        conn.commit()
        conn.close()

    # insert the keys to the data base after they were found
    def insert_keys(self, column1, column2, special=""):
        lines_list = self.find_keys(special)
        for data in lines_list:
            self.insert(self.keys_table_name, column1, column2, data)

    def main(self):
        try:
            keys_column1 = 'the_key'
            keys_column2 = 'the_file'
            users_column1 = 'user_name'
            users_column2 = 'password'
            history_column1 = 'user_name'
            history_column2 = 'search'
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
