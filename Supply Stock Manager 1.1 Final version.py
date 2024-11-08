#Imported functions to be used throughout the code
#Allows the use of SQL throughout the code
import mysql.connector
#Import different parts of tkinter which was used for the GUI
import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
#Used to hash the passwords using MD5
import hashlib
import time


#The MySQL DB connection
mydb = mysql.connector.connect(
    host = "localhost",
    user = "root",
    passwd = "BisterJedder?17",
    database = "SSM")

#Allows for SQL statements to be used in the program
mycursor = mydb.cursor()
#All cursors created from this will be buffered by default
#Closes the program when Exit button is pressed
def Exit():
    root.destroy()
    print("Program successfully closed")


#universal calculate becuase the function will calculate the cost of a specified quantity for all records
def uni_calc():
    quant =  int(quant_entry.get())
    final_cost = cost * quant
    messagebox.showinfo("Supply Cost", "The cost of " + str(quant) + " units of " + s_name + " is £" + str(final_cost) + "")
    try:
        entry1.delete(0,END)
        entry1.insert(0, "£" + str(final_cost) + "")
    except:
        return True
    
#Function for the intial calculation screen
def calculate():
    def search1():
        global cost
        global s_name
        s_entry_get = search_ent.get()
        try:
            #Fetches the cost and supply name of the related supplies based on the users input
            mycursor.execute("SELECT Supply_Name FROM stock WHERE Supply_Name LIKE '%"+ s_entry_get +"%'")
            rows = mycursor.fetchone()
            mycursor.execute("SELECT Cost_£ FROM stock WHERE Supply_Name LIKE '%"+ s_entry_get +"%'")
            rows1 = mycursor.fetchone()
            #Tuples are used to receive the data from the database and place them in variables
            rows_tup = ();
            rows1_tup = ();
            for x in rows:
                rows_tup = (x,)

            for x in rows1:
                rows1_tup =(x,)
            s_name = rows_tup[0]
            cost = rows1_tup[0]
            try:
                lbl.pack_forget()
            except:
                messagebox.showinfo("Supply Price", "The cost per unit " + s_name + " is £" + str(cost) + "")
        except:
            messagebox.showinfo("Search Error", "No matching supply found")    
    global calc_screen
    global quant_entry
    calc_screen = Toplevel(main_app)
    calc_screen.title("Supply Stock Manager 1.1")
    calc_screen.geometry("300x250")
    #Fetches all product costs from SSM DB
    Label(calc_screen, text = "Calculate", bg = "black", fg = "white", width = 50, height = 1, font = ("Times New Roman", 13, "bold")).pack()
    Label(calc_screen, text = '''Type in the product name below
to find its price''', font = ("Times New Roman", 12)).pack()
    search_ent = Entry(calc_screen)
    search_ent.pack()
    search_btn = Button(calc_screen, text = "Search", bg = "black", fg = "white", command = search1).pack()
    Label(calc_screen)
    Label(calc_screen, text = '''Enter the quantity of the product searched
above that you want to calculate''', font = ("Times New Roman", 12)).pack()
    quant_entry = Entry(calc_screen)
    quant_entry.pack()
    calc_btn = Button(calc_screen, text = "Calculate", bg = "black", fg = "white", command = uni_calc).pack()

    
def update(rows):
    tv.delete(*tv.get_children())
    #for loop places fetched data into rows
    for i in rows:
        tv.insert('', 'end', values = i)
#allows the user to search for a supply    
def search():
    s_entry2 = entry.get()
    mycursor.execute("SELECT * FROM stock WHERE Supply_Name LIKE '%"+ s_entry2 +"%'")
    rows = mycursor.fetchall()
    update(rows)

#refreshes the table on the screen
def refresh():
    mycursor.execute("SELECT * FROM stock")
    rows = mycursor.fetchall()
    update(rows)
#Places the record the user double clicks on into the relevant entries so that the user can easily edit the table
def getrow(event):
    rowid = tv.identify_row(event.y)
    item = tv.item(tv.focus())
    #Clears the entry boxes before new values are placed in them
    ent1.delete(0, END)
    ent2.delete(0, END) 
    ent3.delete(0, END)
    ent4.delete(0, END)
    #Places the record the user double-clicks into the entry boxes
    ent1.insert(0, item['values'][0])
    ent2.insert(0, item['values'][1])
    ent3.insert(0, item['values'][2])
    ent4.insert(0, item['values'][3])

