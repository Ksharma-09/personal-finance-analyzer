from streamlit.testing.v1 import AppTest


def test_streamlit_app_runs_without_exception():
    app = AppTest.from_file("kanchan2.py").run()
    assert not app.exception
    assert any("Personal Finance Analyzer" in str(item.value) for item in app.title)
