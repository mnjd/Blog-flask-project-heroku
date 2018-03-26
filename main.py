from rq import Queue
import time
from worker import conn
from apiowm import get_data

q = Queue(connection=conn)
counter = 0
while counter != 4:
    q.enqueue(get_data)
    print('sleeping 5 minutes')
    time.sleep(3600)
    print('awake')
    counter += 1
