import socket
import sqlite3
import select
import create_db
import threading


class server:

    def __init__(self, data_base_path, files_path):
        self.data_base_path = data_base_path    # db file path
        self.keys_table_name = "KEYS"
        self.users_table_name = "USERS"
        self.history_table_name = "HIST"
        self.open_client_sockets = []
        self.messages_to_send = []
        self.create = create_db.create(data_base_path, files_path)
        self.words_to_add = []    # words to add after client close
        self.socket_names = []    # the user name of every socket

    # send messages
    def send_waiting_messages(self, wlist, messages_to_send):
        for message in messages_to_send:
            (client_socket, data) = message
            # if the client can get the massage
            if client_socket in wlist:
                data = data.encode()
                client_socket.send(data)
                messages_to_send.remove(message)

    # find the word in the data base
    def find_word(self, the_word):
        # open the data base
        conn = sqlite3.connect(self.data_base_path)
        cursor = conn.execute("SELECT * from {}".format(self.keys_table_name))
        names_lst = []
        cut_word = the_word.split(' ')
        # delete connectors
        delete_words = ["i", "a", "to", "the", "do", "can", "how", "what", "of", "for", "from", "on", "in"]
        for i in delete_words:
            if i in cut_word:
                cut_word.remove(i)
        # go over the data base table
        for row in cursor:
            # go over the word
            for word in cut_word:
                # row[0] = key, word[1] = file name
                if word.lower() in row[0].lower():
                    names_lst.append(row[0])
        # get list with grades
        file_lst = self.get_grade(names_lst)
        results = self.return_results(file_lst)
        return results

    # find the grade of every file
    def get_grade(self, names_lst):
        file_lst = []
        for name in names_lst:
            # how much matches in the file
            grade = 0
            for another_name in names_lst:
                if another_name == name:
                    grade += 1
            # add the file name with its grade to list
            current_file = (name, grade)
            if current_file not in file_lst:
                file_lst.append(current_file)
        return file_lst

    # return the list as ordered string
    def return_results(self, file_lst):
        if len(file_lst) == 0:
            return "no results"
        else:
            # order the list from the biggest grade
            order_file_lst = self.order_lst(file_lst)
            # send only 20 results
            if len(order_file_lst) > 20:
                mini_list = []
                for i in range(20):
                    mini_list.append(order_file_lst[i])
                order_file_lst = mini_list
            # change the list to string for sending
            str_names_lst = ""
            for file in order_file_lst:
                str_names_lst = str_names_lst + file[0] + ", "
            str_names_lst = str_names_lst[:-2]
            return str_names_lst

    # order the list from the biggest grade
    def order_lst(self, lst):
        order_lst = []
        for j in range(len(lst)):
            max_num = 0
            max_file = 0
            for i in lst:
                if i[1] >= max_num:
                    max_num = i[1]
                    max_file = i
            order_lst.append(max_file)
            lst.remove(max_file)
        return order_lst

    # find the files withe the method
    def find_file(self, method):
        conn = sqlite3.connect(self.data_base_path)
        cursor = conn.execute("SELECT * from {}".format(self.keys_table_name))
        files_lst = ""
        for row in cursor:
            if row[0] == method:
                files_lst += row[1] + ", "
        files_lst = files_lst[:-2]
        return files_lst

    # find the user name and the password from the message
    def cut_sign_msg(self, msg):
        data = msg.split("; ")
        profile = data[1]
        profile = profile.split(", ")
        profile = tuple(profile)
        return profile

    # if the user is in the table
    def sign_in_table(self, profile, sign):
        conn = sqlite3.connect(self.data_base_path)
        cursor = conn.execute("SELECT * from {}".format(self.users_table_name))
        exist = False
        if sign == "sign_in":
            for row in cursor:
                if row == profile:
                    exist = True
        else:
            for row in cursor:
                if row[0] == profile[0]:
                    exist = True
        return exist

    # sign up an user
    def sing_up(self, column1, column2, the_word, current_socket):
        profile = self.cut_sign_msg(the_word)
        exist = self.sign_in_table(profile, "sign_up")
        if exist:
            self.messages_to_send.append((current_socket, "This user is already exists"))
        else:
            self.create.insert(self.users_table_name, column1, column2, profile)
            self.messages_to_send.append((current_socket, "You signed up"))
            self.add_name(current_socket, profile[0])

    # sign in an user
    def sign_in(self, the_word, current_socket):
        profile = self.cut_sign_msg(the_word)
        exist = self.sign_in_table(profile, "sign_in")
        if exist:
            self.messages_to_send.append((current_socket, "You signed in"))
            self.add_name(current_socket, profile[0])
        else:
            self.messages_to_send.append((current_socket, "You have a mistake in your user name or your password"))

    # add name of socket to the list
    def add_name(self, socket, name):
        for user in self.socket_names:
            if user[0] == socket:
                self.socket_names.remove(user)
        self.socket_names.append((socket, name))

    # find the name of the socket
    def find_name(self, current_socket):
        for socket in self.socket_names:
            if socket[0] == current_socket:
                return socket[1]

    # find the history of the user
    def find_history(self, name):
        conn = sqlite3.connect(self.data_base_path)
        cursor = conn.execute("SELECT * from {}".format(self.history_table_name))
        result_list = []
        results = ""
        for row in cursor:
            if row[0] == name:
                if row[1] not in result_list:
                    result_list.append(row[1])
        # only last 20 results
        if len(result_list) > 20:
            start = len(result_list) - 20
            result_list = result_list[start:]
        # make the list to a string
        for word in result_list:
            results += word + ", "
        if results == "":
            results = "no results"
        else:
            results = results[:-2]
        return results

    # get message from the client and handle it
    def handle_word(self, server_socket,
                    users_column1, users_column2, keys_column1, keys_column2, history_column1, history_column2):
        while True:
            # select
            rlist, wlist, xlist = \
                select.select([server_socket] + self.open_client_sockets, self.open_client_sockets, [])
            for current_socket in rlist:
                # if a new socket is connected
                if current_socket is server_socket:
                    (new_socket, address) = server_socket.accept()
                    self.open_client_sockets.append(new_socket)
                # if the server got a message
                else:
                    # get the word
                    the_word = current_socket.recv(1024)
                    the_word = the_word.decode()
                    # if the client want to quit the app
                    if the_word == "close_window":
                        # remove socket from lists
                        self.open_client_sockets.remove(current_socket)
                        for socket in self.socket_names:
                            if socket[0] == current_socket:
                                self.socket_names.remove(socket)
                        # add word to data base
                        for to_add in self.words_to_add:
                            if to_add[0] == current_socket:
                                try:
                                    thread = threading.Thread(target=lambda: self.create.insert_keys(
                                        keys_column1, keys_column2, to_add[1]))
                                    thread.start()
                                except:
                                    pass
                                self.words_to_add.remove(to_add)
                    # sign up message
                    elif "sign_up" in the_word:
                        try:
                            self.sing_up(users_column1, users_column2, the_word, current_socket)
                        except:
                            self.messages_to_send.append((current_socket, "There is a mistake in the server, sorry"))
                    # sign in message
                    elif "sign_in" in the_word:
                        try:
                            self.sign_in(the_word, current_socket)
                        except:
                            self.messages_to_send.append((current_socket, "There is a mistake in the server, sorry"))
                    # find the length of the file, to know how much times send it
                    elif "file_len" in the_word:
                        (command, file_name) = the_word.split("; ")
                        try:
                            file = open(file_name)
                            text = file.read()
                        except:
                            text = ""
                        length = len(text)
                        times = (length//1024)+1
                        times = str(times)
                        self.messages_to_send.append((current_socket, times))
                    # send the file to the client
                    elif "send_file" in the_word:
                        (command, file_name) = the_word.split("; ")
                        try:
                            file = open(file_name)
                            text = file.read()
                        except:
                            text = "Can't show the file"
                        self.messages_to_send.append((current_socket, text))
                    # find the user history on data base
                    elif "get_history" in the_word:
                        (command, name) = the_word.split("; ")
                        results = self.find_history(name)
                        self.messages_to_send.append((current_socket, results))
                    # find the files form the method
                    elif "get_files" in the_word:
                        (command, method) = the_word.split("; ")
                        files = self.find_file(method)
                        self.messages_to_send.append((current_socket, files))
                    # if the server got a word to search
                    else:
                        try:
                            name = self.find_name(current_socket)
                            history = (name, the_word)
                            self.create.insert(self.history_table_name, history_column1, history_column2, history)
                            results = self.find_word(the_word)
                            # there is no results to the word
                            if results == "no results":
                                # add the word to words_to_add
                                if the_word not in self.words_to_add:
                                    self.words_to_add.append((current_socket, the_word))
                                self.messages_to_send.append((current_socket, results))
                            # if there are results
                            else:
                                self.messages_to_send.append((current_socket, results))
                        except:
                            self.messages_to_send.append((current_socket, "no results"))
            self.send_waiting_messages(wlist, self.messages_to_send)

    def main(self):
        print("server begin")
        server_socket = socket.socket()
        server_socket.bind(("0.0.0.0", 8820))
        server_socket.listen(1)
        users_column1 = 'user_name'
        users_column2 = 'password'
        keys_column1 = 'the_key'
        keys_column2 = 'the_file'
        history_column1 = 'user_name'
        history_column2 = 'search'

        self.handle_word(
            server_socket, users_column1, users_column2, keys_column1, keys_column2, history_column1, history_column2)


data_base_path = 'data_base.db'
files_path = 'files_data'
server(data_base_path, files_path).main()
