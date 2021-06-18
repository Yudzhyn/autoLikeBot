import tkinter as tk
import tkinter.ttk as ttk
import json
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import time
import random
from threading import Thread
import logging

# ===========================================================================================
# -----------------------------------------CONSTANTS-----------------------------------------
# ===========================================================================================

# ------------------------------------------JSON---------------------------------------------

PATH_JSON_FILE = r"accounts\accounts.json"
PATH_JSON_CONFIGS = "config.json"

# ------------------------------------------GUI----------------------------------------------

NAME_TITLE_WINDOW = "AutoLike"
SIZE_WINDOW = "450x420"

# ------------------------------------------TIME----------------------------------------------

DEFAULT_TIME_FROM = 1
DEFAULT_TIME_TO = 3
DEFAULT_UNIT_TIME = "min"

# ------------------------------------------LOGGING----------------------------------------------

DIRECTORY_LOG = ".\LOGS.txt"

logging.basicConfig(filename=DIRECTORY_LOG, level=logging.INFO, format='%(asctime)s %(levelname)s %(module)s - %(funcName)s: %(message)s',
    datefmt='%d-%m-%Y %H:%M:%S')


# ===========================================================================================
# ####################################JSON DATABASE##########################################
# ===========================================================================================

# ===========================================================================================
# -------------------------------------------CLASSES-----------------------------------------
# ===========================================================================================

class Account:

    def __init__(self, email, password):
        self.email = email
        self.password = password
        self.status = '-'

    def pack_to_dict(self):
        return {"email":self.email, "password":self.password, "status": self.status}

class JSON_DB:

    def __init__(self, path):
        self.path = path
        self.data = self.get_all_data()

    def get_all_data(self):
        with open(self.path, 'r') as json_file:
            data_tmp = json.load(json_file)["accounts"]
        return data_tmp

    def print_data(self):
        print(self.data)

    def get_data(self):
        with open(self.path, 'r') as json_file:
            data_tmp = json.load(json_file)
        return data_tmp

    def write_data(self, data_to_write):
        with open(self.path, 'w') as json_file:
            json.dump(data_to_write, json_file)

    def add_account_to_json(self, new_account_dict):

        data_tmp = self.get_data()

        self.data.append(new_account_dict)

        data_tmp["accounts"] = self.data

        self.write_data(data_tmp)


    def delete_account_from_json(self, email):

        data_tmp = self.get_data()

        for account in data_tmp["accounts"]:
            if account["email"] == email:
                data_tmp["accounts"].remove(account)
                break

        self.write_data(data_tmp)

    def get_accounts_with_minus(self, only_count=False):
        data_tmp = self.get_all_data()
        data = [account for account in data_tmp if account["status"] == '-']
        return len(data) if only_count else data

    def get_password_by_email(self, need_email):
        data_tmp = self.get_all_data()
        for account in data_tmp:
            if account["email"] == need_email:
                return_password = account["password"]
                break
        return return_password

    def change_status_account(self, email, flag):
        data_tmp = self.get_data()
        for account in data_tmp["accounts"]:
            if account["email"] == email:
                account["status"] = flag
                break
        self.data = data_tmp["accounts"]
        self.write_data(data_tmp)

    def change_values_account(self, old_email, new_email, password, status):
        data_tmp = self.get_data()
        for account in data_tmp["accounts"]:
            if account["email"] == old_email:
                account["email"] = new_email
                account["password"] = password
                account["status"] = status
                break
        print(data_tmp)
        self.data = data_tmp["accounts"]
        self.write_data(data_tmp)


def get_last_configs():
    with open(PATH_JSON_CONFIGS, 'r') as json_file:
        configs = json.load(json_file)
        url = configs["lastPostURL"]
        random_time_from = configs["defaultDiapasonRandomTime"][0]
        random_time_to = configs["defaultDiapasonRandomTime"][1]
        unit_random_time = configs["defaultRandomTimeUnit"]

    return {"url": url,
            "random_time_from": random_time_from,
            "random_time_to": random_time_to,
            "unit_random_time": unit_random_time,
            }

# ===========================================================================================
# ###########################################GUI#############################################
# ===========================================================================================

