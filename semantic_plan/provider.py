"""Explicitly separated synthetic and paid providers; no automatic retries."""
import json
import os
import ssl
from urllib.error import HTTPError,URLError
from urllib.request import Request,build_opener,HTTPRedirectHandler,HTTPSHandler
from .engine import canonical

class FakeProvider:
    synthetic=True
    def __init__(self,confidence=1.0):self.confidence=confidence;self.cache_namespace=f"synthetic-fixture-v1-confidence-{confidence}";self.requests=[]
    def __call__(self,body):
        self.requests.append(body);answers={};columns=body["state"]["columns"];text=str(columns.get("message","")).lower()
        for id,q in body["questions"].items():
            options=q["criteria"]
            if "billing" in options:choice="billing" if any(w in text for w in ("invoice","facture","factura")) else "technical" if any(w in text for w in ("outage","panne","interrupción")) else "other"
            elif "urgent" in options:choice="urgent" if any(w in text for w in ("outage","panne","interrupción")) else "routine"
            elif "priority" in options:choice="priority" if columns.get("customer_tier")=="premium" else "standard"
            else:choice=next(iter(options))
            remainder=(1-self.confidence)/(len(options)-1)
            answers[id]={"type":"choice","choice":choice,"confidence":self.confidence,"probabilities":{k:self.confidence if k==choice else remainder for k in options}}
        return {"model":body["model"],"answers":answers,"usage":{"input_tokens":len(canonical(body))//4,"output_tokens":len(answers)*12}}

class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self,*args,**kwargs):return None

class JevProvider:
    synthetic=False
    cache_namespace="typesafe-api-systemone-v1"
    def __init__(self,api_key=None):
        self.key=api_key or os.environ.get("TYPESAFE_API_KEY")
        if not isinstance(self.key,str) or not self.key:raise ValueError("missing_typesafe_key")
    def __call__(self,body):
        import certifi
        request=Request("https://api.typesafe.ai/v1/systemone",data=json.dumps(body).encode(),headers={"Authorization":"Bearer "+self.key,"Content-Type":"application/json"},method="POST")
        try:
            with build_opener(NoRedirect(),HTTPSHandler(context=ssl.create_default_context(cafile=certifi.where()))).open(request,timeout=30) as response:
                raw=response.read(500001)
                if len(raw)>500000:raise ValueError("provider_size")
                return json.loads(raw)
        except HTTPError as e:raise ValueError("provider_http_"+str(e.code)) from None
        except (URLError,TimeoutError):raise ValueError("provider_transport") from None
