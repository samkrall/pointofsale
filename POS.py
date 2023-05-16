import sys
import datetime
import pickle

class User:
    '''Class for users, 3 instance attributes, username, password and locked, class attribute
    that is a dictionary with the username as key and object as value, instance method for
    locking username, subclass admin underconstruction...'''

    all_users = {} #create class dict, dict{user:object}
    def __init__(self, username, password, locked): #__init__ func for user
        self.username = username
        self.password = password
        self.locked = locked
        User.all_users[self.username] = self #insert username:object into class dict

    def lock_user(self): #function to lock user
        self.locked = True

    @classmethod #alternative generator to create class instances from a list
    def from_list(cls, my_list):
        username, password, locked = my_list[0], my_list[1], bool(my_list[2])
        return cls(username, password, locked)

    @classmethod #load inventory data from file
    def load_users(cls):
        print('Loading user information.')
        with open('users.txt') as f:  # open file
            lines = f.readlines()  # readlines and separate by \n
            lines = lines[1:]  # remove top line (that has column names)
            for line in lines:  # iterate through lines
                item_info = line.split(',')[0:3]  # split on the comma and grab first 6 as list members
                User.from_list(item_info)  # create Item object from list
        print('User information loaded')

class Admin(User):
    def __init__(self, username, password, locked):
        super().__init__(username, password, locked)
        self.admin = 1
    def unlock_user(cls, username):
        User.all_users[username].locked = False

class Item:
    '''Item class for each item in inventory, 7 attributes: upc, description, item max qty,
    order threshold, replenishment order qty, items on hand and price.

    Class variable: a dictionary where the key is the UPC and the value is the object.

    Class methods: alternative constructor for creating objects from the retail store
    item data file, update inventory to file, report inventory, convert file into data alt
    constructor can use.
    '''
    item_dict = {} #class dictionary upc:object
    def __init__(
        self,
        upc,
        description,
        item_max_qty,
        order_threshold,
        replenishment_order_qty,
        item_on_hand,
        unit_price):
        self.upc = upc
        self.description = description
        self.item_max_qty = item_max_qty
        self.order_threshold = order_threshold
        self.replenishment_order_qty = replenishment_order_qty
        self.item_on_hand = item_on_hand
        self.unit_price = unit_price
        Item.item_dict[self.upc] = self #add upc:object to class dict


    @classmethod #alternative generator to create class instances from a list
    def from_list(cls, my_list):
        upc, description, item_max_qty, order_threshold, replenishment_order_qty, item_on_hand, unit_price = \
            my_list[0], my_list[1], my_list[2], my_list[3], my_list[4], my_list[5], my_list[6]
        return cls(upc, description, item_max_qty, order_threshold, replenishment_order_qty, item_on_hand, unit_price)

    @classmethod #output inventory as file
    def report_inventory(cls):
        f = open('inventory.txt', 'w')
        list_header = ['description', 'item_max_qty', 'order_threshold', 'item_on_hand', '\n']
        list_header = ','.join(list_header)
        f.write(list_header)
        for item in Item.item_dict.values():
            item_list = [item.description,item.item_max_qty,item.order_threshold,item.replenishment_order_qty,
                         str(item.item_on_hand), '\n']
            line = ','.join(item_list)
            f.write(line)
        f.close()

    @classmethod  # update inventory in RetailStoreItemData.txt
    def update_inventory(cls):
        print('Inventory updating...')
        f = open('RetailStoreItemData.txt', 'w')
        list_header = 'UPC,Description,Item_Max_Qty,Order_Threshold,replenishment_order_qty,Item_on_hand,Unit price,\
        Order_placed,,'
        f.write(list_header)
        for item in Item.item_dict.values():
            item_list = [item.upc,item.description,item.item_max_qty,item.order_threshold,item.replenishment_order_qty,
                         str(item.item_on_hand),str(item.unit_price), '\n']
            line = ','.join(item_list)
            f.write(line)
        f.close()
        print('Inventory Updated.')

    @classmethod #load inventory data from file
    def load_inventory(cls):
        with open('RetailStoreItemData.txt') as f:  # open file
            lines = f.readlines()  # readlines and separate by \n
            lines = lines[1:]  # remove top line (that has column names)
            for line in lines:  # iterate through lines
                item_info = line.split(',')[:7]  # split on the comma and grab first 6 as list members
                item_info[5] = float(item_info[5])  # change quatity on hand to float
                item_info[6] = float(item_info[6])  # change price to float
                Item.from_list(item_info)  # create Item object from list