#updates the supplies in the database   
def update_supply():
    s_name = ent1.get()
    stock = ent2.get()
    b_stock = ent3.get()
    cost = ent4.get()
    #Allows the user to make changes to records in the database
    if messagebox.askyesno("Confirm Edit?", "Are you sure you want to update this supply"):
        query = "UPDATE stock SET Supply_Name = %s, Stock = %s, Buffer_Stock = %s, Cost_£ = %s WHERE Supply_Name = %s"
        mycursor.execute(query, (s_name, stock, b_stock, cost, s_name))
        mydb.commit()
        refresh()
        mycursor.execute("SELECT Buffer_Stock FROM stock WHERE Supply_Name = '" + s_name + "'")
        row = mycursor.fetchone()
        #tuple used to store data from the database into a variable
        row_tup = ();
        for x in row:
            row_tup = (x,)
        buff = row_tup[0]
        #Uses selection to output an alert when the buffer stock of any supply is matched or surpassed
        if int(stock) < int(buff):
            messagebox.showinfo("Attention", "The stock level of " + s_name + " has gone below the buffer limit")
        elif int(stock) == int(buff):
            messagebox.showinfo("Attention", "The stock level of " + s_name + " has reached the buffer limit")
        else:
            return True
    else:
        return True
#adds new record to the database
def add_new():
    s_name = ent1.get()
    stock = ent2.get()
    b_stock = ent3.get()
    cost = ent4.get()
    query = "INSERT INTO stock (Supply_Name, Stock, Buffer_Stock, Cost_£) VALUES ('" + s_name + "','" + stock + "','" + b_stock + "','" + cost + "')"
    if messagebox.askyesno("Create Record?", "Are you sure you want to create this record?"):
        #since supply name is the primary key "try" is used to ensure an error is not returned if the same supply is entered
        try:
            mycursor.execute(query)
        except:
            return True
    else:
        return True
    mydb.commit()
    refresh()
    

def delete_supply():
    #deletes the record of the selected supply
    supply_name = ent1.get()
    #messagebox used to receive the users confirmation
    if messagebox.askyesno("Confirm Delete?", "Are you sure you want to delete this record?"):
        query = "DELETE FROM stock WHERE Supply_Name = %s"
        sn = (supply_name,)
        mycursor.execute(query, sn)
        mydb.commit()
        refresh()
    else:
        return True


