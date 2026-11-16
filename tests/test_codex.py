import json
import pytest
from chinese_transcriber.codex import validate_result,validate_selection

def test_ids_are_validated_before_persisting():
    source=[dict(id='a',zh='你好'),dict(id='b',zh='谢谢')]
    valid=dict(segments=[dict(id='b',vi='Cảm ơn',note=''),dict(id='a',vi='Xin chào',note='')])
    assert [x['id'] for x in validate_result(valid,source)]==['a','b']
    for items in [[dict(id='a',vi='x',note='')]*2,[dict(id='wrong',vi='x',note='')],[]]:
        with pytest.raises(ValueError): validate_result(dict(segments=items),source)

def test_never_substitutes_an_unavailable_model_or_effort():
    models=[dict(model='available',supportedReasoningEfforts=[dict(reasoningEffort='low')])]
    with pytest.raises(ValueError): validate_selection(models,'other','low')
    with pytest.raises(ValueError): validate_selection(models,'available','high')


def test_whole_transcript_is_one_structured_turn_with_all_ids(monkeypatch,tmp_path):
    from chinese_transcriber import codex
    source=[dict(id=str(i),zh=f'句子{i}') for i in range(14)]
    result=[dict(id=row['id'],vi='Bản dịch',note='') for row in reversed(source)]
    calls=[]; waits=[]
    class Rpc:
        def __init__(self,*args): pass
        def __enter__(self): return self
        def __exit__(self,*args): pass
        def call(self,method,params,**kwargs):
            calls.append((method,params)); return {'thread':{'id':'one-thread'}} if method=='thread/start' else {}
        def next(self,timeout):
            waits.append(timeout)
            return dict(method='turn/completed',params=dict(turn=dict(status='completed',items=[dict(type='agentMessage',text=json.dumps(dict(segments=result)))])))
    monkeypatch.setattr(codex,'Rpc',Rpc)
    output=codex.translate_segments('test.exe',tmp_path,[dict(model='test',supportedReasoningEfforts=[dict(reasoningEffort='low')])],
        'test','low','lecture',[dict(zh='句子',vi='câu')],source,timeout=900)
    assert [method for method,_ in calls]==['thread/start','turn/start']
    prompt=json.loads(calls[1][1]['input'][0]['text'])
    assert prompt['segments']==source and prompt['context']=='lecture' and len(output)==14
    assert [item['id'] for item in output]==[row['id'] for row in source]
    assert waits[0]>180
