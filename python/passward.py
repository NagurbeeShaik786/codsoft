import string
import time
import sys
import secrets




try:
    from colorama import Fore, Style, init
    init(autoreset=True)
except ImportError:
    class Fore:
        RED = GREEN = YELLOW = BLUE = CYAN = MAGENTA = ""
    class Style:
        RESET_ALL = BRIGHT = ""




try:
    import winsound
except ImportError:
    winsound = None




def print_rainbow_text(text):
    colors = [Fore.RED, Fore.YELLOW, Fore.GREEN, Fore.CYAN, Fore.BLUE, Fore.MAGENTA]
    rainbow_text = ''.join([secrets.choice(colors) + char for char in text])
    print(rainbow_text + Style.RESET_ALL)





def animate_loading(message, duration=1.5):
    chars = "⣾⣽⣻⢿⡿⣟⣯⣷"
    start_time = time.time()
    while time.time() - start_time < duration:
        for c in chars:
            sys.stdout.write(f"\r{message} {c} ")
            sys.stdout.flush()
            time.sleep(0.1)
    sys.stdout.write("\r" + " " * 40 + "\r")





def generate_password(length, complexity_level):
    if length < 4:
        return Fore.RED + "❌ Password length must be at least 4 characters."

    sets = {
        'lower': string.ascii_lowercase,
        'upper': string.ascii_uppercase,
        'digits': string.digits,
        'symbols': string.punctuation
    }

    complexity = {
        1: ['lower', 'upper'],
        2: ['lower', 'upper', 'digits'],
        3: ['lower', 'upper', 'digits', 'symbols']
    }

    if complexity_level not in complexity:
        return Fore.RED + "❌ Invalid complexity level."

    print(Fore.YELLOW + "\n🔧 Generating password...")
    animate_loading(Fore.CYAN + "Mixing characters")

    selected_sets = complexity[complexity_level]
    all_chars = ''.join(sets[key] for key in selected_sets)

    # Ensure at least one from each set
    password = [secrets.choice(sets[key]) for key in selected_sets]
    remaining_length = length - len(password)

    password += [secrets.choice(all_chars) for _ in range(remaining_length)]
    secrets.SystemRandom().shuffle(password)

    print("\n")

    if winsound:
        try:
            for i in range(500, 1500, 100):
                winsound.Beep(i, 50)
        except:
            pass

    boxed = (
        Fore.GREEN + Style.BRIGHT +
        f"╔{'═' * (len(password) + 4)}╗\n" +
        f"║ ★ {''.join(password)} ★ ║\n" +
        f"╚{'═' * (len(password) + 4)}╝"
    )
    return boxed




def main():
    print_rainbow_text(r"""
     ____                        ____              
    |  _ \ __ _ ___ ___  _ __   / ___|  __ _ _ __ 
    | |_) / _` / __/ _ \| '_ \  \___ \ / _` | '__|
    |  __/ (_| | (_| (_) | | | |  ___) | (_| | |   
    |_|   \__,_|\___\___/|_| |_| |____/ \__,_|_|   
    """)

    try:
        length = int(input(Fore.YELLOW + "\n🔢 Enter password length (4-64): "))
        if not 4 <= length <= 64:
            print(Fore.RED + "❌ Length must be between 4-64.")
            return

        print(Fore.YELLOW + "\n🔐 Password Complexity Levels:")
        print(Fore.CYAN + " 1. Basic (Letters)")
        print(Fore.BLUE + " 2. Strong (Letters + Numbers)")
        print(Fore.MAGENTA + " 3. Fort Knox (Letters + Numbers + Symbols)")
        complexity = int(input(Fore.YELLOW + "\n⚡ Choose complexity (1-3): "))

        result = generate_password(length, complexity)
        print("\n" + result + Style.RESET_ALL)

        print_rainbow_text(r"""
         /\_/\
        ( o.o )
         > ^ <
        /_ - _\
        """)

    except ValueError:
        print(Fore.RED + "\n")
        for _ in range(3):
            sys.stdout.write("\r🚫 INVALID INPUT! ")
            sys.stdout.flush()
            time.sleep(0.2)
            sys.stdout.write("\r   INVALID INPUT! ")
            sys.stdout.flush()
            time.sleep(0.2)
        print("\n")





if __name__ == "__main__":
    main()
