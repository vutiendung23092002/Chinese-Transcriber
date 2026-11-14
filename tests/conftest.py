import os
os.environ.setdefault('CHINESE_TRANSCRIBER_NO_PROBE','1')
import pytest
from chinese_transcriber.theme import load_fonts

@pytest.fixture(autouse=True)
def fonts_for_qt(request):
    if 'qtbot' in request.fixturenames:
        application=request.getfixturevalue('qapp'); load_fonts(application)
