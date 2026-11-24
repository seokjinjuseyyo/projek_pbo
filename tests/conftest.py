import pytest
from pathlib import Path
from clinic import create_app, db
from seed import seed_data


@pytest.fixture
def app(tmp_path):
    app=create_app({'TESTING':True,'WTF_CSRF_ENABLED':False,'SECRET_KEY':'test-only',
        'SQLALCHEMY_DATABASE_URI':'sqlite:///'+str(tmp_path/'test.db')})
    app.instance_path=str(tmp_path/'instance')
    Path(app.instance_path).mkdir(exist_ok=True)
    with app.app_context():
        seed_data(demo=False)
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app): return app.test_client()
