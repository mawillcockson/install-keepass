from threading import Thread
from queue import SimpleQueue
from time import sleep
from sys import exit

def writer(q):
    for i in range(10):
        try:
            q.put(("message", str(i)))
            sleep(0.25)
        except KeyboardInterrupt:
            q.put(("end", "stop"))
            raise

    q.put(("end", "stop"))

def reader(q):
    while True:
        if not q.empty():
            tup = q.get()
            if tup[0] == "message":
                print(tup[1])
            elif tup[0] == "end":
                print("stop")
                break

        sleep(0.01)

if __name__ == "__main__":
    q = SimpleQueue()
    r = Thread(target=reader, kwargs={"q":q})
    w = Thread(target=writer, kwargs={"q":q})
    r.start()
    w.start()
    w.join()
    r.join()
