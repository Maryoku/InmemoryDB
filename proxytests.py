import unittest
import requests
import time
import os
import shutil
from multiprocessing import Process
from node import run_node
from proxy import run_proxy

proxy_url = 'http://127.0.0.1:9000/'
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

class TestProxy(unittest.TestCase):
    def test_proxy(self):
        clear_directory(directory)
        proxy = Process(target=run_proxy, args=(9000,))
        node1 = Process(target=run_node, args=("127.0.0.1", 5000,))
        node2 = Process(target=run_node, args=("127.0.0.1", 6000,))
        
        proxy.start()
        print("Proxy running...")
        time.sleep(2)
        
        node1.start()
        print("Node running...")
        time.sleep(4)

        node2.start()
        print("Node running...")
        time.sleep(4)
        
        self.assertEqual(save_to_db(proxy_url), get_from_db(proxy_url))

        node1_count = requests.get('http://127.0.0.1:5000/')
        node2_count = requests.get('http://127.0.0.1:6000/')

        self.assertEqual(node1_count.text, node2_count.text)
    
        node2.terminate()
        node1.terminate()
        proxy.terminate()
        print("KILL ALL")
        
if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)