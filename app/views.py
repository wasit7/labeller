from flask import render_template, jsonify, send_from_directory, send_file, request
from app import app
import os
from collections import defaultdict
import json
import string

@app.route('/')
@app.route('/index')
def index():
    print os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    return render_template("index.html")

@app.route('/tree')
def tree():
    return render_template("treeview.html")

@app.route('/browse', methods = ['POST'])
def browse():
    path = request.form['path']
    print path
    
    if path == '-root-':
        data = []
        base_path = os.path.abspath('./')
        data.append({'name': base_path, 'type': 'folder', 'additionalParameters': {'path': base_path, 'children': True}})
        drives = [c+':\\' for c in string.uppercase if os.path.isdir(c+':\\')]
        if len(drives) > 0:
            for drive in drives:
                data.append({'name': drive, 'type': 'folder', 'additionalParameters': {'path': drive, 'children': True}})
        else:
            data.append({'name': '/', 'type': 'folder', 'additionalParameters': {'path': '/', 'children': True}})
        return jsonify(status='OK', data=data)
    else:
        data = []
        for root, dirs, files in os.walk(path):
            for name in sorted(dirs):
                data.append({'name': name, 'type': 'folder', 'additionalParameters': {'path': os.path.join(root, name), 'children': True}})
#             for name in sorted(files):
#                 data.append({'name': "<i class='ace_icon fa fa-picture-o green'></i> "+name, 'type': 'item', 'additionalParameters': {'path': os.path.join(root, name), 'children': False}})
            break
        return jsonify(status='OK', data=data)

@app.route('/info', methods = ['POST'])
def info():
    image_base = request.form['image_base']
    print image_base
    try:
        image_base = os.path.relpath(request.form['image_base'])
    except:
        image_base = request.form['image_base']
    print image_base
    order = []
    children = defaultdict(list)

    for root, dirs, files in os.walk(image_base, topdown=False):
        for name in sorted(dirs):
            children[root].append({'name': name, 'type': 'folder', 'path': os.path.join(root, name), 'additionalParameters': {'children': children[os.path.join(root, name)]}})
        for name in sorted(files):
            if name.endswith('.jpg') or name.endswith('.jpeg') or name.endswith('.JPG') or name.endswith('.JPEG'):
                order.append(os.path.join(root, name))
                children[root].append({'name': "<i class='ace_icon fa fa-picture-o green'></i> "+name, 'type': 'item', 'path': os.path.join(root, name)})

    tree = {
        '[Base]':{
            'name': '[Base]',
            'type': 'folder',
            'additionalParameters': {
                'children': children[image_base]
            }
        }
    }

    print json.dumps(tree)
    print request.get_json()
    return jsonify(files=tree, order=order, base_path=image_base)

@app.route('/images/<path:filename>')
def image(filename):
    if filename.startswith('_root_'):
        filename = filename.replace('_root_', '/')
        print filename
    else:
        filename = filename.replace('_parent_', '..')
        print filename
        filename = os.path.abspath(filename)
        print filename
    return send_file(filename)

@app.route('/record/<path:filename>', methods = ['POST'])
def record(filename):
    req_id = request.form['req_id']
    if filename.startswith('_root_'):
        filename = filename.replace('_root_', '/')
    else:
        filename = filename.replace('_parent_', '..')
    filename = filename + '.json'
    try:
        rec = json.loads(open(filename, 'r').read())
    except:
        rec = None
    return jsonify(status='OK', record=rec, req_id=req_id)

@app.route('/submit', methods=['POST'])
def submit():
    req = request.get_json()
    print req
    filename = req['path'] + '.json'
    print filename
    print 'abs', os.path.abspath(filename)
    
    req['path'] = req['path'].replace('\\', '/')
    
    with open(filename, 'w') as output:
        output.write(json.dumps(req, indent=2))
    return jsonify(status='OK')