#edit screen
def edit():
    global rows
    global edit_screen
    global tv
    global entry
    global ent1
    global ent2
    global ent3
    global ent4
    global entry1
    edit_screen = Toplevel(main_app)
    edit_screen.title("Supply Stock Manager")
    edit_screen.geometry("1000x500")
    Label(edit_screen, text = "Current Stock Information", bg = "black", fg = "white", width = 100, height = 1, font = ("Times New Roman", 16, "bold")).pack()
    wrapper1 = LabelFrame(edit_screen, text = "Stock Table")
    wrapper2 = LabelFrame(edit_screen, text = "Search & Calculate")
    wrapper3 = LabelFrame(edit_screen, text = "Edit Table")
    wrapper1.pack(fill = "both", expand = "yes", padx = 20, pady = 10)
    wrapper2.pack(fill = "both", expand = "yes", padx = 20, pady = 10)
    wrapper3.pack(fill = "both", expand = "yes", padx = 20, pady = 10)
    #creating scrollbar in the treeview frame to scroll through the database
    tree_scroll = Scrollbar(wrapper1)
    tree_scroll.pack(side = RIGHT, fill = Y)
    #Treeview as "tv" to place database information on the screen using "ttk" which was imported earlier
    tv = ttk.Treeview(wrapper1, columns = (1,2,3,4), show = "headings", height = 5, yscrollcommand = tree_scroll.set)
    tv.pack()
    #configure scrollbar
    tree_scroll.config(command = tv.yview)
    #table headings
    tv.heading(1, text = "Supply Name")
    tv. heading(2, text = "Stock")
    tv.heading(3, text = "Buffer Stock")
    tv. heading(4, text = "Cost in £")
    #SQL query to fetch data and place in the frame
    mycursor.execute("SELECT * FROM stock")
    rows = mycursor.fetchall()
    update(rows)
    #Section for searching for data in the table and calculating
    lbl = Label(wrapper2, text = "Search")
    lbl.pack(side = tk.LEFT, padx = 10)
    entry = Entry(wrapper2)
    entry.pack(side = tk.LEFT, padx = 6)
    btn = Button(wrapper2, text = "Search", command = search)
    btn.pack(side = tk.LEFT, padx = 6)
    cbtn = Button(wrapper2, text = "Refresh", command = refresh)
    cbtn.pack(side = tk.LEFT, padx = 6)
    tv.bind('<Double 1>', getrow)

    calc_btn = Button(wrapper2, text = "Calculate", command = calculate)
    calc_btn.pack(side = tk.RIGHT, padx = 6)
    entry1 = Entry(wrapper2)
    entry1.pack(side = tk.RIGHT, padx = 6)
    lbl5 = Label(wrapper2, text = "Total Cost:")
    lbl5.pack(side = tk.RIGHT, padx = 10)

    #Stock data section
    lbl1 = Label(wrapper3, text = "Supply Name")
    lbl1.grid(row = 0, column = 0, padx = 5, pady = 3)
    ent1 = Entry(wrapper3)
    ent1.grid(row = 0, column = 1, padx = 5, pady = 3)
    lbl2 = Label(wrapper3, text = "Stock")
    lbl2.grid(row = 1, column = 0, padx = 5, pady = 3)
    ent2 = Entry(wrapper3)
    ent2.grid(row = 1, column = 1, padx = 5, pady = 3)
    lbl3 = Label(wrapper3, text = "Buffer Stock")
    lbl3.grid(row = 2, column = 0, padx = 5, pady = 3)
    ent3 = Entry(wrapper3)
    ent3.grid(row = 2, column = 1, padx = 5, pady = 3)
    lbl4 = Label(wrapper3, text = "Cost in £")
    lbl4.grid(row = 3, column = 0, padx = 5, pady = 3)
    ent4 = Entry(wrapper3)
    ent4.grid(row = 3, column = 1, padx = 5, pady = 3)
    up_btn = Button(wrapper3, text = "Update", command = update_supply)
    add_btn = Button(wrapper3, text = "Add New", command = add_new)
    deletebtn = Button(wrapper3, text = "Delete", command = delete_supply)
    add_btn.grid(row = 4, column = 0, padx = 5, pady = 3)
    up_btn.grid(row = 4, column = 1, padx = 5, pady = 3)
    deletebtn.grid(row = 4, column = 2, padx = 5, pady = 3)
    
    
    
#help screen
def help_sc():
    global help_screen
    help_screen = Toplevel(main_app)
    help_screen.title("Supply Stock Manager 1.1")
    help_screen.geometry("770x350")
    Label(help_screen, text = "Helpful Points", bg = "black", fg = "white", width = 100, height = 1, font = ("Times New Roman", 16, "bold")).pack()
    #label frames to hold information
    wrapper1 = LabelFrame(help_screen, text = "Edit Help")
    wrapper2 = LabelFrame(help_screen, text = "Calculate Help")
    wrapper1.pack(fill = "both", expand = "yes", padx = 20, pady = 10)
    wrapper2.pack(fill = "both", expand = "yes", padx = 20, pady = 10)
    #placing information on the screen
    lbl1 = Label(wrapper1, text = "- Double-clicking any record will place all its relevant details into the 4 entry boxes in the 'Edit Table' section", fg = "black", font = ("Times New Roman", 12))
    lbl1.pack()
    lbl2 = Label(wrapper1, text = "- Data in the 4 entry boxes in the 'Edit Table' section can be editied, added as a new record, or deleted", fg = "black", font = ("Times New Roman", 12))
    lbl2.pack()
    lbl3 = Label(wrapper1, text = "- Records can be found by typing in their supply name and clicking the search button in the 'Search & Calculate' section", fg = "black", font = ("Times New Roman", 12))
    lbl3.pack()
    lbl4 = Label(wrapper1, text = "- The refresh button is used to reset the data in the table after a search", fg = "black", font = ("Times New Roman", 12))
    lbl4.pack()

    lbl8 = Label(wrapper2, text = "- The calculate function can be accessed from both the main screen and the edit screen", fg = "black", font = ("Times New Roman", 12))
    lbl8.pack()
    lbl5 = Label(wrapper2, text = "- The calculate button is used to calculate the cost of a specified quantity of supplies", fg = "black", font = ("Times New Roman", 12))
    lbl5.pack()
    lbl6 = Label(wrapper2, text = "- The name of the supply must entered so the program knows which supply to calculate for", fg = "black", font = ("Times New Roman", 12))
    lbl6.pack()
    lbl7 = Label(wrapper2, text = "- The quantity of the supply required can then be entered and total cost will be displayed to the user", fg = "black", font = ("Times New Roman", 12))
    lbl7.pack()
    
    
   
    
