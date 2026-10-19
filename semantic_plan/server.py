import copy
import json
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
import tempfile
from urllib.parse import urlparse
from .__main__ import ROOT,example
from .engine import compile_plan,execute,query_results
from .provider import FakeProvider

SQL="SELECT row_id, choice, confidence FROM decisions WHERE node_id='route' AND status='decided' ORDER BY row_id"
def comparison(lang='en',mode='cold',max_calls=20):
    if lang not in ('fr','en','es') or mode not in ('cold','warm','changed','policy','review'):raise ValueError('mode')
    data=example(lang);baseline=execute(data['plan'],data['rows'],FakeProvider(),optimize=False)
    with tempfile.TemporaryDirectory() as temp:
        path=str(Path(temp)/'run.sqlite');cold=execute(data['plan'],data['rows'],FakeProvider(),cache_path=path)
        if mode=='cold':selected=cold
        else:
            if mode=='changed':data['rows'][0]['message']+=' [B]'
            if mode=='policy':data['plan']['policy_version']='demo-2'
            selected=execute(data['plan'],data['rows'],FakeProvider(.6) if mode=='review' else FakeProvider(),cache_path=path,max_calls=max_calls)
        sql=SQL.replace("WHERE node_id",f"WHERE run_id='{selected['run_id']}' AND node_id")
        selected_rows=query_results(path,sql)
    return {'mode':mode,'synthetic':True,'source_case':data,'compiled':compile_plan(data['plan']),'baseline':baseline,'cold':cold,'selected':selected,'sql':sql,'sql_rows':selected_rows}

class Handler(BaseHTTPRequestHandler):
    def log_message(self,*_):pass
    def reply(self,code,data,kind='application/json'):
        content=data if isinstance(data,bytes) else json.dumps(data).encode();self.send_response(code);self.send_header('Content-Type',kind+'; charset=utf-8');self.send_header('Content-Length',str(len(content)));self.send_header('Cache-Control','no-store');self.send_header('X-Content-Type-Options','nosniff');self.end_headers();self.wfile.write(content)
    def do_GET(self):
        path=urlparse(self.path).path
        if path in ('/','/app.js','/style.css'):
            file='index.html' if path=='/' else path[1:];return self.reply(200,(ROOT/'web'/file).read_bytes(),{'index.html':'text/html','app.js':'text/javascript','style.css':'text/css'}[file])
        self.reply(404,{'error':'not_found'})
    def do_POST(self):
        if self.path!='/api/compare':return self.reply(404,{'error':'not_found'})
        if self.headers.get('Origin') not in (None,f'http://127.0.0.1:{self.server.server_port}'):return self.reply(403,{'error':'origin_denied'})
        try:
            size=int(self.headers.get('Content-Length','0'))
            if not 0<size<=10000:raise ValueError('size')
            body=json.loads(self.rfile.read(size));self.reply(200,comparison(body.get('lang','en'),body.get('mode','cold')))
        except (ValueError,TypeError,KeyError):self.reply(400,{'error':'invalid_input','messages':['Entrée non valide','Invalid input','Entrada no válida']})
def serve(port=8774):ThreadingHTTPServer(('127.0.0.1',port),Handler).serve_forever()
