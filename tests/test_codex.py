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