class GUI:

    def __init__(self):
        
        # --------------------------------------DATABASE--------------------------------------
        self.db_accounts = JSON_DB(PATH_JSON_FILE)
        # self.db_accounts.get_all_data()

        # ----------------------------------GET LAST CONFIGS----------------------------------
        last_data_configs = get_last_configs()
        self.url = last_data_configs["url"]
        self.random_time_from = last_data_configs["random_time_from"]
        self.random_time_to = last_data_configs["random_time_to"]
        self.unit_random_time = last_data_configs["unit_random_time"]

        # ---------------------------------BUILD MAIN WINDOW----------------------------------
        self.window = tk.Tk()
        self.window.title(NAME_TITLE_WINDOW)
        self.window.geometry(SIZE_WINDOW)
        self.build_input_URL_frame()
        self.build_table_accounts()
        self.build_legend_frame()
        self.build_set_random_time_area()
        self.build_run_area()

        # ------------------------------------RUN GUI----------------------------------------
        self.window.mainloop()


    # -----------------------------------MAIN SCRIPT-------------------------------------------

    def main_script_auto_like(self, url, login, password, hide_firefox=False):
        # options for headless (run background Firefox)
        options = Options()
        options.headless = hide_firefox
        options.page_load_strategy = 'none'
        # run Firefox
        self.driver = webdriver.Firefox(options=options)
        # driver = webdriver.Firefox()
        print('[+] Opened Firefox')
        logging.info('[+] Opened Firefox')

        # go to the URL
        self.driver.get(url)
        time.sleep(3)
        #check available URL
        if self.driver.title.endswith("Error"):
            print(f'[-] Url {url} is not available')
            logging.info(f'[-] Url {url} is not available')
            self.time_to_next_auto_like_var.set(f'Url is not available')
            self.driver.close()
            self.driver.quit()
            print(f'[+] Firefox closed')
            logging.info(f'[+] Firefox closed')
            self.thread.join()
            return
        else:
            print(f'[+] Went to site {url}')
            logging.info(f'[+] Went to site {url}')

        # click Sign In
        self.driver.find_element_by_class_name("fa-sign-in").click()
        print(f'[+] Clicked button "Sign In" by {login}')
        logging.info(f'[+] Clicked button "Sign In" by {login}')

        # enter email
        time.sleep(1)
        self.driver.find_element_by_id("user_email").send_keys(login)
        print(f'[+] Entered email {login}')
        logging.info(f'[+] Entered email {login}')

        # enter password
        self.driver.find_element_by_id("user_password").send_keys(password)
        print(f'[+] Entered password {len(password)*"*"}')
        logging.info(f'[+] Entered password {len(password)*"*"}')

        # click Sign In
        self.driver.find_element_by_class_name("bs-btn.bs-btn-default").click()
        print(f'[+] Clicked button "Sign In" by {login}')
        logging.info(f'[+] Clicked button "Sign In" by {login}')

        time.sleep(3)
        try:
            self.driver.find_element_by_id("user_email")
            print(f'[-] {login} — login or password is incorrect.')
            logging.info(f'[-] {login} — login or password is incorrect.')
            self.driver.close()
            self.driver.quit()
            print(f'[+] Firefox closed')
            logging.info(f'[+] Firefox closed')
            return "!"
        except:
            print(f'[+] {login} successfully authorized.')
            logging.info(f'[+] {login} successfully authorized.')

        # click Like
        try:
            self.driver.find_element_by_class_name("btn.btn-success.btn-sm").click()
            print(f'[+] Clicked button "Like" by {login}')
            logging.info(f'[+] Clicked button "Like" by {login}')
        except:
            print("[!] The post has already liked")
            self.driver.close()
            self.driver.quit()
            print(f'[+] Firefox closed')
            logging.info(f'[+] Firefox closed')
            return "?"

        # click Avatar
        self.driver.find_element_by_class_name("main-menu-bar-item.dropdown.bs-d-flex").click()
        print(f'[+] Clicked image "Avatar" by {login}')
        logging.info(f'[+] Clicked image "Avatar" by {login}')

        time.sleep(1)

        # click Sign Out
        self.driver.find_element_by_class_name("fa-sign-out").click()
        print(f'[+] Clicked button "Sign Out" by {login}')
        logging.info(f'[+] Clicked button "Sign Out" by {login}')

        time.sleep(3)
        self.driver.close()
        self.driver.quit()
        print(f'[+] Firefox closed')
        logging.info(f'[+] Firefox closed')
        return "+"

    # ----------------------------------AREA INPUT URL---------------------------------------

    def change_current_URL_text(self):
        URL = self.input_URL_post_field.get()
        if URL != '':
            self.current_URL_text.set(f"Current URL: {URL}")
        self.url = URL

        with open(PATH_JSON_CONFIGS, 'r') as json_file:
            data_tmp = json.load(json_file)

        data_tmp["lastPostURL"] = URL;

        with open(PATH_JSON_CONFIGS, 'w') as json_file:
            json.dump(data_tmp, json_file)

    def build_input_URL_frame(self):

        tk.Label(self.window, text="Post URL: ").place(x=0, y=5)

        self.input_URL_post_field = tk.Entry(self.window, width=50)
        self.input_URL_post_field.place(x=60, y=5)

        self.current_URL_text = tk.StringVar()

        self.current_URL_text.set(f"Current URL: {self.url}")

        current_URL_label = tk.Label(self.window, textvariable=self.current_URL_text)
        current_URL_label.place(x=0, y=30)

        input_enter_btn = tk.Button(self.window, text="Enter", command=self.change_current_URL_text)
        input_enter_btn.place(x=370, y=4)

    # ---------------------------------------AREA TABLE------------------------------------------

    def init_database(self):
        for account in self.db_accounts.get_all_data():
            self.table_accounts.insert("", "end", values=(account["email"], account["status"]))

    def add_account_to_db(self):
        new_email = self.input_email_field.get()
        new_pass = self.input_pass_field.get()

        if new_email != '' and new_pass != '':
            new_account = Account(new_email, new_pass)

            self.table_accounts.insert("", "end", values=(new_account.email, new_account.status))

            self.db_accounts.add_account_to_json(new_account.pack_to_dict())

        self.window_add.destroy()


    def build_add_account_to_database(self):
        self.window_add = tk.Tk()
        self.window_add.title("Add account")
        self.window_add.geometry("250x110")

        tk.Label(self.window_add, text="Enter please email:").grid(column=0, row=0)

        self.input_email_field = tk.Entry(self.window_add, width=40)
        self.input_email_field.grid(column=0, row=1, padx=2)

        tk.Label(self.window_add, text="Enter please password:").grid(column=0, row=2)

        self.input_pass_field = tk.Entry(self.window_add, width=40)
        self.input_pass_field.grid(column=0, row=3, padx=2)

        input_enter_btn = tk.Button(self.window_add, text="Enter", command=self.add_account_to_db)
        input_enter_btn.grid(column=0, row=4, pady=3)

    def modify_account_in_db(self):
        modify_email = self.input_email_field.get()
        modify_pass = self.input_pass_field.get()
        if modify_email != '' and modify_pass != '':
            if self.chk_reset_status:
                self.status_to_modify = '-'
            self.table_accounts.item(self.selected_item_to_modify, values=(modify_email, self.status_to_modify))
            self.db_accounts.change_values_account(self.email_to_modify, modify_email, modify_pass, self.status_to_modify)
        self.window_modify.destroy()

    def build_modify_account_in_database(self):
        self.window_modify = tk.Tk()
        self.window_modify.title("Modify account")
        self.window_modify.geometry("250x150")

        selected_items = self.table_accounts.selection()
        for item in selected_items:
            self.selected_item_to_modify = item
            self.email_to_modify = str(self.table_accounts.item(self.selected_item_to_modify)["values"][0])
            pass_to_modify = self.db_accounts.get_password_by_email(self.email_to_modify)
            self.status_to_modify = str(self.table_accounts.item(self.selected_item_to_modify)["values"][1])

        tk.Label(self.window_modify, text="Email:").grid(column=0, row=0)

        self.input_email_field = tk.Entry(self.window_modify, width=40)
        self.input_email_field.grid(column=0, row=1, padx=2)
        self.input_email_field.insert(-1, self.email_to_modify)
        tk.Label(self.window_modify, text="Password:").grid(column=0, row=2)

        self.input_pass_field = tk.Entry(self.window_modify, width=40)
        self.input_pass_field.grid(column=0, row=3, padx=2)
        self.input_pass_field.insert(-1, pass_to_modify)

        self.chk_reset_status = tk.IntVar()
        check_button_reset_status = tk.Checkbutton(self.window_modify, text='Reset status to \'-\'',
                                                   var=self.chk_reset_status,
                                                   onvalue=1, offvalue=0)
        check_button_reset_status.grid(column=0, row=4, pady=5, padx=5)

        input_enter_btn = tk.Button(self.window_modify, text="Modify", command=self.modify_account_in_db)
        input_enter_btn.grid(column=0, row=5, pady=3)

    def delete_account_from_database(self):
        selected_items = self.table_accounts.selection()
        for item in selected_items:
            email_to_delete = str(self.table_accounts.item(item)["values"][0])
            self.db_accounts.delete_account_from_json(email_to_delete)
            self.table_accounts.delete(item)

    def reset_all_accounts_in_database(self):
        all_items = self.table_accounts.get_children()
        # print(items)
        for item in all_items:
            email_to_change_status = str(self.table_accounts.item(item)["values"][0])
            self.db_accounts.change_status_account(email_to_change_status, '-')
            self.table_accounts.item(item, values=(email_to_change_status, '-'))

    def build_buttons_for_table(self):
        buttonContainer_db = tk.Frame(self.window)
        buttonContainer_db.place(x=230, y=50)

        btn_add = tk.Button(buttonContainer_db, text="Add", width=7, command=self.build_add_account_to_database)
        btn_add.grid(column=0, row=0, pady=15, padx=15)

        btn_modify = tk.Button(buttonContainer_db, text="Modify", width=7, command=self.build_modify_account_in_database)
        btn_modify.grid(column=0, row=1, pady=15, padx=15)

        btn_del = tk.Button(buttonContainer_db, text="Delete", width=7, command=self.delete_account_from_database)
        btn_del.grid(column=0, row=2, pady=15, padx=15)

        btn_del = tk.Button(buttonContainer_db, text="Reset All", width=7, command=self.reset_all_accounts_in_database)
        btn_del.grid(column=0, row=3, pady=15, padx=15)

    def build_table_accounts(self):

        self.table_accounts = ttk.Treeview(self.window, height=10)
        self.table_accounts['show'] = 'headings'

        scroll_bar = tk.Scrollbar(self.window, orient="vertical", command=self.table_accounts.yview)
        scroll_bar.place(x=213, y=50, height=227)

        self.table_accounts.configure(yscrollcommand=scroll_bar.set)
        self.table_accounts["columns"] = ("1", "2")
        self.table_accounts.column("1", width=150)
        self.table_accounts.column("2", width=50)
        self.table_accounts.heading("1", text="E-mail")
        self.table_accounts.heading("2", text="Status")
        self.table_accounts.place(x=10, y=50)

        self.table_accounts.tag_configure('done', background='green')
        self.table_accounts.tag_configure('ready', background='yellow')

        self.init_database()
        self.build_buttons_for_table()

    # ---------------------------------------AREA LEGEND-----------------------------------------

    def build_legend_frame(self):
        legendContainer = ttk.Labelframe(self.window)
        legendContainer.place(x=35, y=280)

        explainStatus = tk.Label(legendContainer, text="Status legend:", anchor=tk.W)
        explainStatus.grid(row=0, column=0)
        explain1 = tk.Label(legendContainer, text="[+] — well liked")
        explain1.grid(row=1, column=0)
        explain2 = tk.Label(legendContainer, text="[?] — already been liked")
        explain2.grid(row=2, column=0)
        explain2 = tk.Label(legendContainer, text="[!] — incorrect login or pass")
        explain2.grid(row=3, column=0)
        explain3 = tk.Label(legendContainer, text="[-] — haven't checked yet")
        explain3.grid(row=4, column=0)

    # ------------------------------------AREA RANDOM TIME---------------------------------------

    def set_random_time(self):

        tmp_random_time_from = int(self.input_time_from.get())
        tmp_random_time_to = int(self.input_time_to.get())

        if tmp_random_time_to > tmp_random_time_from:
            self.random_time_from = tmp_random_time_from
            self.random_time_to = tmp_random_time_to
            self.unit_random_time = self.choose_unit_time.get()
            self.current_random_time_text.set(f"from {self.random_time_from} to {self.random_time_to} {self.unit_random_time}")

    def build_set_random_time_area(self):

        tk.Label(self.window, text="Set random time-wait (from/to):").place(x=240, y=280)

        self.input_from_to_time = tk.Frame(self.window)
        self.input_from_to_time.place(x=240, y=300)

        self.input_time_from = tk.Entry(self.input_from_to_time, width=3)
        self.input_time_from.grid(row=0, column=0, pady=5)

        tk.Label(self.input_from_to_time, text="/").grid(row=0, column=1, pady=5)


        self.input_time_to = tk.Entry(self.input_from_to_time, width=3)
        self.input_time_to.grid(row=0, column=2, pady=5)

        self.choose_unit_time = ttk.Combobox(self.input_from_to_time, width=4)
        self.choose_unit_time['values'] = ("sec", "min")
        self.choose_unit_time.current(1)
        self.choose_unit_time.grid(row=0, column=3, padx=10, pady=5)

        btn_set_random_time = tk.Button(self.input_from_to_time, text="Set", width=5, command=self.set_random_time)
        btn_set_random_time.grid(row=1, column=3)

        tk.Label(self.window, text="Current random diapason: ").place(x=240, y=360)

        self.current_random_time_text = tk.StringVar()

        self.current_random_time_text.set(f"from {self.random_time_from} to {self.random_time_to} {self.unit_random_time}")

        current_random_time_label = tk.Label(self.window, textvariable=self.current_random_time_text)
        current_random_time_label.place(x=240, y=380)

    # -----------------------------------------AREA RUN------------------------------------------

    def change_status(self, email, status):
        items = self.table_accounts.get_children()
        for item in items:
            item_email = str(self.table_accounts.item(item)["values"][0])
            if item_email == email:
                self.table_accounts.item(item, values=([item_email, status]))
                self.table_accounts.item(item, tags=("done",))
                self.db_accounts.change_status_account(email, status)
                break

    def wait_for_next_auto_like(self):
        random_time = round(random.uniform(self.random_time_from, self.random_time_to), 1)
        if self.unit_random_time == "min":
            temp = random_time * 60
        if self.unit_random_time == "sec":
            temp = random_time

        while temp > -1:
            mins, secs = divmod(temp, 60)
            self.time_to_next_auto_like_var.set("{0}:{1}".format(int(mins), int(secs)))
            time.sleep(1)
            temp -= 1

    def check_thread(self, thread):
        if thread.is_alive():
            self.window.after(1000, lambda: self.check_thread(thread))
        else:
            thread.join()


    def bust_accounts(self):
        status_hide_firefox = bool(self.chk_state_firefox.get())
        accounts = self.db_accounts.get_accounts_with_minus()
        number_of_accounts = len(accounts)
        for account, number_of_acc in zip(accounts, range(number_of_accounts)):
            self.current_check_email = account["email"]
            self.current_check_password = account["password"]
            self.time_to_next_auto_like_var.set("Processing...\n{0}".format(self.current_check_email))
            status = self.main_script_auto_like(self.url,
                                       self.current_check_email,
                                       self.current_check_password,
                                       status_hide_firefox)
            self.change_status(self.current_check_email, status)
            if number_of_acc != number_of_accounts - 1:
                self.wait_for_next_auto_like()
        self.check_thread(self.thread)
        self.btn_run_script.config(state=tk.NORMAL)
        self.time_to_next_auto_like_var.set("DONE!!!")

    def run_thread_main_script(self):
        if self.url.startswith("http"):
            self.btn_run_script.config(state=tk.DISABLED)
            self.thread = Thread(target=self.bust_accounts)
            self.thread.daemon = True
            self.thread.start()
        else:
            self.time_to_next_auto_like_var.set("URL is empty!!!")

    def build_run_area(self):

        self.buttonContainer_run = ttk.Frame(self.window)
        self.buttonContainer_run.place(x=320, y=70)

        self.chk_state_firefox = tk.IntVar()
        check_button_hide_firefox = tk.Checkbutton(self.buttonContainer_run, text='Hide Firefox', var=self.chk_state_firefox,
                                                onvalue=1, offvalue=0)
        check_button_hide_firefox.grid(column=0, row=2, pady=15, padx=15)

        self.btn_run_script = tk.Button(self.buttonContainer_run, text="Run", command=self.run_thread_main_script, width=11, height=2)
        self.btn_run_script.grid(column=0, row=3, pady=5, padx=15)

        self.time_to_next_auto_like_var = tk.StringVar()
        time_to_next_auto_like_label = tk.Label(self.buttonContainer_run, textvariable=self.time_to_next_auto_like_var)
        time_to_next_auto_like_label.grid(column=0, row=4, pady=3)


app = GUI()