class Menus:
    '''
    Menus contains static methods code for all of the menus
    '''
    @staticmethod
    def root_menu():  # root menu
        root_menu_input = input(
            'Please select your options\n1 = New Sale, 2 = Return Item/s, 3 = Backroom Operations, 4 = Logout, 9 = Exit Application\n')
        if root_menu_input == '1':
            Menus.initial_sale_menu()
        elif root_menu_input == '2':
            Menus.return_menu()
        elif root_menu_input == '3':
            Menus.backroom_menu()
        elif root_menu_input == '4':
            print('logging out user\n')
            Item.update_inventory()
            point_of_sale()
        elif root_menu_input == '9':
            Item.update_inventory()
            print('exit')
            raise SystemExit()

        else:
            print('error, input not recognized')
            Menus.root_menu()

    @staticmethod
    def initial_sale_menu():  # initial sale menu
        transaction_dict = {}
        Sale.sale_function(transaction_dict)

    @staticmethod
    def continue_sale_menu(transaction_dict):
        continue_sale_menu_input = input('1 = sell another item, 2 = Return Item/s, 9 = Complete Sale\t')
        if continue_sale_menu_input == '1':
            Sale.sale_function(transaction_dict)
        elif continue_sale_menu_input == '2':
            Sale.sale_return(transaction_dict)
        elif continue_sale_menu_input == '9':
            Sale.complete_sale(transaction_dict)
        else:
            print('error, input not recognized')
            Menus.continue_sale_menu(transaction_dict)

    @staticmethod
    def return_menu():
        receipt_file = open('state', 'rb')
        sale_dict = pickle.load(receipt_file)
        receipt_file.close()

        receipt_input = input('Please Enter the receipt number:\t')
        if receipt_input in sale_dict:
            return_menu_input = input('1 = Return Single Item, 2 = Return All Items\nPlease select your option\t')
            if return_menu_input == '1':
                Return.single_item_return(receipt_input, sale_dict)
            elif return_menu_input == '2':
                Return.all_item_return(receipt_input, sale_dict)
            else:
                print('Error')
                Menus.return_menu()
        else:
            print('Error, receipt not found.')
            Menus.return_menu()

    @staticmethod
    def backroom_menu():
        receipt_file = open('state', 'rb')
        sale_dict = pickle.load(receipt_file)
        receipt_file.close()
        backroom_input = input('1 = Inventory Report, 2 = Daily Sales, 3 = Monthly Sales, 4 = Root Menu\t')
        if backroom_input == '1':
            Backroom.inventory_report()
            Menus.backroom_menu()
        elif backroom_input == '2':
            Backroom.daily_sales(sale_dict)
        elif backroom_input == '3':
            Backroom.monthly_sales(sale_dict)
        elif backroom_input == '4':
            Menus.root_menu()
        else:
            print('error, input not recognized')
            Menus.backroom_menu()
class Sale:
    '''
    Sale contains all sale related functions, sale_return in Sale is for removing item(s) from
    receipt prior to sale completion.
    '''
    @staticmethod
    def sale_function(transaction_dict):  # adds to transaction dict, upc:[description, amount, price]
        upc_input = input('Please Enter the UPC ')
        if upc_input in Item.item_dict:
            print('You entered: ' + Item.item_dict[upc_input].description)
            quantity_input = int(input('Please Enter quantity '))
            if quantity_input <= Item.item_dict[upc_input].item_on_hand:
                print('The cost is ' + str(round(quantity_input * Item.item_dict[upc_input].unit_price, 2)))
                transaction_dict[upc_input] = [Item.item_dict[upc_input].description, quantity_input,
                                               Item.item_dict[upc_input].unit_price]
                Menus.continue_sale_menu(transaction_dict)
            else:
                print('You entered more ' + Item.item_dict[upc_input].description + ' than in inventory, try again.')
                Sale.sale_function(transaction_dict)
        else:
            print('UPC not found.')
            Sale.sale_function(transaction_dict)

    @staticmethod
    def sale_return(transaction_dict):  # sale return *IF ALREADY IN SALE* removes from dict by UPC
        upc_input = input('Please Enter the UPC to be returned ')
        if upc_input in transaction_dict:
            print(transaction_dict)  # todelete
            return_input = int(input('Number to be returned:\t'))
            if return_input < transaction_dict[upc_input][1]:
                transaction_dict[upc_input][1] = transaction_dict[upc_input][1] - return_input
                Menus.continue_sale_menu(transaction_dict)
            elif return_input == transaction_dict[upc_input][1]:
                del transaction_dict[upc_input]
                Menus.continue_sale_menu(transaction_dict)
            else:
                print('You are trying to return more than were purchased.')
                Sale.sale_return(transaction_dict)
        else:
            print('No item exists')
            Menus.continue_sale_menu(transaction_dict)

    @staticmethod
    def complete_sale(transaction_dict):
        receipt_file = open('state', 'rb')
        sale_dict = pickle.load(receipt_file)
        receipt_file.close()

        now = datetime.datetime.now()
        receipt = now.strftime("%Y%m%d%H%M%S")
        print('Your receipt number is ' + receipt)
        total = 0
        for transaction in list(transaction_dict.values()):
            total += (transaction[1] * transaction[2])
        print('Your total is ' + str(round(total, 2)))
        sale_dict[receipt] = transaction_dict
        for upc, transaction in transaction_dict.items():
            Item.item_dict[upc].item_on_hand = Item.item_dict[upc].item_on_hand - transaction[1]

        receipt_file = open('state', 'wb')
        pickle.dump(sale_dict, receipt_file)
        receipt_file.close()
        Menus.root_menu()
