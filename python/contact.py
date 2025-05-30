import json
import os
import time
import sys


try:
    from colorama import Fore, Style, init
    init(autoreset=True)
except ImportError:
    class Fore:
        RED = GREEN = YELLOW = BLUE = CYAN = MAGENTA = RESET = ""
    class Style:
        RESET_ALL = BRIGHT = ""

CONTACTS_FILE = "contacts.json"


def animate_message(message, duration=1.5):
    chars = "⣾⣽⣻⢿⡿⣟⣯⣷"
    start = time.time()
    i = 0
    while time.time() - start < duration:
        sys.stdout.write(f"\r{Fore.CYAN}{message} {chars[i % len(chars)]} ")
        sys.stdout.flush()
        time.sleep(0.1)
        i += 1
    sys.stdout.write("\r" + " " * 40 + "\r")



def print_banner():
    print(Fore.MAGENTA + Style.BRIGHT + r"""
   ____            _             _          __  __                                    
  / ___|___  _ __ | |_ _ __ ___ (_) ___    |  \/  | ___ _ __ ___   ___  _ __ ___  ___ 
 | |   / _ \| '_ \| __| '__/ _ \| |/ __|   | |\/| |/ _ \ '_ ` _ \ / _ \| '_ ` _ \/ __|
 | |__| (_) | | | | |_| | | (_) | | (__    | |  | |  __/ | | | | | (_) | | | | | \__ \
  \____\___/|_| |_|\__|_|  \___//_|\___|   |_|  |_|\___|_| |_| |_|\___/|_| |_| |_|___/

    """ + Style.RESET_ALL)


def load_contacts():
    if os.path.exists(CONTACTS_FILE):
        with open(CONTACTS_FILE, 'r') as f:
            return json.load(f)
    return []




def save_contacts(contacts):
    with open(CONTACTS_FILE, 'w') as f:
        json.dump(contacts, f, indent=4)




def add_contact():
    print(Fore.YELLOW + "\n🔹 Add New Contact")
    contact = {
        "store_name": input("🏪 Store Name: "),
        "phone": input("📞 Phone Number: "),
        "email": input("📧 Email: "),
        "address": input("📍 Address: ")
    }
    contacts.append(contact)
    animate_message("Saving contact")
    save_contacts(contacts)
    print(Fore.GREEN + "✅ Contact added successfully!")




def view_contacts():
    print(Fore.YELLOW + "\n📒 Contact List")
    if not contacts:
        print(Fore.RED + "No contacts available.")
        return
    for idx, c in enumerate(contacts, 1):
        print(f"\n{Fore.CYAN}{idx}. {c['store_name']}")
        print(f"{Fore.GREEN}   📞 Phone: {c['phone']}")
        print(f"{Fore.BLUE}   📧 Email: {c['email']}")
        print(f"{Fore.MAGENTA}   🏠 Address: {c['address']}")




def search_contact():
    keyword = input(Fore.YELLOW + "\n🔍 Enter name or phone to search: ").lower()
    animate_message("Searching")
    found = [c for c in contacts if keyword in c['store_name'].lower() or keyword in c['phone']]
    if not found:
        print(Fore.RED + "❌ No matching contact found.")
    else:
        for c in found:
            print(f"\n{Fore.CYAN}🔹 {c['store_name']}")
            print(f"{Fore.GREEN}   📞 {c['phone']} | {Fore.BLUE}📧 {c['email']} | {Fore.MAGENTA}🏠 {c['address']}")




def update_contact():
    name = input(Fore.YELLOW + "\n✏️ Enter the store name to update: ").lower()
    for c in contacts:
        if c['store_name'].lower() == name:
            print(Fore.CYAN + "Leave blank to keep existing value.")
            c['store_name'] = input(f"New Store Name ({c['store_name']}): ") or c['store_name']
            c['phone'] = input(f"New Phone ({c['phone']}): ") or c['phone']
            c['email'] = input(f"New Email ({c['email']}): ") or c['email']
            c['address'] = input(f"New Address ({c['address']}): ") or c['address']
            animate_message("Updating contact")
            save_contacts(contacts)
            print(Fore.GREEN + "✅ Contact updated successfully!")
            return
    print(Fore.RED + "❌ Contact not found.")





def delete_contact():
    name = input(Fore.YELLOW + "\n🗑️ Enter the store name to delete: ").lower()
    for i, c in enumerate(contacts):
        if c['store_name'].lower() == name:
            confirm = input(f"{Fore.RED}Are you sure you want to delete {c['store_name']}? (y/n): ")
            if confirm.lower() == 'y':
                animate_message("Deleting contact")
                contacts.pop(i)
                save_contacts(contacts)
                print(Fore.GREEN + "✅ Contact deleted.")
                return
    print(Fore.RED + "❌ Contact not found.")



def main():
    print_banner()
    while True:
        print(Fore.YELLOW + "\n====== Contact Manager Menu ======")
        print("1. ➕ Add Contact")
        print("2. 📋 View Contacts")
        print("3. 🔍 Search Contact")
        print("4. ✏️ Update Contact")
        print("5. 🗑️ Delete Contact")
        print("6. ❌ Exit")
        choice = input(Fore.CYAN + "\nSelect an option (1-6): ")

        if choice == '1':
            add_contact()
        elif choice == '2':
            view_contacts()
        elif choice == '3':
            search_contact()
        elif choice == '4':
            update_contact()
        elif choice == '5':
            delete_contact()
        elif choice == '6':
            print(Fore.MAGENTA + "\n👋 Thank you for using Contact Manager. Goodbye!\n")
            break
        else:
            print(Fore.RED + "❗ Invalid option. Please choose between 1-6.")




contacts = load_contacts()
main()
