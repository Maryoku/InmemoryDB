from flask import Flask, request, abort
import requests
import json

#TO DO: resharding

app = Flask(__name__)
nodes = list()

@app.route('/', methods=['POST'])
def register_node():
    new_node = request.data.decode('utf-8')
    nodes.append(new_node)
    resharding(new_node)
    return "OK"

@app.route('/<int:id_record>', methods=['GET', 'PUT', 'DELETE'])
def sharding(id_record):
    node_num = shard_func(id_record)
    if request.method == 'GET':
        record = requests.get(nodes[node_num]+str(id_record))
        return record.text
    elif request.method == 'PUT':
        record = requests.put(nodes[node_num]+str(id_record), str(id_record))
        return record.text
    elif request.method == 'DELETE':
        record = requests.delete(nodes[node_num]+str(id_record))
        return record.text

def shard_func(id_record):
    node_num = id_record % len(nodes)
    return node_num

def resharding(new_node):
    for node in nodes:
        if not node == new_node:
            data = str(nodes.index(new_node))+","+str(len(nodes))
            requests.post(node, data=data)
            print("I'm asking")

def run_proxy(port):
    app.run(port=port, threaded=True)

if __name__ == '__main__':
    run_proxy(9000)