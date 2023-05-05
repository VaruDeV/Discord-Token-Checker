import threading
import time
import os
import requests
from requests import get, post 
import sys
from colorama import init, Fore, Style
init()

ascii_text = """
        
████████╗░█████╗░██╗░░██╗███████╗███╗░░██╗░░░░░░░█████╗░██╗░░██╗███████╗░█████╗░██╗░░██╗███████╗██████╗░
╚══██╔══╝██╔══██╗██║░██╔╝██╔════╝████╗░██║░░░░░░██╔══██╗██║░░██║██╔════╝██╔══██╗██║░██╔╝██╔════╝██╔══██╗
░░░██║░░░██║░░██║█████═╝░█████╗░░██╔██╗██║█████╗██║░░╚═╝███████║█████╗░░██║░░╚═╝█████═╝░█████╗░░██████╔╝
░░░██║░░░██║░░██║██╔═██╗░██╔══╝░░██║╚████║╚════╝██║░░██╗██╔══██║██╔══╝░░██║░░██╗██╔═██╗░██╔══╝░░██╔══██╗
░░░██║░░░╚█████╔╝██║░╚██╗███████╗██║░╚███║░░░░░░╚█████╔╝██║░░██║███████╗╚█████╔╝██║░╚██╗███████╗██║░░██║
░░░╚═╝░░░░╚════╝░╚═╝░░╚═╝╚══════╝╚═╝░░╚══╝░░░░░░░╚════╝░╚═╝░░╚═╝╚══════╝░╚════╝░╚═╝░░╚═╝╚══════╝╚═╝░░╚═╝
"""
print(ascii_text)

        
tokens_file = 'tokens.txt'
webhook_url = None

def check_tokens(tokens, print_lock):
    success_tokens = []

    for token in tokens:
        token = token.strip()

        if not token:
            continue

        if ":" in token:
            parts = token.split(":")
            if len(parts) == 3:
                email, password, token = parts
            elif len(parts) == 1:
                token = parts[0]
                email = None
                password = None
            else:
                print_lock.acquire()
                print(f"{Fore.RED}[INVALID] {token}{Style.RESET_ALL}")
                print_lock.release()
                with open('failed.txt', 'a') as f:
                    f.write(token + '\n')
                continue
        else:
            email = None
            password = None

        if len(token) < 59:
            print_lock.acquire()
            print(f"{Fore.RED}[INVALID] {token}{Style.RESET_ALL}")
            print_lock.release()
            with open('failed.txt', 'a') as f:
                f.write(token + '\n')
            continue

        headers = {'Authorization': token}

        try:
            response = get('https://discord.com/api/v6/users/@me', headers=headers)
            if response.status_code == 200:
                print_lock.acquire()
                if email and password:
                    print(f"{Fore.GREEN}[SUCCESS] {email}:{password}:{token}{Style.RESET_ALL}")
                else:
                    print(f"{Fore.GREEN}[SUCCESS] {token}{Style.RESET_ALL}")
                print_lock.release()

                success_tokens.append(token)



            def variant2(token):
                response = get('https://discord.com/api/v6/users/@me', headers=headers)
                if "You need to verify your account in order to perform this action." in str(response.content) or "401: Unauthorized" in str(response.content):
                    print_lock.acquire()
                    print(f"{Fore.RED}[INVALID] {token}{Style.RESET_ALL}")
                    print_lock.release()
                    with open('failed.txt', 'a') as f:
                        f.write(token + '\n')

                else:
                    print_lock.acquire()
                print(f"{Fore.YELLOW}[ERROR {response.status_code}] {token}{Style.RESET_ALL}")
                print_lock.release()
                with open('failed.txt', 'a') as f:
                    f.write(token + '\n')

        except Exception as e:
            print_lock.acquire()
            print(f"{Fore.YELLOW}[ERROR] {token}: {e}{Style.RESET_ALL}")
            print_lock.release()
            with open('failed.txt', 'a') as f:
                f.write(token + '\n')

            

    with open('success.txt', 'a') as f:
        f.write('\n'.join(success_tokens) + '\n')

tokens = []
with open(tokens_file, 'r') as f:
    for line in f:
        tokens.append(line.strip())

class Colors:
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'

if __name__ == '__main__':
    print_lock = threading.Lock()

    print(f"{Colors.BLUE}[INFO] Loading tokens...{Colors.END}")
    with open(tokens_file, 'r') as f:
        tokens = f.readlines()
    print(f"{Colors.BLUE}[INFO] Successfully loaded {len(tokens)} tokens{Colors.END}")

    time.sleep(0.5)
    num_threads = int(input(f"[INFO] Enter the number of threads: "))

# Split tokens into chunks for each thread
token_chunks = []
chunk_size = (len(tokens) + num_threads - 1) // num_threads
for i in range(0, len(tokens), chunk_size):
    token_chunks.append(tokens[i:i + chunk_size])

print_lock = threading.Lock()
success_lock = threading.Lock()
failed_lock = threading.Lock()

threads = []
for i in range(num_threads):
    try:
        thread = threading.Thread(target=check_tokens, args=(token_chunks[i], print_lock))
        threads.append(thread)
        thread.start()
    except IndexError:
        break

start_time = time.time()

for thread in threads:
    thread.join()

total_time = time.time() - start_time
print(f"{Fore.CYAN}Task Completed... Time taken: {total_time:.2f} seconds{Style.RESET_ALL}")
input("Press enter to exit.")
