#!/usr/bin/env python3
"""Unit test to verify event loop reuse optimization."""

import sys
import asyncio
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_event_loop_reuse():
    """Test that AgentSession reuses the same event loop."""
    # Import directly from factory to avoid circular import
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "factory",
        Path(__file__).parent / "agents" / "factory.py"
    )
    factory = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(factory)
    AgentSession = factory.AgentSession

    # Create a mock agent
    class MockAgent:
        async def run(self, input_text):
            # Simulate async work
            await asyncio.sleep(0.01)
            return f"Mock response to: {input_text}"

    config = {}
    mock_agent = MockAgent()

    print('Testing event loop reuse optimization...')
    print('=' * 60)

    # Create session
    session = AgentSession(mock_agent, config)

    # Get the event loop reference
    loop1 = session._event_loop
    print(f'✓ AgentSession created with event loop: {id(loop1)}')

    # Execute first message
    print('\n[Test 1] First execution...')
    response1 = session.execute('Hello')
    loop2 = session._event_loop
    print(f'  Event loop after execution: {id(loop2)}')
    print(f'  Response: {response1}')

    # Execute second message
    print('\n[Test 2] Second execution...')
    response2 = session.execute('World')
    loop3 = session._event_loop
    print(f'  Event loop after execution: {id(loop3)}')
    print(f'  Response: {response2}')

    # Verify it's the same loop
    print('\n' + '=' * 60)
    if loop1 is loop2 is loop3:
        print('✓ SUCCESS: Event loop is reused across executions!')
        print(f'  All three references point to same loop: {id(loop1)}')
        success = True
    else:
        print('✗ FAIL: Event loop is being recreated!')
        print(f'  Loop 1: {id(loop1)}')
        print(f'  Loop 2: {id(loop2)}')
        print(f'  Loop 3: {id(loop3)}')
        success = False

    # Verify loop is not closed
    if not loop1.is_closed():
        print('✓ Event loop is still open (as expected)')
    else:
        print('✗ Event loop was closed prematurely!')
        success = False

    # Test cleanup
    print('\nTesting cleanup...')
    session.close()
    if loop1.is_closed():
        print('✓ Event loop properly closed after session.close()')
    else:
        print('✗ Event loop was not closed!')
        success = False

    print('=' * 60)

    return 0 if success else 1

if __name__ == '__main__':
    sys.exit(test_event_loop_reuse())
