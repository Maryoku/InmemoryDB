from flask import Flask, request, abort
import requests
import json
import os
import asyncio

proxy = 'http://127.0.0.1:9000/'
inmemory_db = dict()
storage = "db.json"
db_path = "databases"
replication_model = "sync"
slaves = list()

app = Flask(__name__)

def create_storage(ip, port):
    dir = ip+":"+str(port)
    path = os.path.join(db_path, dir)
    if not os.path.exists(path):
        os.makedirs(path)
    global storage_path
    storage_path = os.path.join(path, storage)
    if not os.path.isfile(storage_path):
        file = open(storage_path, 'w')
        file.close()
        print("Storage created")
    else:
        file = open(storage_path)
        global inmemory_db
        inmemory_db = json.loads(file.read())
        print("Restore data")

def connect_to_proxy(port):
    try:
        url = 'http://127.0.0.1:'+str(port)+'/'
        requests.post(proxy, data=url)
        return print("I'm register")
    except requests.RequestException:
        return print("Proxy is DEAD")

def set_slaves(slaves_list: list):
    global slaves
    slaves = slaves_list
    print("I'm register slaves: ", slaves)
    
async def writer(db):
    with open(storage_path, "w") as storage:
        json.dump(db, storage)      
        
async def async_replication(method, record_id, data=None):
    if method == "put":
        for slave_node in slaves:
            requests.put("http://"+slave_node+str(record_id), data)
    if method == "delete":
        for slave_node in slaves:
            requests.delete("http://"+slave_node+str(record_id))
            
def sync_replication(method, record_id, data=None):
    if method == "put":
        for slave_node in slaves:
            requests.put("http://"+slave_node+str(record_id), data)
    if method == "delete":
        for slave_node in slaves:
            requests.delete("http://"+slave_node+str(record_id))
        
@app.route('/', methods=['GET'])
def get_counts():
    count = len(inmemory_db)
    return str(count)

@app.route('/', methods=['POST'])
def get_shard():
    data = request.data.decode('utf-8')
    new_node = request.host
    node_num, nodes_count = data.split(",")
    temp_dict = inmemory_db
    for key in temp_dict.keys():
        if int(key) % int(nodes_count) == int(node_num):
            requests.put("http://"+str(new_node)+"/", temp_dict[key])
            delete_record(str(key))
    return "Shard register"

@app.route('/<int:record_id>', methods=['GET'])
def get_record(record_id):
    if record_id in inmemory_db:
        return inmemory_db[record_id]
    else:
        abort(404)

@app.route('/<int:record_id>', methods=['PUT'])
def update_record(record_id):
    data = request.data.decode('utf-8')
    inmemory_db[record_id] = data
    asyncio.run(writer(inmemory_db))
    
    method = "put"
    if replication_model == "sync":
        sync_replication(method, record_id, data)
    if replication_model == "async":
        asyncio.run(async_replication(method, record_id, data))
    
    return inmemory_db[record_id]

@app.route('/<int:record_id>', methods=['DELETE'])
def delete_record(record_id):
    if record_id in inmemory_db:
        inmemory_db.pop(record_id)
        asyncio.run(writer(inmemory_db))
        
        method = "delete"
        if replication_model == "sync":
            sync_replication(method, record_id)
        if replication_model == "async":
            asyncio.run(async_replication(method, record_id))
        
        return "Record successful deleted"
    else:
        abort(404)

def run_node(ip, port, slaves=None):
    create_storage(ip, port)
    connect_to_proxy(port)
    if slaves is not None:
        set_slaves(slaves)
    app.run(host=ip, port=port, threaded=True)

if __name__ == '__main__':
    run_node("127.0.0.1", 5000)
    #run_node("127.0.0.1", 5000, ["http://127.0.0.2:5000/", "http://127.0.0.3:5000/"])