import time
import asyncio
import random
import threading

def DoltThread(str):
    cnt = 0
    while (cnt < 10):
        time.sleep(random.randint(0, 100)/300.0)
        print(str, cnt)
        cnt += 1
    print("=== ", str, " Exit Thread ===")

th_a = threading.Thread(target=DoltThread, args=("Mike",))
th_b = threading.Thread(target=DoltThread, args=("Jake",))
th_c = threading.Thread(target=DoltThread, args=("Jake",))

print("=== Start Thread ===")
th_a.start()
th_b.start()

th_a.join()
th_b.join()
print("Test finished")