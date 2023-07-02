from flask import Flask,request
app = Flask(__name__)

import json

from flask_cors import CORS

# from algorithm.Hyperedge import Hypergraph

# hyper=Hypergraph(threshold=0.5)
cors = CORS(app, supports_credentials=True)

@app.route('/')
def hello_world():
   return 'Hello World'

@app.route('/datainput',methods=['POST'])
def solve_hypedge():
    obj = request.files.get('file')
    file_name=obj.filename
    print(file_name)
    obj.save(str(file_name))
    # hyperedge_dimension=request.form['d']
    return  json.dumps(1)



if __name__ == '__main__':
   app.run(debug=True,host='0.0.0.0')