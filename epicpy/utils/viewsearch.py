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


def find_next_index_with_target_serial(
    lines, target, start_line, direction="forward", is_regex=False, ignore_case: bool = False
):
    # Compile the pattern based on whether the target is a regex
    if ignore_case:
        pattern = re.compile(target if is_regex else re.escape(target), re.IGNORECASE)
    else:
        pattern = re.compile(target if is_regex else re.escape(target))

    if direction == "forward":
        for i in range(start_line, len(lines)):
            if pattern.search(lines[i]):
                return i
    elif direction == "backward":
        for i in range(start_line, -1, -1):
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
            for i in range(start_line, len(lines), chunk_size if chunk_size else 1):
                chunk_end = min(i + chunk_size, len(lines))
                chunk = lines[i:chunk_end]
                futures.append(executor.submit(find_next_index_in_chunk, chunk, target, i, ignore_case, direction))
        elif direction == "backward":
            for i in range(start_line, -1, -chunk_size if chunk_size else -1):
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