#Logout screen   
def logout():
    #message box creates the 'yes' or 'no' processes
    if messagebox.askyesno("Confirm Logout?", "Are you sure you want to logout?"):
        #closes the main screen and re-opens the opening screen
        main_app.withdraw()
        root.deiconify()
        #closes the edit, calcualte, and help screens if they are open
        try:
            edit_screen.withdraw()
        except:
            return True
        try:
            calc_screen.withdraw()
        except:
            return True
        try:
            help_screen.withdraw()
        except:
            return True
    else:
        #closes message box
        return True
    
#main screen of the application
def main_app():
    global main_app
    main_app = Tk()
    main_app.title("Supply Stock Manager 1.1")
    main_app.geometry("750x250")
    main_app.configure(bg = "black")
    screen.withdraw()
    root.withdraw()
    import tkinter
    #creation and positioning of widgets
    title_label = Label(main_app, text = "Supply Stock Manager 1.1", bg = "black", fg = "white", font = ("Times New Roman", 20, "bold")).pack()
    calc_button = Button(main_app, text = "Calculate", width = 15, height = 1, bg = "sky blue", fg = "white", font = ("Times New Roman", 15, "bold"), command = calculate)
    calc_button.place(x = 0, y = 45)
    edit_button = Button(main_app, text = "Edit", width = 15, height = 1, bg = "sky blue", fg = "white", font = ("Times New Roman", 15, "bold"), command = edit)
    edit_button.place(x = 190, y = 45)
    help_button = Button(main_app, text = "Help", width = 15, height = 1, bg = "sky blue", fg = "white", font = ("Times New Roman", 15, "bold"), command = help_sc)
    help_button.place(x = 380, y = 45)
    logout_button = Button(main_app, text = "Logout", width = 15, height = 1, bg = "sky blue", fg = "white", font = ("Times New Roman", 15, "bold"), command = logout)
    logout_button.place(x = 570, y = 45)

    
    
#Selects a hash value equal to one stored in the database
#Allows the label showing the number of passowrd attempts to change
def label_change():
    my_string_var.set("Attempts -" + count2 +"")

#Removes login button preventing the user from accessing the program after 5 unsuccessful attempts
def button_remove():
    login_b.pack_forget()
    time.sleep(5)
    login_b.pack()
#Login page screen and funcitonality    
def login_page():
    global count
    global count2
    count = count + 1
    count2 = str(count)
    p3 = password.get()
    #Hashing of input
    p3_hash = hashlib.md5(p3.encode())
    finalp3 = p3_hash.hexdigest()
    mycursor.execute("SELECT Hashed_Password FROM passwords WHERE Hashed_Password = '" + finalp3 + "'")
    if mycursor.fetchall() == []:
        messagebox.showinfo("ATTENTION", "INCORRECT PASSWORD")
        #informs the user they have one more password attempt left
        if count == 4:
            messagebox.showinfo("ATTENTION", "ONE MORE ATTEMPT")
        #prevents the user from attempting another password entry
        if count > 4:
            messagebox.showinfo("ATTENTION", '''PASSWORD ATTEMPTS EXHAUSTED
CLOSE THE APPLICATION''')
            screen.withdraw()
            login_b.pack_forget()
    else:
        try:
            main_app()
        except TypeError:
            main_app.deiconify()
            screen.withdraw()
            root.withdraw()
