import unittest
import requests
import time
import os
import shutil
from multiprocessing import Process
from node import run_node

url = 'http://127.0.0.1:5000/'
directory = "databases"
sended_data = dict()
getted_data = dict()
updated_data = dict()

def clear_directory(directory):
    try:
        shutil.rmtree(directory)
    except Exception as e:
        print(e)

def save_to_db():
    for i in range(200):
        requests.put(url+str(i), str(i))
        sended_data[i] = str(i)
    return sended_data

def get_from_db():
    for i in range(200):
        r = requests.get(url+str(i))
        getted_data[i] = r.text
    return getted_data

def update():
    for i in range(200):
        requests.put(url+str(i), str(i+1))
        updated_data[i] = str(i+1)
    return updated_data

def delete_from_db():
    requests.delete(url+'1')
    response = requests.get(url+'1')
    return response.status_code

class TestApiMethods(unittest.TestCase):
    def test_api(self):
        clear_directory(directory)
        node = Process(target=run_node, args=("127.0.0.1", 5000,))
        node.start()
        print("Node running...")
        time.sleep(2)
        
        self.assertEqual(save_to_db(), get_from_db())
        self.assertEqual(update(), get_from_db())
        
        self.assertEqual(delete_from_db(), 404)
        
        node.terminate()
        print("Kill node")
        
if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)