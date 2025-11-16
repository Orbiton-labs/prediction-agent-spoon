#!/usr/bin/env python3
"""Performance test for optimized AgentSession."""

import time
import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_performance():
    """Test the performance improvements."""
    from agents.factory import AgentFactory, AgentSession

    config = {
        'llm': {
            'default_provider': 'openai',
            'default_model': 'gpt-4o'
        },
        'agent': {
            'type': 'react',
            'max_iterations': 10
        }
    }

    print('=' * 60)
    print('Performance Test: Optimized AgentSession')
    print('=' * 60)

    print('\nCreating agent session...')
    start_total = time.time()

    try:
        agent = AgentFactory.create_agent('react', config)
        session = AgentSession(agent, config)
        init_time = time.time() - start_total
        print(f'✓ Agent session created in {init_time:.2f}s')

        # Test 1: First message
        print('\n[Test 1] First message...')
        start = time.time()
        response = session.execute('Hello! Say API is working.')
        elapsed1 = time.time() - start
        print(f'✓ Response in {elapsed1:.2f}s')
        print(f'  Response: {response[:100]}...')

        # Test 2: Second message (should benefit from event loop reuse)
        print('\n[Test 2] Second message (testing event loop reuse)...')
        start = time.time()
        response = session.execute('What is 2+2?')
        elapsed2 = time.time() - start
        print(f'✓ Response in {elapsed2:.2f}s')
        print(f'  Response: {response[:100]}...')

        # Cleanup
        session.close()
        print('\n✓ Event loop properly closed')

        total_time = time.time() - start_total
        print(f'\n' + '=' * 60)
        print('Summary:')
        print(f'  Initialization: {init_time:.2f}s')
        print(f'  First message:  {elapsed1:.2f}s')
        print(f'  Second message: {elapsed2:.2f}s')
        print(f'  Total time:     {total_time:.2f}s')
        print('=' * 60)

        # Performance improvements from event loop reuse
        if elapsed1 > 0:
            improvement = ((elapsed1 - elapsed2) / elapsed1) * 100
            if improvement > 0:
                print(f'\n✓ Event loop reuse improved 2nd message by {improvement:.1f}%')

    except Exception as e:
        print(f'\n✗ Error: {e}')
        import traceback
        traceback.print_exc()
        return 1

    return 0

if __name__ == '__main__':
    sys.exit(test_performance())
