"""Methods for handling chat requests."""

import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path

from aiohttp import web

from server.config import (
    STATIC_DIR,
    TEMPLATES_DIR
)

from server.message_handler import MessageHandler

logger = logging.getLogger(__name__)

async def serve_messages(request):
    """Serve messages."""
    try:
        message_handler = MessageHandler(request.app['storage'])
        response = await message_handler.handle_get_messages()
        return web.json_response(response)
    except Exception as e:
        logger.error(f'Error serving messages: {e}')
        return web.json_response({
            'success': False,
            'error': str(e)
        }, status=500)

async def handle_message_post(request):
    """Handle message post request."""
    try:
        data = await request.json()
        content = data.get('content', '').strip()
        author = data.get('author', '') or data.get('username', '').strip()

        if not content or not author:
            return web.json_response({
                'success': False,
                'error': 'Missing required fields'
            }, status=400)

        # Create message
        message_handler = MessageHandler(request.app['storage'])
        response = await message_handler.handle_post_message({
            'content': content,
            'author': author
        })

        if isinstance(response, dict) and not response.get('success', True):
            return web.json_response(response, status=400)

        return web.json_response(response['data'], status=200)

    except json.JSONDecodeError:
        return web.json_response({
            'success': False,
            'error': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        logger.error(f'Error handling message post: {e}')
        return web.json_response({
            'success': False,
            'error': str(e)
        }, status=500)

async def handle_username_change(request):
    """Handle username change request."""
    try:
        data = await request.json()
        old_username = data.get('old_username', '').strip()
        new_username = data.get('new_username', '').strip()

        if not new_username:
            return web.Response(status=400, text='New username cannot be empty')

        if not (3 <= len(new_username) <= 20):
            return web.Response(status=400, text='Username must be between 3 and 20 characters')

        if not new_username.replace('_', '').isalnum():
            return web.Response(status=400, text='Username can only contain letters, numbers, and underscores')

        # For now, we'll just accept any valid username change
        # In a real app, you might want to check if username is taken, etc.
        return web.json_response({
            'success': True,
            'username': new_username
        })
    except Exception as e:
        logger.error(f'Error changing username: {e}')
        return web.json_response({
            'success': False,
            'error': str(e)
        }, status=500)
