import random
import time
from multiprocessing import Process, Value, Lock

# ------------------------
# Configuration for Puzzle 1
# ------------------------
LOWER_BOUND = 0x0
UPPER_BOUND = 0xFFFFFFFF
PUZZLE_1_KEY = 0x87654321  # Replace this with the actual Puzzle 1 solution

NUM_WORKERS = 4
STATUS_INTERVAL = 1.0  # seconds

# ------------------------
# Worker function
# ------------------------
def worker(worker_id, checked_count, stop_flag, lock):
    random.seed(time.time() + worker_id)

    while not stop_flag.value:
        key = random.randint(LOWER_BOUND, UPPER_BOUND)
        with lock:
            checked_count.value += 1

        if key == PUZZLE_1_KEY:
            with lock:
                stop_flag.value = True
            print(f"\n🔥 Worker {worker_id} FOUND KEY: {hex(key)}")
            with open("FOUND_KEY.txt", "w") as f:
                f.write(hex(key))
            break

# ------------------------
# Status printer
# ------------------------
def status_printer(checked_count, stop_flag, lock):
    last_checked = 0
    while not stop_flag.value:
        time.sleep(STATUS_INTERVAL)
        with lock:
            total = checked_count.value
        speed = total - last_checked
        last_checked = total
        percent_complete = ((total - LOWER_BOUND) / (UPPER_BOUND - LOWER_BOUND)) * 100
        print(f"[+] Checked: {total} | Speed: {speed/STATUS_INTERVAL:.0f}/sec | % Complete: {percent_complete:.6f}%")

# ------------------------
# Main
# ------------------------
if __name__ == "__main__":
    print("🚀 Starting Puzzle 1 test solver...")

    lock = Lock()
    checked_count = Value('Q', 0)
    stop_flag = Value('b', False)

    # Start workers
    workers = []
    for i in range(NUM_WORKERS):
        p = Process(target=worker, args=(i, checked_count, stop_flag, lock))
        p.start()
        workers.append(p)
        print(f"✅ Worker {i} started")

    # Start status printer
    status = Process(target=status_printer, args=(checked_count, stop_flag, lock))
    status.start()

    # Wait for workers to finish
    for p in workers:
        p.join()

    # Stop status printer
    status.terminate()

    print("\n✅ Finished")
    print(f"Total checked: {checked_count.value}")
    if stop_flag.value:
        print("Key was found and saved to FOUND_KEY.txt")
    else:
        print("Key was not found")
