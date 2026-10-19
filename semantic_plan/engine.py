"""DAG validation, projected-input CSE, batching, durable cache and SQL lineage."""
import hashlib
import json
import math
import re
import sqlite3
import uuid

def canonical(value):return json.dumps(value,sort_keys=True,separators=(",",":"),ensure_ascii=False,allow_nan=False)
def digest(value):return hashlib.sha256(canonical(value).encode()).hexdigest()

def compile_plan(plan):
    if not isinstance(plan,dict) or not isinstance(plan.get("policy_version"),str) or not plan["policy_version"] or plan.get("model")!="jev-1.13.0" or not isinstance(plan.get("nodes"),list) or not 1<=len(plan["nodes"])<=16:raise ValueError("invalid_plan")
    if set(plan)-{"model","policy_version","nodes"}:raise ValueError("unknown_plan_field")
    nodes={}
    for node in plan["nodes"]:
        if not isinstance(node,dict) or not isinstance(node.get("id"),str) or not re.fullmatch(r"[a-z][a-z0-9_]{0,40}",node["id"]) or node["id"] in nodes:raise ValueError("invalid_node_id")
        if node.get("kind") not in ("choice","subtract") or not isinstance(node.get("reads"),list) or not 1<=len(node["reads"])<=12 or any(not isinstance(c,str) or not c for c in node["reads"]) or len(set(node["reads"]))!=len(node["reads"]):raise ValueError("invalid_reads")
        allowed={"id","kind","reads","depends","when"}|({"instructions","criteria"} if node["kind"]=="choice" else set())
        if set(node)-allowed:raise ValueError("unknown_node_field")
        dependencies=node.get("depends",[])
        if not isinstance(dependencies,list) or any(not isinstance(x,str) for x in dependencies) or len(dependencies)!=len(set(dependencies)):raise ValueError("invalid_dependencies")
        if node["kind"]=="choice":
            criteria=node.get("criteria")
            if not isinstance(node.get("instructions"),str) or not 1<=len(node["instructions"])<=6000 or not isinstance(criteria,dict) or not 2<=len(criteria)<=20 or any(not isinstance(k,str) or not k or not isinstance(v,str) or not v for k,v in criteria.items()):raise ValueError("invalid_choice_contract")
        elif len(node["reads"])!=2:raise ValueError("subtract_requires_two_columns")
        when=node.get("when")
        if when is not None:
            if not isinstance(when,dict) or set(when)!={"node","equals"} or not isinstance(when["node"],str):raise ValueError("invalid_condition")
            dependencies=list(set(dependencies)|{when["node"]})
        nodes[node["id"]]={**node,"depends":sorted(dependencies)}
    for node in nodes.values():
        if any(d not in nodes for d in node["depends"]):raise ValueError("missing_dependency")
        if node.get("when"):
            parent=nodes[node["when"]["node"]]
            if parent["kind"]!="choice" or node["when"]["equals"] not in parent["criteria"]:raise ValueError("invalid_condition_choice")
    layers=[];done=set()
    while len(done)<len(nodes):
        layer=[n for n in nodes.values() if n["id"] not in done and set(n["depends"])<=done]
        if not layer:raise ValueError("dependency_cycle")
        layers.append(layer);done.update(n["id"] for n in layer)
    return {"model":plan["model"],"policy_version":plan["policy_version"],"nodes":nodes,"layers":layers,"plan_sha256":digest(plan),"exact_cache_reuse_requires_same_model_policy_question_and_projected_state":True}

def validate_rows(rows,compiled):
    if not isinstance(rows,list) or not 1<=len(rows)<=200 or any(not isinstance(r,dict) or not isinstance(r.get("id"),str) or not r["id"] for r in rows) or len({r["id"] for r in rows})!=len(rows):raise ValueError("invalid_rows")
    for row in rows:
        canonical(row)
        for node in compiled["nodes"].values():
            if any(col not in row for col in node["reads"]):raise ValueError("missing_input_column")
            if node["kind"]=="subtract" and any(type(row[col])is not int for col in node["reads"]):raise ValueError("exact_integer_required")

