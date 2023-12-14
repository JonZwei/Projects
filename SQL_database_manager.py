import mysql.connector
from mysql.connector import errorcode


#############################functions##############################
## Controls what function to run after user input    
def switch(x):
    
    global cm_connection
    if x == '1':
        UserTableView()
        print_table_user()
    elif x == '2':
        AdminTableView()
        print_table_admin()
    elif x == '3':
        query_one_user()
    elif x == '4':
        add_user()
    elif x == '5':
        delete_user()
    elif x == '6':
        update_password()
    elif x == 'q':
        cm_connection.commit()
        global done
        done = False
    else:
        print('\nPlease enter a valid response\n')

## Create view for the user database as a user   
def UserTableView():
    global cm_connection
    user_cursor = cm_connection.cursor()
    user_view = ('CREATE OR REPLACE VIEW UserTableView (FirstName,' +
                 'LastName, UserName, JobTitle) AS SELECT FirstName, ' +
                 'LastName, UserName, JobTitle FROM usertable')
    user_cursor.execute(user_view)
    user_cursor.close()

## Create view for the user database as an admin             
def AdminTableView():
    global cm_connection
    admin_cursor = cm_connection.cursor()
    admin_view = ('CREATE OR REPLACE VIEW AdminTableView (FirstName,' +
                  'LastName, UserName, Password, JobTitle) AS SELECT ' + 
                  'FirstName, LastName, UserName, Password, JobTitle ' +
                  'FROM usertable')
    admin_cursor.execute(admin_view)
    admin_cursor.close()

##input for user query
def query_one_user():
    global cm_connection
    print('\nQuery a single user')
    while True:
        try:
            query_user_input = input('Enter the username: ')
            if query_user_input.isalpha():
                break
            else:
                raise TypeError
        except TypeError:
            print("Not a valid username")
            return
        
    query_user(query_user_input)
    
## Query a single user
def query_user(query_user_input):
    global cm_connection
    query_user_cursor = cm_connection.cursor()
    query_user_query = ('SELECT FirstName, LastName, UserName, JobTitle' +
                       ' FROM usertable WHERE UserName = %s')
    query_tuple = [query_user_input]
    try:
        query_user_cursor.execute(query_user_query, query_tuple)
    except (cm_connection.Error, cm_connection.Warning) as err:
        print(err)
        query_one_user()
    else:
        results = query_user_cursor.fetchall()
        if not results:
            print('No user exists')
            return False
        for row in results:
            print('{} {} {} {}'.format(row[0], row[1], row[2], row[3]))    
        query_user_cursor.close()

## Print Single User
def user_exists(username):
    global cm_connection
    query_user_cursor = cm_connection.cursor()
    query_user_query = ('SELECT FirstName, LastName, UserName, JobTitle' +
                       ' FROM usertable WHERE UserName = %s')
    query_tuple = [username]
    try:
        query_user_cursor.execute(query_user_query, query_tuple)
    except (cm_connection.Error, cm_connection.Warning) as err:
        print(err)
        return
    else:
        results = query_user_cursor.fetchall()
        if not results:
            print('No user exists')
            return False
        else:
            return True
        query_user_cursor.close()
    
## Add a new user
def add_user():
    global cm_connection
    print('\nAdd a new user')
    add_first = input('Enter the users first name: ')
    add_last = input('Enter the users last name: ')
    add_username = add_first[0] + add_last
    if (len(add_username) > 8):
        add_username = add_username[:8]
    if user_exists(add_username):
        print('User already exists')
        return
    print('\nNew username is: {}'.format(add_username))
    add_job = input('Enter {}`s job: '.format(add_first))
    add_pw = input('Enter a password of 20 characters or less: ')
    if(len(add_pw)>20):
        while(len(add_pw)>20):
            add_pw = input('Input a shorter password (<=20 characters)')
    
    add_query = ('INSERT INTO usertable VALUES(%s, %s, %s, ' +
                 " %s, aes_encrypt(%s, '" + KEY + "'));")
    add_cursor = cm_connection.cursor()
    user_list = [add_username, add_first, add_last, add_job, add_pw]
    try:
        add_cursor.execute(add_query, user_list)
    except (cm_connection.Error, cm_connection.Warning) as err:
        print(err)
        add_user()
    else:
        add_cursor.close()
        query_user(add_username)
    
