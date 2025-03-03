"""Tests for HTTP request handlers."""

import json
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from aiohttp import web

from server.handler_methods import (
    handle_message_post
)
from server.message_handler import MessageHandler


@pytest.fixture
def mock_storage():
    """Create a mock storage backend."""
    storage = MagicMock()
    storage.get_messages = AsyncMock(return_value=[])
    storage.save_message = AsyncMock(return_value=1)  # Return message ID
    storage.update_message = AsyncMock(return_value={
        'id': 1,
        'content': 'Test message',
        'author': 'test_user',
        'timestamp': '2025-01-17T14:04:38-05:00'
    })
    storage.get_message = AsyncMock(return_value={
        'id': 1,
        'content': 'Test message',
        'author': 'test_user',
        'timestamp': '2025-01-17T14:04:38-05:00'
    })
    return storage


@pytest.fixture
def mock_request(mock_storage):
    """Create a mock aiohttp request."""
    request = MagicMock()
    request.app = {'storage': mock_storage}
    request.headers = {'Content-Length': '100'}
    request.rfile = MagicMock()
    return request


@pytest.mark.asyncio
async def test_handle_message_post_success(mock_request):
    """Test successful message posting."""
    # Setup request data
    message_data = {
        'content': 'Hello, this is a test message',
        'author': 'test_user'
    }
    mock_request.json = AsyncMock(return_value=message_data)
    mock_request.rfile.read = MagicMock(return_value=json.dumps(message_data).encode('utf-8'))

    # Post message
    response = await handle_message_post(mock_request)
    
    # Verify response
    assert isinstance(response, web.Response)
    assert response.status == 200
    
    data = json.loads(response.text)
    assert 'id' in data
    assert 'content' in data
    assert 'author' in data
    assert 'timestamp' in data
    assert data['content'] == 'Hello, this is a test message'
    assert data['author'] == 'test_user'


@pytest.mark.asyncio
async def test_handle_message_post_missing_fields(mock_request):
    """Test message posting with missing fields."""
    # Test missing content
    mock_request.json = AsyncMock(return_value={
        'author': 'test_user'
    })
    response = await handle_message_post(mock_request)
    assert response.status == 400
    assert 'Missing required fields' in response.text

    # Test missing author
    mock_request.json = AsyncMock(return_value={
        'content': 'Test message'
    })
    response = await handle_message_post(mock_request)
    assert response.status == 400
    assert 'Missing required fields' in response.text