def validated_answers(questions,response,model):
    if not isinstance(response,dict) or response.get("model")!=model or not isinstance(response.get("answers"),dict) or set(response["answers"])!=set(questions):raise ValueError("invalid_response_questions")
    answers={}
    for id,q in questions.items():
        a=response["answers"][id]
        if not isinstance(a,dict):raise ValueError("invalid_answer")
        probabilities=a.get("probabilities");confidence=a.get("confidence")
        if a.get("type")!="choice" or a.get("choice") not in q["criteria"] or not isinstance(probabilities,dict) or set(probabilities)!=set(q["criteria"]) or any(type(p) not in (int,float) or not math.isfinite(p) or not 0<=p<=1 for p in probabilities.values()) or abs(sum(probabilities.values())-1)>.001 or type(confidence) not in (int,float) or not math.isfinite(confidence) or not 0<=confidence<=1 or probabilities[a["choice"]]+1e-6<max(probabilities.values()):raise ValueError("invalid_choice_answer")
        answers[id]={k:a[k] for k in ("type","choice","confidence","probabilities")}
    usage=response.get("usage",{})
    if any(type(usage.get(k))is not int or usage[k]<0 for k in ("input_tokens","output_tokens")):raise ValueError("invalid_usage")
    return answers,{k:usage[k] for k in ("input_tokens","output_tokens")}

def database(path):
    db=sqlite3.connect(path)
    db.executescript('''CREATE TABLE IF NOT EXISTS cache(key TEXT PRIMARY KEY, model TEXT NOT NULL, answer TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS runs(id TEXT PRIMARY KEY, plan_sha256 TEXT NOT NULL, policy_version TEXT NOT NULL, report TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS decisions(run_id TEXT NOT NULL, row_id TEXT NOT NULL, node_id TEXT NOT NULL, status TEXT NOT NULL, choice TEXT, confidence REAL, exact_value TEXT, cache_key TEXT, PRIMARY KEY(run_id,row_id,node_id));
    CREATE INDEX IF NOT EXISTS decision_status ON decisions(run_id,status,choice);''')
    return db

