#import statements
import sqlite3
import csv
import shutil

import requests

# establish connection to data file
conn = sqlite3.connect('/Users/bailey/PycharmProjects/pythonProject/Assignment1/DB/identifier.sqlite')
mycursor = conn.cursor()  # the cursor allows python to execute SQL statements


#create function to read in csv
def read_csv():
    source_path = '/Users/bailey/PycharmProjects/pythonProject/Assignment1/Students.csv'
    destination_path = '/Users/bailey/PycharmProjects/pythonProject/Assignment1/DB'

    #open file
    with open(source_path) as csvfile:
        reader = csv.DictReader(csvfile)


        # Iterate through the rows
        for row in reader:
            mycursor.execute("INSERT INTO Student('FirstName', 'LastName', 'GPA', 'Major',"
                                 "'Address', 'City', 'State', 'ZipCode', 'MobilePhoneNumber') "
                                 "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                                 (row['FirstName'],row['LastName'],row['GPA'],row['Major'], row['Address'],
                                  row['City'], row['State'], row['ZipCode'], row['MobilePhoneNumber'],))

            #initalize isDeleted to 0 so that all Students are "existing" until made to be otherwise ("deleted"--> 1)
            mycursor.execute("UPDATE Student SET isDeleted = 0")

            #update and sure database is consistent
            conn.commit()

            #print that records have been added to show function complete
            print('created new records in the Student table')
            #move csv records to done folder so that it can no longer be processed twice
            #return menu for next option

    # Move the file from source to destination so that it does not get read in multiple times
    shutil.move(source_path, destination_path)

    #print statement to let user know csv file moved now that it has been read
    print(f"File moved from {source_path} to {destination_path}")


#function to display students
def display_students():
    #make sure to only display students that are still valid... aka isDeleted should be 0
    mycursor.execute("SELECT * FROM Student WHERE isDeleted = 0")
    #get results of most recent query above and set to results to use in rest of function code
    results = mycursor.fetchall()

    #go through results using a for loop to print all results of select query
    for row in results:
        print(row)
    print("All students displayed.")


#function to add new student
def add_student():
    FirstName = input("Please enter the Students First Name: ")
    LastName = input("Please enter the students Last Name: ")

    while True: #continue to loop through until breaks are reached meaning valid value has been entered
        GPA_input = input("Please enter the GPA. GPA must be a number: ")
        try: #check validity of input
            GPA = float(GPA_input) #cast to float
            if GPA < 0: #needs to be greater than 0
                print("Error invalid GPA. Must be greate than 0")
            elif GPA > 5: #needs to be less than 5
                print("Error invalid GPA must be less than 5")
            else:
                break
        except ValueError: #must be a number entry-- caught by this ValueError
            print("Error: The entered value is not a number.")

    Major = input("Please enter the students Major: ")
    Address = input("Please enter the students Address: ")
    City = input("Please enter the students City: ")

    while True: #continue to loop through until breaks are reached meaning valid value has been entered
        state_input = input("Please enter the state in official USPS postal abbreviation (two letters): ")

        State = state_input.upper() #put input to upper case
        if len(State) == 2:
            state = state_input.upper()
            break
        else:
            print("Error: State must be only two letters. Please search up USPS state abbreviation if needed")


    while True: #continue to loop through until breaks are reached meaning valid value has been entered
        zip_input = input("Please enter a 5 digit numeric zip code: ")
        try:
            ZipCode = int(zip_input)
            if len(str(ZipCode)) == 5: #check that it is proper length
                break
            else: # if not, output error
                print("Error: Zip Code must be 5 numbers")
        except ValueError: #check that value is number
            print("Error: The entered value is not a number.")

    MobilePhoneNumber = input("Please enter a mobile phone number: ")

    try:
        add_query = "INSERT INTO Student (FirstName, LastName, GPA, Major, Address, City, State, ZipCode, MobilePhoneNumber) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"
        mycursor.execute(add_query, (FirstName, LastName, GPA, Major, Address, City, State, ZipCode, MobilePhoneNumber))
        #set isDeleted to 0 so that it can be deleted later if needed
        mycursor.execute("UPDATE Student SET isDeleted = 0 WHERE FirstName = ?", (FirstName))
        print("Student Added Successfully")

    except TypeError as e:
        print(f"An error occurred while inserting the student: {e}")

    finally:
        conn.commit()