class Return:
    '''
    Return contains all functions related to returns
    '''
    @staticmethod
    def single_item_return(receipt_input, sale_dict):
        upc = input('Please enter UPC to be returned:\t')
        if upc in sale_dict[receipt_input]:
            print('You entered ' + sale_dict[receipt_input][upc][0])
            quantity_input = int(input('Please enter quantity:\t'))
            if quantity_input <= sale_dict[receipt_input][upc][1]:
                print('Return amount:\t' + str(quantity_input * sale_dict[receipt_input][upc][2]))
                sale_dict[receipt_input][upc][1] = sale_dict[receipt_input][upc][1] - quantity_input
                Item.item_dict[upc].item_on_hand = Item.item_dict[upc].item_on_hand + quantity_input
                receipt_file = open('state', 'wb')
                pickle.dump(sale_dict, receipt_file)
                receipt_file.close()
                Menus.root_menu()
            else:
                print('You entered more than were sold')
                Return.single_item_return(receipt_input, sale_dict)
        else:
            print('Item not found on receipt.')
            Return.single_item_return(receipt_input, sale_dict)

    @staticmethod
    def all_item_return(receipt_input, sale_dict):
        all_item_return_input = input('Are you sure you want to return all items? Y=yes, N=No\t')
        if all_item_return_input == 'Y':
            print('you entered:')
            total = 0
            for transaction in sale_dict[receipt_input].values():
                print(str(transaction[1]) + ' ' + transaction[0])
                total += (transaction[1] * transaction[2])
            print('Return Amount:\t' + str(round(total, 2)))
            for upc, transaction in sale_dict[receipt_input].items():
                Item.item_dict[upc].item_on_hand = Item.item_dict[upc].item_on_hand + transaction[1]
            del sale_dict[receipt_input]
            receipt_file = open('state', 'wb')
            pickle.dump(sale_dict, receipt_file)
            receipt_file.close()
            Menus.root_menu()
        elif all_item_return_input == 'N':
            Menus.return_menu()
        else:
            print('error, command not recognized')
            Return.all_item_return(receipt_input, sale_dict)
class Backroom:
    '''
    Backroom contains functions related to backroom operations
    '''
    @staticmethod
    def inventory_report():
        print('Sending inventory report to file inventory.txt')
        Item.report_inventory()
        print('inventory.txt updated')
        Menus.backroom_menu()

    @staticmethod
    def daily_sales(sale_dict):
        print('Sending daily sales to file daily_sales.txt')
        now = datetime.datetime.now()
        day = now.strftime("%Y%m%d")
        f = open('daily_sales.txt', 'w')
        total = 0
        f.write('receipt, Item, number sold, price, total\n')
        for receipt, information in sale_dict.items():
            if receipt.startswith(day):
                for transaction in information.values():
                    line = ', '.join([receipt, transaction[0], str(transaction[1]), str(transaction[2]),
                                      str(round(transaction[1]*transaction[2],2)),'\n'])
                    f.write(line)
                    total += transaction[1] * transaction[2]
        total_sales = ('\nTotal daily sales are: ' + str(round(total, 2)))
        f.write(total_sales)
        f.close()
        print('daily_sales.txt updated')
        Menus.backroom_menu()

    @staticmethod
    def monthly_sales(sale_dict):
        print('Sending monthly sales to file monthly_sales.txt')
        now = datetime.datetime.now()
        day = now.strftime("%Y%m")
        f = open('monthly_sales.txt', 'w')
        f.write('receipt, Item, number sold, price, total\n')
        total = 0
        for receipt, information in sale_dict.items():
            if receipt.startswith(day):
                for transaction in information.values():
                    line = ', '.join([receipt, transaction[0], str(transaction[1]), str(transaction[2]),
                                      str(round(transaction[1] * transaction[2], 2)), '\n'])
                    f.write(line)
                    total += transaction[1] * transaction[2]
        total_sales = ('\nTotal monthly sales are: ' + str(round(total, 2)))
        f.write(total_sales)
        f.close()
        print('monthly_sales.txt updated')
        Menus.backroom_menu()

'''
password gate is a decorator to check username/password
'''
def password_gate(func):
    def wrapper():
        username = input('Enter username:\t')
        if username in User.all_users: #check user_dict for username
            if User.all_users[username].locked == False: #check if user is locked
                attempt = 1
                while attempt <= 3: #while loop allowing 3 tries
                    password = input("Enter the password:\t")
                    if password == User.all_users[username].password:
                        return func()
                    else:
                        print(f"Incorrect password, attempt {attempt} of 3.")
                        attempt += 1
                print("Username locked, contact system admin.")
                User.all_users[username].lock_user() #call instance function to lock user
                wrapper() #return to enter username
            else:
                print('Username locked, contact system admin.')
                wrapper() #return to enter username
        else:
            print('username not found')
            wrapper() #return to enter username
    return wrapper
def point_of_sale():
    print('Welcome to the point of sale system.')
    User.load_users()
    start()
@password_gate
def start():
    Item.load_inventory()
    Menus.root_menu()

point_of_sale()
