import pytest
import os.path
from gofi import objects


@pytest.fixture
def application_object():
    class Application(object):
        def __init__(self, name):
            self.app_id = "org.test.app.desktop"
            self.app_name = name
            self.display_name = name
            self.search_string = name.lower()
            self.popularity = 0
            self.last_use = 0
            self.visibility = 2

    return Application("Test application")


@pytest.fixture(scope="session")
def home_dir(tmp_path_factory):
    fn = tmp_path_factory.mktemp("gofi")
    return fn


def test_save_history(home_dir, application_object):
    history = objects.History(home_dir)
    history.update(application_object)
    assert history.entries["org.test.app.desktop"][0] == 1
    assert os.path.isfile(history.filename)


def test_load_history(home_dir, application_object):
    history = objects.History(home_dir)
    assert history.entries["org.test.app.desktop"][0] == 1
