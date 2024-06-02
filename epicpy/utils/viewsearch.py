import re
from concurrent.futures import ProcessPoolExecutor, as_completed
from multiprocessing import cpu_count

from epicpy.utils.apputils import timeit_decorator


# **************************************************************
# SERIAL VERSION (fast enough, but slower than parallel version)
# **************************************************************


def search_chunk(params):
    lines, pattern, start, end = params
    for i in range(start, end):
        if pattern.search(lines[i]):
            return i
    return -1


def find_next_index_with_target_serial(lines, target, current_line, direction="forward", is_regex=False):
    # Compile the pattern based on whether the target is a regex
    if is_regex:
        pattern = re.compile(target)  # , re.IGNORECASE)
    else:
        pattern = re.compile(re.escape(target))  # , re.IGNORECASE)

    if direction == "forward":
        for i in range(current_line, len(lines)):
            if pattern.search(lines[i]):
                return i
    elif direction == "backward":
        for i in range(current_line, -1, -1):
            if pattern.search(lines[i]):
                return i

    return -1  # Return -1 if the target is not found


# *********************************************************************
# PARALLEL VERSION (fast! uses concurrent.futures with multiprocessing)
# *********************************************************************


def find_next_index_in_chunk(lines, target, start_index, ignore_case, direction):
    # Compile the pattern for regex matching
    if ignore_case:
        pattern = re.compile(target, re.IGNORECASE)
    else:
        pattern = re.compile(target)

    if direction == "forward":
        for i, line in enumerate(lines):
            if pattern.search(line):
                return start_index + i
    elif direction == "backward":
        for i in range(len(lines) - 1, -1, -1):
            if pattern.search(lines[i]):
                return start_index + i
    return -1


def search_cpu_count() -> int:
    count = (cpu_count() - 2) if cpu_count() > 3 else (cpu_count() - 1)
    return count if count else cpu_count()


def find_next_index_with_target_parallel_concurrent(
    lines: list[str],
    target: str,
    start_line: int = 0,
    direction: str = "forward",
    is_regex: bool = False,
    ignore_case: bool = False,
    num_workers: int = cpu_count() - 2,
):
    if not is_regex:
        target = re.escape(target)

    chunk_size = len(lines) // num_workers
    futures = []
    with ProcessPoolExecutor(max_workers=num_workers) as executor:
        if direction == "forward":
            for i in range(start_line, len(lines), chunk_size):
                chunk_end = min(i + chunk_size, len(lines))
                chunk = lines[i:chunk_end]
                futures.append(executor.submit(find_next_index_in_chunk, chunk, target, i, ignore_case, direction))
        elif direction == "backward":
            for i in range(start_line, -1, -chunk_size):
                chunk_start = max(i - chunk_size, 0)
                chunk = lines[chunk_start:i]
                futures.append(
                    executor.submit(find_next_index_in_chunk, chunk, target, chunk_start, ignore_case, direction)
                )

        for future in as_completed(futures):
            result = future.result()
            if result != -1:
                return result
    return -1


# **********************
# TESTING and SPEED DEMO
# **********************

if __name__ == "__main__":
    import string
    import random

    # Create 20 million lines of random text
    # --------------------------------------

    def random_words() -> str:
        min_char, max_char = 4, 15
        min_word, max_word = 4, 10
        chars = string.ascii_letters + string.digits + string.punctuation[:10]
        words = [
            "".join(random.sample(chars, random.randint(min_char, max_char)))
            for _ in range(random.randint(min_word, max_word))
        ]
        return " ".join(words)

    lines = [random_words()] * 4 * 5000000  # 20 million lines
    print(f"NOTE: Test list contain {len(lines)} lines of text.")
    lines[-1] = "Who is she anyway? MI6?"
    lines[0] = "LookTheOtherWay343ss"

    # Create Serial Version Tests
    # --------------------

    @timeit_decorator
    def serial_forward_test():
        target = "anyway? MI"
        current_line = 0
        direction = "forward"
        result_forward = find_next_index_with_target_serial(lines, target, current_line, direction)
        print(f"result={result_forward}, correct={result_forward==len(lines)-1}")

    @timeit_decorator
    def serial_backward_test():
        target = "Way343"
        current_line = 20_000_000 - 1
        direction = "backward"
        result_backward = find_next_index_with_target_serial(lines, target, current_line, direction)
        print(f"result={result_backward}, correct={result_backward==0}")

    @timeit_decorator
    def serial_forward_regex_test():
        target = "MI\d\?"
        current_line = 0
        direction = "forward"
        result_regex = find_next_index_with_target_serial(lines, target, current_line, direction, is_regex=True)
        print(f"result={result_regex}, correct={result_regex==len(lines)-1}")

    # Create Parallel Version Tests
    # ----------------------

    @timeit_decorator
    def parallel_forward_test():
        target = "anyway? MI"
        current_line = 0
        direction = "forward"
        result_forward = find_next_index_with_target_parallel_concurrent(lines, target, current_line, direction)
        print(f"result={result_forward}, correct={result_forward==len(lines)-1}")

    @timeit_decorator
    def parallel_backward_test():
        target = "Way343"
        current_line = 20_000_000
        direction = "backward"
        result_backward = find_next_index_with_target_parallel_concurrent(lines, target, current_line, direction)
        print(f"result={result_backward}, correct={result_backward==0}")

    @timeit_decorator
    def parallel_forward_regex_test():
        target = "MI\d\?"
        current_line = 0
        direction = "forward"
        result_regex = find_next_index_with_target_parallel_concurrent(
            lines, target, current_line, direction, is_regex=True
        )
        print(f"result={result_regex}, correct={result_regex==len(lines)-1}")

    # Run Tests
    # ---------

    # serial_forward_test()
    # serial_backward_test()
    # serial_forward_regex_test()

    parallel_forward_test()
    parallel_backward_test()
    parallel_forward_regex_test()

    """
    For example:
    
    NOTE: Test list contain 20000000 lines of text.

    
    # when using ignore_case = True
    # -----------------------------
        
    result=19999999, correct=True
    Function 'serial_forward_test' executed in 9.288053 seconds
    
    result=0, correct=True
    Function 'serial_backward_test' executed in 10.047978 seconds
    
    result=19999999, correct=True
    Function 'serial_forward_regex_test' executed in 10.128728 seconds
    
    # when using ignore_case = False
    # ------------------------------
    
    result=19999999, correct=True
    Function 'serial_forward_test' executed in 2.919134 seconds
    
    result=0, correct=True
    Function 'serial_backward_test' executed in 2.875000 seconds
    
    result=19999999, correct=True
    Function 'serial_forward_regex_test' executed in 2.740468 seconds
    
    # when using ignore_case = True
    # -----------------------------
    
    result=19999999, correct=True
    Function 'parallel_forward_test' executed in 1.547238 seconds
    
    result=0, correct=True
    Function 'parallel_backward_test' executed in 1.577013 seconds
    
    result=19999999, correct=True
    Function 'parallel_forward_regex_test' executed in 1.604368 seconds
    
    # when NOT using ignore_case
    # --------------------------
    
    result=19999999, correct=True
    Function 'parallel_forward_test' executed in 0.833112 seconds
    
    result=0, correct=True
    Function 'parallel_backward_test' executed in 0.763032 seconds
    
    result=19999999, correct=True
    Function 'parallel_forward_regex_test' executed in 0.778173 seconds
    
    """
