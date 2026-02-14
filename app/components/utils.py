import time
import functools

# ANSI Colors
CYAN = "\033[96m"
YELLOW = "\033[93m"
RESET = "\033[0m"
BOLD = "\033[1m"
GREEN = "\033[92m"
MAGENTA = "\033[95m"
BLUE = "\033[94m"
RED = "\033[91m"

def time_it(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        

        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()
        
        duration = end - start
        
        # Fancy Print Message
        print(f"{CYAN}🛠️  {BOLD}{func.__name__}{RESET}")
        print(f" ╰─> ⏱️  Time: {YELLOW}{duration:.4f}s{RESET}")
        print(f"{MAGENTA}{'-' * 30}{RESET}")
        
        return result
    return wrapper

def print_summary_result(processed, skipped, total_files):
    print(f"📊 SUMMARY RESULT{RESET}")
    print(f"{MAGENTA}{'-' * 30}{RESET}")

    # Processed
    print(f" ✅  Processed Files : {GREEN}{len(processed)}{RESET}")
    if processed:
        for name in processed:
            print(f"     └─ {name}")
    else:
        print("     └─ None")

    # Skipped
    print(f"\n ⏭️  Skipped Files   : {YELLOW}{len(skipped)}{RESET}")
    if skipped:
        for name in skipped:
            print(f"     └─ {name}")
    else:
        print("     └─ None")

    # Total
    print(f"\n 📁  Total Files     : {BOLD}{total_files}{RESET}")
    print(f"{MAGENTA}{'-' * 30}{RESET}")

def print_process_flow_message(flow_name):
    print(f"{MAGENTA}{'-' * 30}{RESET}")
    print(f"{CYAN}{BOLD}{flow_name}{RESET}")
    print(f"{MAGENTA}{'-' * 30}{RESET}")