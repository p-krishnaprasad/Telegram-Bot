import time
import functools

def time_it(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # ANSI Colors
        CYAN = "\033[96m"
        YELLOW = "\033[93m"
        RESET = "\033[0m"
        BOLD = "\033[1m"

        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()
        
        duration = end - start
        
        # Fancy Print Message
        print(f"{CYAN}🛠️  {BOLD}{func.__name__}{RESET}")
        print(f" ╰─> ⏱️  Time: {YELLOW}{duration:.4f}s{RESET}")
        print("-" * 30)
        
        return result
    return wrapper