## Delete a user
def delete_user():
    global cm_connection
    delete_input = input('\nEnter the username you want to delete: ')
    if not user_exists(delete_input):
        return
    delete_cursor = cm_connection.cursor()
    delete_query = ('DELETE FROM usertable WHERE username = %s')
    delete_tuple = [delete_input]
    try:
        delete_cursor.execute(delete_query, delete_tuple)
    except (cm_connection.Error, cm_connection.Warning) as err:
        print(err)
    else:
        delete_cursor.close()

## Update user password
def update_password():
    global cm_connection
    global KEY
    count = 0
    pwdone = True
    print('\nChange user password')
    update_name = input('Enter your username: ')
    pw_query = ("SELECT aes_decrypt(Password, '" + KEY + 
                  "') FROM usertable WHERE UserName = '" + update_name + "';")
    update_cursor = cm_connection.cursor()
    try:
        update_cursor.execute(pw_query)
    except (cm_connection.Error, cm_connection.Warning) as err:
        print(err)
        
    else:
        for row in update_cursor.fetchall():
            current_pw = row[0].decode()
        test_pw = input('Enter your password: ')
        
        while pwdone:
            if current_pw.casefold() == test_pw.casefold():
                test_new = input('Enter a new password: ')
                pwdone = False
            elif current_pw != test_pw and count < 2:
                print(current_pw + test_pw)
                test_pw = input('Wrong password try again: ')
                count += 1
            elif count > 2:
                print('\nToo many password attempts')
                pwdone = False
                update_cursor.close()
                return
            else:
                pwdone = False
                update_cursor.close()
                return
        if count <= 2:        
            new_pw = [test_new]
            new_query = ("UPDATE usertable SET Password = aes_encrypt(%s, '" +
                         KEY + "') WHERE UserName = '" + update_name + "';")
            update_cursor.execute(new_query, new_pw)
            
        update_cursor.close()
    
## Print out the Table as a user    
def print_table_user():
    global cm_connection
    table_cursor = cm_connection.cursor()
    table_query = ('SELECT * FROM UserTableView')
    table_cursor.execute(table_query)
    for row in table_cursor.fetchall():
        print('{} {} {} {}'.format(row[0], row[1], row[2], row[3]))
    table_cursor.close()

## Print out the Table as admin
def print_table_admin():
    global cm_connection
    table_cursor = cm_connection.cursor()
    table_query = ('SELECT * FROM AdminTableView')
    table_cursor.execute(table_query)
    for row in table_cursor.fetchall():
        print('{} {} {} {} {}'.format(row[0],row[1],row[2],row[3].decode(encoding='latin-1'),row[4]))
    table_cursor.close()

    
###########################end of functions##########################

#############################Main####################################


## Declare variables
user_input = 'a'
done = True
KEY = 'SpaceBalls'


## Log into database
try:
    cm_connection = mysql.connector.connect(
        user="CS509",
        password="CS509",
        host="127.0.0.1",
        port=3306,
        database="demo509")

except mysql.connector.Error as err:
    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        print('Invalid credentials')
    elif err.errno == errorcode.ER_BAD_DB_ERROR:
        print('Database not found')
    else:
        print('Cannot connect to database:', err)

else:
##  Main

    while done:
        user_input = input('******************************' + 
                                '\n1 - Show Users (as user)' + 
                                '\n2 - Show Users (as admin)' + 
                                '\n3 - Query One User (as admin)'
                                '\n4 - Add One User' +
                                '\n5 - Delete User' +
                                '\n6 - Change User Password' +
                                '\nq = quit the program' + 
                                '\n******************************\n')
        switch(user_input)
    
    cm_connection.close()






