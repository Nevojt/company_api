<<<<<<< HEAD
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)
=======
# from fastapi.testclient import TestClient
# from app.main import app

# client = TestClient(app)
>>>>>>> b76081a8ec4b9a820a3d0f1adef71c7e7cef6824

# def test_home():
#     response = client.get("/", allow_redirects=False)
#     assert response.status_code == 307
    
<<<<<<< HEAD
def test_reset():
    response = client.get("/reset")
    assert response.status_code == 200

def test_success_page():
    response = client.get("/success-page")
    assert response.status_code == 200

def test_privacy_policy():
    response = client.get("/privacy-policy", allow_redirects=False)
    assert response.status_code == 307


def test_contact_form():
    response = client.get("/contact-form")
    assert response.status_code == 200
=======
# def test_reset():
#     response = client.get("/reset")
#     assert response.status_code == 200

# def test_success_page():
#     response = client.get("/success-page")
#     assert response.status_code == 200

# def test_privacy_policy():
#     response = client.get("/privacy-policy", allow_redirects=False)
#     assert response.status_code == 307


# def test_contact_form():
#     response = client.get("/contact-form")
#     assert response.status_code == 200
>>>>>>> b76081a8ec4b9a820a3d0f1adef71c7e7cef6824
