import unittest
import requests
import time
import os
import shutil
from multiprocessing import Process
from node import run_node

master_url = 'http://127.0.0.1:5000/'
slave1_url = 'http://127.0.0.2:5000/'
slave2_url = 'http://127.0.0.3:5000/'
directory = "databases"
sended_data = dict()
getted_data = dict()
updated_data = dict()

def clear_directory(directory):
    try:
        shutil.rmtree(directory)
    except Exception as e:
        print(e)

def save_to_db(url):
    for i in range(200):
        requests.put(url+str(i), str(i))
        sended_data[i] = str(i)
    return sended_data

def get_from_db(url):
    for i in range(200):
        r = requests.get(url+str(i))
        getted_data[i] = r.text
    return getted_data

def delete_from_db(url):
    requests.delete(url+'1')
    response = requests.get(url+'1')
    return response.status_code

class TestReplication(unittest.TestCase):
    def test_work(self):
        clear_directory(directory)
        
        slave1 = Process(target=run_node, args=("127.0.0.2", 5000,))
        slave2 = Process(target=run_node, args=("127.0.0.3", 5000,))
        master = Process(target=run_node, args=("127.0.0.1", 5000, ["127.0.0.2:5000/", "127.0.0.3:5000/"]))
        
        slave1.start()
        print("Slave1 running...")
        time.sleep(4)
        
        slave2.start()
        print("Slave2 running...")
        time.sleep(4)
        
        master.start()
        print("Master running...")
        time.sleep(4)
        
        save_to_db(master_url)
        self.assertEqual(get_from_db(master_url), get_from_db(slave1_url))
        self.assertEqual(get_from_db(master_url), get_from_db(slave2_url))
        self.assertEqual(get_from_db(slave1_url), get_from_db(slave2_url))
        
        slave1.terminate()
        slave2.terminate()
        master.terminate()
        print("KILL ALL")
        
if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)