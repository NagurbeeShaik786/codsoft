import math
from colorama import Fore, Style, init
import os
import time

init(autoreset=True)


history = []
last_result = None

def add(numbers):
    return sum(numbers)




def subtract(numbers):
    result = numbers[0]
    for n in numbers[1:]:
        result -= n
    return result



def multiply(numbers):
    result = 1
    for n in numbers:
        result *= n
    return result



def divide(numbers):
    try:
        result = numbers[0]
        for n in numbers[1:]:
            if n == 0:
                raise ZeroDivisionError
            result /= n
        return result
    except ZeroDivisionError:
        return "❌ Error: Division by zero."



def modulus(a, b):
    try:
        return a % b
    except ZeroDivisionError:
        return "❌ Error: Modulus by zero."



def percentage(a, b):
    try:
        return (a / b) * 100
    except ZeroDivisionError:
        return "❌ Error: Division by zero."



def scientific(operation, value):
    if operation == "sin":
        return math.sin(math.radians(value))
    elif operation == "cos":
        return math.cos(math.radians(value))
    elif operation == "tan":
        try:
            return math.tan(math.radians(value))
        except:
            return "❌ Undefined"
    elif operation == "log":
        if value > 0:
            return math.log10(value)
        else:
            return "❌ Logarithm undefined"
    elif operation == "sqrt":
        if value >= 0:
            return math.sqrt(value)
        else:
            return "❌ Square root of negative"
    elif operation == "fact":
        if value >= 0 and value == int(value):
            return math.factorial(int(value))
        else:
            return "❌ Invalid input"
    elif operation == "exp":
        return math.exp(value)



def get_input(prompt, allow_ans=False):
    global last_result
    while True:
        try:
            user_input = input(Fore.YELLOW + prompt).strip()
            if allow_ans and user_input.lower() == "ans":
                if last_result is None:
                    print(Fore.RED + "No previous result available")
                    continue
                return last_result
            return float(user_input)
        except ValueError:
            print(Fore.RED + "Invalid number. Please try again.")




def get_number_list(prompt):
    global last_result
    while True:
        try:
            nums = input(Fore.YELLOW + prompt).split()
            parsed_nums = []
            for num in nums:
                if num.lower() == "ans":
                    if last_result is None:
                        raise ValueError("No previous result available")
                    parsed_nums.append(last_result)
                else:
                    parsed_nums.append(float(num))
            return parsed_nums
        except ValueError as e:
            print(Fore.RED + f"Error: {str(e)}")
        except Exception:
            print(Fore.RED + "Invalid input. Please enter numbers separated by spaces")




def print_history():
    if not history:
        print(Fore.YELLOW + "\nNo history available")
        return
    
    print(Fore.CYAN + "\n📜 Calculation History:")
    for i, entry in enumerate(history[-5:], 1):
        print(f"{Fore.MAGENTA}{i}. {entry['operation']:20} {Fore.GREEN}= {entry['result']}")




def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')




def animate_text(text, color=Fore.CYAN, delay=0.05):
    for char in text:
        print(color + char, end='', flush=True)
        time.sleep(delay)
    print()




def record_history(operation, result):
    global history, last_result
    last_result = result
    history.append({"operation": operation, "result": result})
    if len(history) > 10:
        history.pop(0)




def calculator():
    global history, last_result
    
    clear_screen()
    animate_text("🚀 Python Scientific Calculator", Fore.MAGENTA)
    print(Fore.CYAN + "-" * 50)



    while True:
        print(Fore.CYAN + "\nSelect an operation:")
        print(Fore.GREEN + " 1. Addition")
        print(Fore.GREEN + " 2. Subtraction")
        print(Fore.GREEN + " 3. Multiplication")
        print(Fore.GREEN + " 4. Division")
        print(Fore.BLUE + " 5. Modulus (a % b)")
        print(Fore.BLUE + " 6. Percentage (a is what % of b)")
        print(Fore.MAGENTA + " 7. Scientific Functions")
        print(Fore.YELLOW + " 8. View History")
        print(Fore.YELLOW + " 9. Clear History")
        print(Fore.RED + " 0. Exit")
        
        choice = input(Fore.CYAN + "\nEnter your choice (0-9): ")

        if choice == '0':
            print(Fore.MAGENTA + "\n👋 Thank you for using the calculator!")
            break

        elif choice == '8':
            print_history()
            continue
            
        elif choice == '9':
            history = []
            last_result = None
            print(Fore.GREEN + "\n✅ History cleared")
            continue
            
        try:
            if choice == '1':
                numbers = get_number_list("Enter numbers separated by space (type 'ans' for previous result): ")
                result = add(numbers)
                operation = " + ".join(map(str, numbers))
                print(Fore.GREEN + f"\n✅ Result: {result}")
                record_history(operation, result)

            elif choice == '2':
                numbers = get_number_list("Enter numbers separated by space (minuend first): ")
                result = subtract(numbers)
                operation = " - ".join(map(str, numbers))
                print(Fore.GREEN + f"\n✅ Result: {result}")
                record_history(operation, result)

            elif choice == '3':
                numbers = get_number_list("Enter numbers to multiply: ")
                result = multiply(numbers)
                operation = " × ".join(map(str, numbers))
                print(Fore.GREEN + f"\n✅ Result: {result}")
                record_history(operation, result)

            elif choice == '4':
                numbers = get_number_list("Enter numbers (dividend first): ")
                result = divide(numbers)
                operation = " ÷ ".join(map(str, numbers))
                print(Fore.GREEN + f"\n✅ Result: {result}")
                if isinstance(result, float) or isinstance(result, int):
                    record_history(operation, result)

            elif choice == '5':
                a = get_input("Enter first number (a): ", True)
                b = get_input("Enter second number (b): ", True)
                result = modulus(a, b)
                operation = f"{a} % {b}"
                print(Fore.GREEN + f"\n✅ Result: {result}")
                if not isinstance(result, str):
                    record_history(operation, result)

            elif choice == '6':
                a = get_input("Enter part value (a): ", True)
                b = get_input("Enter total value (b): ", True)
                result = percentage(a, b)
                operation = f"{a} is what % of {b}"
                print(Fore.GREEN + f"\n✅ Result: {result}%")
                if not isinstance(result, str):
                    record_history(operation, result)

            elif choice == '7':
                print(Fore.MAGENTA + "\nScientific Functions:")
                print(" sin, cos, tan, log, sqrt, fact, exp")
                op = input(Fore.YELLOW + "Enter operation: ").lower()
                if op not in ["sin", "cos", "tan", "log", "sqrt", "fact", "exp"]:
                    print(Fore.RED + "❌ Invalid operation")
                    continue
                    
                val = get_input("Enter value: ", True)
                result = scientific(op, val)
                operation = f"{op}({val})"
                print(Fore.GREEN + f"\n✅ Result: {result}")
                if not isinstance(result, str):
                    record_history(operation, result)

            else:
                print(Fore.RED + "❌ Invalid choice. Please try again.")
                
        except KeyboardInterrupt:
            print(Fore.RED + "\nOperation cancelled")
            continue
            
        # Pause before clearing screen
        input(Fore.CYAN + "\nPress Enter to continue...")
        clear_screen()
        animate_text("🚀 Python Scientific Calculator", Fore.MAGENTA)
        print(Fore.CYAN + "-" * 50)



if __name__ == "__main__":
    calculator()