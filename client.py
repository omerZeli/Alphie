import socket
import tkinter as tk


class client:

    def __init__(self, ip):
        self.ip = ip    # the ip of the server
        self.my_socket = socket.socket()    # build the socket of the client
        self.user_name = ""
        self.password = ""
        self.root = tk.Tk()     # create the graphic
        self.root.title("Alphie")   # the title of the window
        self.root.configure(background="firebrick1")    # change the window color
        self.text_box = tk.Text(self.root, height=10, width=150)    # create text box
        self.text_box.configure(state='disabled')
        self.entry = tk.Entry(self.root)    # create entry
        self.enter_button = tk.Button(self.root, text="enter")      # create enter button
        self.menu_bar = tk.Menu(self.root)      # the main menu
        self.back_menu = tk.Menu(self.menu_bar, tearoff=0)      # back menu, added to menu_nar
        self.history_menu = tk.Menu(self.menu_bar, tearoff=0)      # history menu, added to menu_nar

    # input details in sign up/in
    def input_sign(self, sign):
        self.user_name = self.input("Enter user name")
        self.password = self.input("Enter password")
        msg = "{}; {}, {}".format(sign, self.user_name, self.password)
        return msg

    # send a message and get a receive an answer
    def send_and_rec(self, msg):
        msg = msg.encode()
        self.my_socket.send(msg)
        ans = self.my_socket.recv(1024)
        ans = ans.decode()
        return ans

    # print message to text box
    def print_message(self, text):
        self.text_box.configure(state='normal')
        self.text_box.insert(tk.END, text + "\n")
        self.text_box.configure(state='disabled')

    # input message
    def input(self, text):
        self.print_message(text)
        var = tk.IntVar()
        self.enter_button.pack()
        self.enter_button.configure(command=lambda: var.set(1))
        self.enter_button.wait_variable(var)
        output = self.entry.get()
        self.print_message(output)
        self.enter_button.pack_forget()
        self.entry.delete(0, 'end')
        return output

    # delete all the items in thw window
    def delete_items(self):
        lst = self.root.winfo_children()
        for item in lst:
            item.pack_forget()

    # delete all the text in the text box
    def delete_text_box(self):
        self.text_box.configure(state='normal')
        self.text_box.delete('1.0', tk.END)
        self.text_box.configure(state='disabled')

    # send quit to the server to stop the connection with the server
    def close_button(self):
        self.my_socket.send("close_window".encode())
        self.my_socket.close()
        self.root.destroy()

    # add back_menu to menu_bar, add it to window
    def create_menu(self):
        self.menu_bar.add_cascade(label="back", menu=self.back_menu)
        self.menu_bar.add_cascade(label="history", menu=self.history_menu)
        self.root.config(menu=self.menu_bar)

    # graphic - the start of the app, choose sign up/in
    def show_start(self):
        self.delete_items()
        self.delete_text_box()
        self.back_menu.delete(0)
        self.history_menu.delete(0)
        self.text_box.pack()
        self.print_message("Hello, my name is Alphie")
        self.print_message("If you have an user click sign in, else click sign up")
        # create sign up/in buttons
        su_button = tk.Button(self.root, text="sign up", command=lambda: self.show_sign("sign_up"))
        su_button.pack()
        si_button = tk.Button(self.root, text="sign in", command=lambda: self.show_sign("sign_in"))
        si_button.pack()

    # graphic - sign up/in
    def show_sign(self, sign):
        self.delete_items()
        self.delete_text_box()
        # back goes to show start
        self.back_menu.delete(0)
        self.history_menu.delete(0)
        self.back_menu.add_command(label="start", command=lambda: self.show_start())
        self.text_box.pack()
        self.entry.pack()
        ser_ans = ""
        if sign == "sign_up":
            while ser_ans != "You signed up":
                msg = self.input_sign("sign_up")
                ser_ans = self.send_and_rec(msg)
                self.print_message(ser_ans)
        else:
            while ser_ans != "You signed in":
                msg = self.input_sign("sign_in")
                ser_ans = self.send_and_rec(msg)
                self.print_message(ser_ans)
        self.show_search()

    # graphic - the searching
    def show_search(self):
        self.delete_items()
        self.delete_text_box()
        self.back_menu.delete(0)
        self.history_menu.delete(0)
        self.back_menu.add_command(label="start", command=lambda: self.show_start())
        self.history_menu.add_command(label="show history", command=lambda: self.show_history())
        self.text_box.pack()
        self.entry.pack()
        self.print_message("Now enter the word you want to search")
        self.print_message("And I'll show you all the results")
        # input the word
        word = self.input("")
        self.do_search(word)

    # do the search
    def do_search(self, word):
        methods = self.send_and_rec(word)
        self.show_methods(methods)

    # graphic - the methods from the searching
    def show_methods(self, methods):
        self.delete_items()
        self.delete_text_box()
        self.back_menu.delete(0)
        self.back_menu.add_command(label="search", command=lambda: self.show_search())
        self.text_box.pack()
        self.text_box.configure(height=10)
        self.print_message("Click the method that you want to read about")
        # create button for every file result
        results_list = methods.split(', ')
        for button_text in results_list:
            button = tk.Button(self.root, text=button_text,
                               command=lambda name=button_text: self.show_files_results(methods, name))
            button.pack()
            if button_text == "no results":
                button.configure(command=lambda: 0)

    # graphic - the file of the method
    def show_files_results(self, methods, method):
        self.delete_items()
        self.delete_text_box()
        self.back_menu.delete(0)
        self.back_menu.add_command(label="methods", command=lambda: self.show_methods(methods))
        self.text_box.pack()
        self.text_box.configure(height=10)
        self.print_message("Click the file you want to open")
        # create button for every file result
        results = self.send_and_rec("get_files; {}".format(method))
        files = results.split(", ")
        for button_text in files:
            button = tk.Button(self.root, text=button_text,
                               command=lambda name=button_text: self.show_file(methods, method, name))
            button.pack()

    # graphic - the file
    def show_file(self, methods, method, file_name):
        self.delete_items()
        self.delete_text_box()
        self.back_menu.delete(0)
        self.back_menu.add_command(label="files", command=lambda: self.show_files_results(methods, method))
        self.text_box.pack()
        self.text_box.configure(height=30)
        # get the file from server
        text = self.rec_file(file_name)
        self.print_message(text)

    # get the file from server
    def rec_file(self, file_name):
        # ask the server for the file length
        msg = "file_len; {}".format(file_name)
        length = self.send_and_rec(msg)
        length = int(length)
        # ask the server for the file
        msg = "send_file; {}".format(file_name)
        self.my_socket.send(msg.encode())
        text = ""
        for i in range(length):
            data = self.my_socket.recv(1024)
            data = data.decode()
            text += data
        return text

    # graphic - the history
    def show_history(self):
        self.delete_items()
        self.delete_text_box()
        self.back_menu.delete(0)
        self.back_menu.add_command(label="search", command=lambda: self.show_search())
        self.text_box.pack()
        self.text_box.configure(height=10)
        self.print_message("This is your last history")
        msg = "get_history; {}".format(self.user_name)
        results = self.send_and_rec(msg)
        results_list = results.split(', ')
        for button_text in results_list:
            button = tk.Button(self.root, text=button_text,
                               command=lambda name=button_text: self.do_search(name))
            button.pack()
            if button_text == "no results":
                button.configure(command=lambda: 0)

    def main(self):
        # connect the client to the server
        self.my_socket.connect((self.ip, 8820))
        # x button
        self.root.protocol('WM_DELETE_WINDOW', self.close_button)
        # the size of the window
        self.root.geometry("1500x1500")
        self.create_menu()
        # start the app
        self.show_start()
        self.root.mainloop()


server_ip = '127.0.0.1'
client(server_ip).main()
