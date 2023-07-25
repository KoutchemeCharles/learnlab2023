# AUTOGRADER IMPORT REMOVED

# ---------------------------------------------------------------------
# Lab: Contact List
# Course: CS110, Fall 2020
# ---------------------------------------------------------------------

# ---------------------------------------------------------------------
# Problem Statement:  Write a Python program that stores names and phone numbers
# for your classmates.  Your program will keep asking the user to input names and
# phone numbers until he/she types "DONE".
# Your program will then store the names/numbers in a dictionary,
# and allow the user to repeatedly type in names until he/she types "DONE".  
#    - If name is in the contact list, your program will output the corresponding phone number.  
#    - If the name is **not** in the contact list, your program will output "NOT FOUND"
# ---------------------------------------------------------------------
name = input()
contact = dict()

while name != 'DONE':
    phone_number = input()
    contact[name] = phone_number
    name = input()
    

check = input()
while check != 'DONE':
    if check in contact.keys():
        #if check == key:
        print(contact[check])
    else:
        print('NOT FOUND')
    check = input()