#function to update student
def update_student():
    # check that field wishing to update is valid
    valid_fields = ['Major', 'Faculty Advisor', 'Mobile Phone Number']

    while True: #continue until valid ID presented
        student_id = input("What is the Student ID of the student you would like to update records for? ")
        try:
            student_id = int(student_id)
            if student_id <= 0: #check that student ID is above 0
                print(f"ERROR: Student ID {student_id} is not a valid ID value.")
                continue
            break
        except ValueError: #to catch when value entered not a number
            print("ERROR: ID value must be numeric.")

    # set value of what is coming from select statment above to go through and check that student_id entered
    mycursor.execute("SELECT COUNT(*) FROM Student")
    rows = mycursor.fetchall()


    if int(student_id) > int(rows[0][0]):   #does not exceed the number of entries in the Student table
        print(f"ERROR: Student ID {student_id} does not exist in the database.")
        return


    while True:
        update_field = input(f"What field would you like to update? ({', '.join(valid_fields)}) ")
        update_field = update_field.lower()  # Convert to lowercase after user input

        if update_field not in [field.lower() for field in valid_fields]:
            print("ERROR: Invalid field specified.")
            continue
        break

    new_value = input(f"Enter the new value for the {update_field}: ")

    mycursor.execute(f"UPDATE Student SET {update_field} = ? WHERE StudentID = ?",
                     (new_value.title(), student_id))

    conn.commit()
    print(f"The {update_field} of the student belonging to ID Number {student_id} has now been successfully"
          f" updated to {new_value}.")


def delete_students():
    update_query = ("UPDATE Student SET isDeleted = 1 WHERE StudentID = ?")
    check_query = ("SELECT isDeleted From Student WHERE StudentID = ?")


    while True: #continue until valid ID presented
        studentID_value = input("Please enter the Student ID of the student you wish to delete: ")
        mycursor.execute("SELECT COUNT(*) FROM Student")
        rows = mycursor.fetchall()

        try:
            studentID_value = int(studentID_value)
            if studentID_value <= 0: #check that student ID is above 0
                print(f"ERROR: Student ID {studentID_value} is not a valid ID value.")
                continue
            elif int(studentID_value) > int(rows[0][0]):   #does not exceed the number of entries in the Student table
                print(f"ERROR: Student ID {studentID_value} does not exist in the database.")
                continue
            break
        except ValueError: #to catch when value entered not a number
            print("ERROR: ID value must be numeric.")


    (mycursor.execute(check_query, (studentID_value,)))
    isDeleted_value = mycursor.fetchone()

    # go through results using a for loop to print all results of select query
    for row in isDeleted_value:
        if row == 0: #checks that the isDeleted value is 0 menaing the student is still in the table
            mycursor.execute(update_query, (studentID_value,))
            print('Student belonging to the Student ID: ', studentID_value, ' has been successfully deleted.')
        else:  # if isDeleted set to 1, student has already been deleted
            print(f"Student belonging to ID number {studentID_value} is no longer in the database, and cannot be deleted.")

    conn.commit()

#function for searching for a select student
def search_student(): #provide options to search
    user_choice = int(input("How would you like to search for a student? Please input the corresponding number to "
                            "one of the following options: \n 1) Major, 2) GPA, 3) City, 4) State, 5) Faculty Advisor \n"))

    while True: #use if statements to run through what is being selected to search by
        if user_choice == 1: # major
            user_input = input("Enter the Major you would like to search for: ")
            search_query = ("SELECT * FROM Student WHERE Major = ?")
            final_input = user_input.capitalize()
            break
        elif user_choice == 2: #GPA
            first_user_input = input("Enter the GPA you would like to search for: ")
            try:
                user_input = float(first_user_input)
                search_query = ("SELECT * FROM Student WHERE GPA = ?")
                final_input = str(user_input)
                break
            except ValueError:
                print("That is not a valid GPA please try again")
        elif user_choice == 3: #city
            user_input = input("Enter the City you would like to search for: ")
            search_query = ("SELECT * FROM Student WHERE City = ?")
            final_input = user_input.capitalize()
            break
        elif user_choice == 4: #state
            user_input = input("Enter the State you would like to search for: ")
            search_query = ("SELECT * FROM Student WHERE State = ?")
            final_input = user_input.capitalize()
            break
        elif user_choice == 5:
            user_input = input("Enter the FacultyAdvisor you would like to search for: ")
            search_query = ("SELECT * FROM Student WHERE FacultyAdvisor = ?")
            final_input = user_input.capitalize()
            break
        else:
            input("Invalid choice. Please choose again: ")


    mycursor.execute(search_query, (final_input,))
    results = mycursor.fetchall()
    if not results: #have something to output if search returns nothing
        print("No students found matching your input.")
    else: #otherwise print results
        for row in results:
            print(row)


def default():
    print("Invalid choice. Please try again.")


# create dictionary to hold menu options of the functions above
menu_options= {
    '1': read_csv,
    '2': display_students,
    '3': add_student,
    '4': update_student,
    '5': delete_students,
    '6': search_student
}

#while loop to continue outputting menu until manually exited with 0
while True:
    print("Menu:")
    print("1. Read in CSV")
    print("2. Display Students")
    print("3. Add New Student")
    print("4. Update Existing Student")
    print("5. Delete Student")
    print("6. Search For Student")
    print("0. Exit")

    choice = input("Enter your choice: ")

    if choice == '0':
        break

    #call function assigned to whichever number has been selected
    menu_options.get(choice, default)()



# ***** TESTING FUNCTIONS *****
#read_csv()
#add_student()
#display_students()
#update_student()
#delete_students()
#search_student()

#accidentally read through CSV file more than once
# mycursor.execute("DELETE FROM Student")
# print("Database has been reset and is currently empty.")
# conn.commit()


mycursor.close()
conn.close()