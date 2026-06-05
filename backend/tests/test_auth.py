import pytest
import json
from unittest.mock import patch
from models import User

def test_login_success(client, seed_data):
    # 1. Post valid credentials
    response = client.post('/api/v1/auth/login', json={
        'email': 'admin@test.com',
        'password': 'AdminPassword123!'
    })
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data.get('status') == 'success'
    assert data.get('role') == 'admin'

def test_login_invalid_credentials(client, seed_data):
    # 2. Post incorrect password
    response = client.post('/api/v1/auth/login', json={
        'email': 'admin@test.com',
        'password': 'WrongPassword'
    })
    
    assert response.status_code == 401
    data = json.loads(response.data)
    assert data.get('status') == 'error'
    assert "Invalid email or password" in data.get('message')

def test_logout(client, seed_data):
    # Login first
    client.post('/api/v1/auth/login', json={
        'email': 'admin@test.com',
        'password': 'AdminPassword123!'
    })
    
    # Logout
    response = client.post('/api/v1/auth/logout')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data.get('status') == 'success'
    assert "Logged out" in data.get('message')

@patch('services.auth_service.mail.send')
def test_forgot_password_and_reset_flow(mock_send_mail, client, seed_data, app):
    # Request reset token
    response = client.post('/api/v1/auth/reset_password', json={
        'email': 'patient@test.com'
    })
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data.get('status') == 'success'
    assert mock_send_mail.called
    
    # Extract token from user object in DB context
    with app.app_context():
        user = User.query.filter_by(email='patient@test.com').first()
        token = user.get_reset_token()
        
    # Reset password with weak password (should fail)
    response_reset_fail = client.post(f'/api/v1/auth/reset_password/{token}', json={
        'password': 'weak'
    })
    assert response_reset_fail.status_code == 400
    assert "at least 8 characters" in json.loads(response_reset_fail.data).get('message')
    
    # Reset password with strong password (should succeed)
    response_reset_success = client.post(f'/api/v1/auth/reset_password/{token}', json={
        'password': 'NewStrongPassword123!'
    })
    assert response_reset_success.status_code == 200
    assert "password has been updated" in json.loads(response_reset_success.data).get('message')
    
    # Attempt login with new password
    response_login = client.post('/api/v1/auth/login', json={
        'email': 'patient@test.com',
        'password': 'NewStrongPassword123!'
    })
    assert response_login.status_code == 200

def test_login_with_csrf_enabled_does_not_block(client, seed_data, app):
    app.config['WTF_CSRF_ENABLED'] = True
    try:
        response = client.post('/api/v1/auth/login', json={
            'email': 'admin@test.com',
            'password': 'AdminPassword123!'
        })
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data.get('status') == 'success'
    finally:
        app.config['WTF_CSRF_ENABLED'] = False