#login screen
def Login():
    #global variables allow the variables to be used outside the function
    global screen
    global password
    global count
    global count_label
    global count1
    global my_string_var
    count = 0
    count1 = str(count)
    #creates the screen above root
    screen = Toplevel(root)
    screen.title("Supply Stock Manger 1.1")
    screen.geometry("500x150")
    Label(screen, text = "Please Enter your Password", bg = "black", fg = "white", width = 50, height = 1, font = ("Times New Roman", 13, "bold")).pack()
    password = StringVar()
    password_label = Label(screen).pack()
    password_entry = Entry(screen, textvariable = password, show = "*").pack()
    Label(screen).pack()
    Button(screen, text = "Login", width = 10, height = 1, bg = "black", fg = "white", command = lambda: [login_page(), label_change()]).pack()
    #increments the number of attempts by 1
    my_string_var = StringVar()
    my_string_var.set("Attempts - "+ count1 +"")
    count_label = Label(screen, textvariable = my_string_var, fg = "black", font = ("Times New Roman", 13, "bold")).pack()

# Function for comparing the new passwords inputted and seeing whether they match
def new_verify():
    #p1 and p2 represent password 1 and password 2
    p1 = password1.get()
    p2 = password2.get()
    if p1 == p2:
        if len(p1) and len(p2) < 7:
            #messagebox used to output error message
            messagebox.showinfo("ATTENTION", "THE PASSWORD YOU ENTERED IS TOO SHORT")
        else:
            #messageboc used to output confirmation message
            messagebox.showinfo("ATTENTION", "PASSWORD SAVED & CREATED")
            hp = p2
            #Hashes input and inserts into the DB
            hp1 = hashlib.md5(hp.encode())
            final_hash = str(hp1.hexdigest())
            #inserts hash value into the database
            sql = "INSERT INTO passwords (Hashed_Password) VALUES ('" + final_hash + "')"
            mycursor.execute(sql)
            mydb.commit()
            screen1.withdraw()
    else:
        messagebox.showinfo("ATTENTION", "THE PASSWORDS YOU ENTERED DO NOT MATCH")

# Function for the password screen and its functionality
def Create_Password():
    #Global variables allows the three variables below to be used outside the function
    global screen1
    global password1
    global password2
    screen1 = Toplevel(root)
    screen1.title("Supply Stock Manager 1.1")
    screen1.geometry("500x270")
    Label(screen1, text = "Create Password", bg = "black", fg = "white", width = 50, height = 1, font = ("Times New Roman", 13, "bold")).pack()
    Label(screen1).pack()
    Label(screen1, text = "Please Enter your Desired Password", bg = "black", fg = "white", height = 1, font = ("Times New Roman", 12, "bold")).pack()

    password1 = StringVar()
    password2 = StringVar()
    password1_label = Label(screen1).pack()
    password1_entry = Entry(screen1, textvariable = password1, show = "*").pack()
    Label(screen1).pack()
    Label(screen1, text = "Please re-enter the password", fg ="white", bg = "black", height = 1, font = ("Times New Roman", 12, "bold")).pack()
    Label(screen1).pack()
    password2_entry = Entry(screen1, textvariable = password2, show = "*").pack()
    lbl = Label(screen1, text = "*Password must be at least 7 characters long*", font = ("Times New Roman", 10)).pack()
    password2_label = Label(screen1).pack()
    Button(screen1, text = "Create Password", width = 15, height = 1, bg = "black", fg = "white", command = new_verify).pack()

# Main screen for the application
def root():
    global root
    global login_b
    root = Tk()
    root.title("Supply Stock Manager 1.1")
    root.geometry("500x250")
    Label(text = "Supply Stock Manager 1.1", bg = "black", fg = "white", width = "300", height = "2", font = ("Times New Roman", 13, "bold")).pack()
    Label(text = "").pack()
    login_b = Button(text = "Login", height = 2, width = 30, bg = "black", fg = "white", command = Login)
    login_b.pack()
    Label(text = "").pack()
    Button(text = "Create Password", height = 2, width = 30, bg = "black", fg = "white", command = Create_Password).pack()
    Label(text = "").pack()
    Button(text = "Exit", height = 2, width = 30, bg = "black", fg = "white", command = Exit).pack()
    root.mainloop()

root()