def execute(plan,rows,provider,cache_path=":memory:",max_calls=20,max_questions=100,min_confidence=.8,max_context_chars=18000,optimize=True):
    compiled=compile_plan(plan);validate_rows(rows,compiled)
    namespace=getattr(provider,"cache_namespace",None)
    if not isinstance(namespace,str) or not namespace or type(getattr(provider,"synthetic",None))is not bool:raise ValueError("explicit_provider_namespace_required")
    if type(optimize)is not bool:raise ValueError("invalid_optimization_mode")
    if type(max_calls)is not int or not 0<=max_calls<=100 or type(max_questions)is not int or not 0<=max_questions<=1000 or type(min_confidence) not in (int,float) or not math.isfinite(min_confidence) or not 0<=min_confidence<=1 or type(max_context_chars)is not int or not 100<=max_context_chars<=50000:raise ValueError("invalid_budget")
    db=database(cache_path);run_id=uuid.uuid4().hex;outputs={r["id"]:{} for r in rows};trace=[];usage={"input_tokens":0,"output_tokens":0};calls=questions_sent=cache_hits=dedup_reuse=0
    def store(node,row,answer,key,origin,question_id):
        status="review" if answer["choice"] in ("unknown","uncertain") or answer["confidence"]<min_confidence else "decided"
        outputs[row["id"]][node["id"]]={"status":status,**answer,"cache_key":key,"question_id":question_id,"origin":origin}
    try:
        for layer in compiled["layers"]:
            pending={}
            for node in layer:
                for row in rows:
                    out=outputs[row["id"]];deps={d:out[d] for d in node["depends"]}
                    if any(v["status"] not in ("decided","exact") for v in deps.values()):out[node["id"]]={"status":"blocked_review"};continue
                    if node.get("when") and deps[node["when"]["node"]]["choice"]!=node["when"]["equals"]:out[node["id"]]={"status":"skipped"};continue
                    if node["kind"]=="subtract":out[node["id"]]={"status":"exact","value":row[node["reads"][0]]-row[node["reads"][1]]};continue
                    state={"columns":{c:row[c] for c in sorted(node["reads"])},"decisions":{k:{"choice":v["choice"]} if v["status"]=="decided" else {"value":v["value"]} for k,v in sorted(deps.items())}}
                    question={"type":"choice","instructions":node["instructions"],"criteria":node["criteria"]};key=digest({"model":compiled["model"],"policy_version":compiled["policy_version"],"state":state,"question":question})
                    if not optimize:key=digest({"key":key,"row":row["id"],"node":node["id"]})
                    if key not in pending:pending[key]={"state":state,"question":question,"members":[]}
                    pending[key]["members"].append((node,row))
            groups={}
            for key,item in pending.items():groups.setdefault(canonical(item["state"])+(":"+key if not optimize else ""),[]).append((key,item))
            for context,items in groups.items():
                items=sorted(items,key=lambda pair:pair[0])
                body={"model":compiled["model"],"state":items[0][1]["state"],"questions":{f"q{i}":item["question"] for i,(_,item) in enumerate(items)}}
                request_key=digest({"provider_namespace":namespace,"policy_version":compiled["policy_version"],"request":body})
                cached=db.execute("SELECT answer FROM cache WHERE key=? AND model=?",(request_key,compiled["model"])).fetchone() if optimize else None
                if cached:
                    try:answers,_=validated_answers(body["questions"],{"model":compiled["model"],"answers":json.loads(cached[0]),"usage":{"input_tokens":0,"output_tokens":0}},compiled["model"])
                    except (ValueError,TypeError,KeyError):db.execute("DELETE FROM cache WHERE key=?",(request_key,))
                    else:
                        for i,(_,item) in enumerate(items):
                            for node,row in item["members"]:store(node,row,answers[f"q{i}"],request_key,"persistent_cache",f"q{i}");cache_hits+=1
                        continue
                reason=None
                if len(canonical(body))>max_context_chars:reason="context_budget"
                elif calls>=max_calls or questions_sent+len(items)>max_questions:reason="budget_exhausted"
                if reason:
                    for _,item in items:
                        for node,row in item["members"]:outputs[row["id"]][node["id"]]={"status":reason}
                    trace.append({"status":reason,"questions":len(items)});continue
                calls+=1;questions_sent+=len(items)
                try:answers,spent=validated_answers(body["questions"],provider(body),compiled["model"])
                except Exception:
                    # Provider errors never echo response bodies, keys or user text.
                    for _,item in items:
                        for node,row in item["members"]:outputs[row["id"]][node["id"]]={"status":"provider_error"}
                    trace.append({"status":"provider_error","questions":len(items)});continue
                for k in usage:usage[k]+=spent[k]
                if optimize:db.execute("INSERT OR REPLACE INTO cache VALUES(?,?,?)",(request_key,compiled["model"],canonical(answers)))
                for i,(key,item) in enumerate(items):
                    a=answers[f"q{i}"]
                    dedup_reuse+=len(item["members"])-1
                    for node,row in item["members"]:store(node,row,a,request_key,"provider_shared" if len(item["members"])>1 else "provider",f"q{i}")
                trace.append({"status":"provider_completed","request_key":request_key,"question_keys":[k for k,_ in items],"question_count":len(items),"projected_state":body["state"],"questions":body["questions"],"usage":spent})
            db.commit()
        statuses=[v["status"] for row in outputs.values() for v in row.values()]
        report={"run_id":run_id,"plan_sha256":compiled["plan_sha256"],"policy_version":compiled["policy_version"],"provider_namespace":namespace,"model":compiled["model"],"status":"completed" if all(s in ("decided","exact","skipped") for s in statuses) else "needs_review","rows":outputs,"provider_calls":calls,"questions_sent":questions_sent,"persistent_cache_hits":cache_hits,"deduplicated_logical_cells":dedup_reuse,"naive_question_upper_bound":len(rows)*sum(n["kind"]=="choice" for n in compiled["nodes"].values()),"usage":usage,"usage_complete":not any(t["status"]=="provider_error" for t in trace),"usage_is_synthetic":provider.synthetic,"trace":trace,"threshold_uncalibrated":min_confidence,"independent_stochastic_samples_preserved":False}
        report.update(optimization_enabled=optimize,input_sha256=digest(rows))
        for row_id,nodes in outputs.items():
            for node_id,v in nodes.items():db.execute("INSERT INTO decisions VALUES(?,?,?,?,?,?,?,?)",(run_id,row_id,node_id,v["status"],v.get("choice"),v.get("confidence"),str(v["value"]) if "value" in v else None,v.get("cache_key")))
        db.execute("INSERT INTO runs VALUES(?,?,?,?)",(run_id,compiled["plan_sha256"],compiled["policy_version"],canonical(report)));db.commit();return report
    finally:db.close()

def query_results(path,sql):
    if not isinstance(sql,str) or len(sql)>10000:raise ValueError("sql_size_budget")
    db=sqlite3.connect(f"file:{path}?mode=ro",uri=True)
    try:
        def authorize(action,arg1,arg2,*_):
            if action==sqlite3.SQLITE_FUNCTION:return sqlite3.SQLITE_OK if arg2 in ("count","sum","min","max","avg","json_extract","length","coalesce","lower","upper") else sqlite3.SQLITE_DENY
            return sqlite3.SQLITE_OK if action in (sqlite3.SQLITE_SELECT,sqlite3.SQLITE_READ,sqlite3.SQLITE_RECURSIVE) else sqlite3.SQLITE_DENY
        db.set_authorizer(authorize)
        db.set_progress_handler(lambda:1,100000)
        cursor=db.execute(sql);names=[d[0] for d in cursor.description];rows=cursor.fetchmany(1001)
        if len(rows)>1000:raise ValueError("sql_result_budget")
        return [dict(zip(names,row)) for row in rows]
    finally:db.close()
