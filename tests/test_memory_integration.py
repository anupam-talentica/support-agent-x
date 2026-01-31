"""Test script for Memory Agent with mem0."""

import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Must be run from project root
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.memory_agent.memory_agent import Mem0MemoryAgent
from agents.memory_agent.memory_tools import MemoryTools


async def test_memory_agent():
    """Test the memory agent functionality."""
    print("=" * 60)
    print("Testing Memory Agent with mem0")
    print("=" * 60)
    
    # Check environment
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ ERROR: OPENAI_API_KEY not set in environment")
        print("Please add OPENAI_API_KEY to your .env file")
        return
    
    print(f"✓ OpenAI API Key: {'*' * 10}{os.getenv('OPENAI_API_KEY')[-4:]}")
    print(f"✓ ChromaDB Host: {os.getenv('CHROMA_HOST', 'localhost')}")
    print(f"✓ ChromaDB Port: {os.getenv('CHROMA_PORT', '8000')}")
    print()
    
    try:
        # Initialize Memory Agent
        print("1. Initializing Memory Agent...")
        agent = Mem0MemoryAgent()
        tools = MemoryTools(agent)
        print("✓ Memory Agent initialized successfully")
        print()
        
        # Test 1: Store a ticket memory
        print("2. Storing a ticket memory...")
        ticket_result = await tools.store_ticket_resolution(
            ticket_id="TKT-TEST-001",
            user_id="test_user_123",
            query="Payment gateway keeps timing out when processing large orders",
            classification={
                "incident_type": "payment",
                "urgency": "P2",
                "affected_systems": ["payment_gateway"]
            },
            resolution="Increased payment gateway timeout from 30s to 60s. Also optimized database queries to reduce processing time."
        )
        print(f"✓ Stored ticket: {ticket_result}")
        print()
        
        # Test 2: Store user preference
        print("3. Storing user preference...")
        preference_result = await tools.store_context(
            information="User prefers to receive refunds via original payment method, not store credit. Also prefers email notifications over SMS.",
            user_id="test_user_123",
            ticket_id="TKT-TEST-001"
        )
        print(f"✓ Stored preference: {preference_result}")
        print()
        
        # Test 3: Search for similar tickets
        print("4. Searching for similar tickets...")
        similar_result = await tools.find_similar_tickets(
            query="Payment processing is very slow",
            user_id="test_user_123",
            limit=3
        )
        print(f"✓ Found similar tickets:")
        if similar_result.get('status') == 'success':
            for i, ticket in enumerate(similar_result.get('similar_tickets', []), 1):
                print(f"   {i}. Similarity: {ticket['similarity']:.2f}")
                print(f"      Content: {ticket['content'][:100]}...")
        else:
            print(f"   {similar_result.get('message')}")
        print()
        
        # Test 4: Recall user context
        print("5. Recalling user preferences...")
        recall_result = await tools.recall_context(
            query="refund preferences",
            user_id="test_user_123",
            limit=5
        )
        print(f"✓ Recalled context:")
        if recall_result.get('status') == 'success':
            for i, mem in enumerate(recall_result.get('memories', []), 1):
                print(f"   {i}. Relevance: {mem['relevance']:.2f}")
                print(f"      Content: {mem['content'][:100]}...")
        else:
            print(f"   {recall_result.get('message')}")
        print()
        
        # Test 5: Get all user history
        print("6. Getting complete user history...")
        history_result = await tools.get_user_history(user_id="test_user_123")
        print(f"✓ User history:")
        if history_result.get('status') == 'success':
            print(f"   Total memories: {history_result['total_memories']}")
            for i, mem in enumerate(history_result.get('memories', [])[:3], 1):
                print(f"   {i}. {mem['content'][:80]}...")
        else:
            print(f"   {history_result.get('message')}")
        print()
        
        # Test 6: Store another ticket to show pattern detection
        print("7. Storing another similar ticket...")
        ticket_result_2 = await tools.store_ticket_resolution(
            ticket_id="TKT-TEST-002",
            user_id="test_user_456",
            query="Dashboard loading very slowly, timing out",
            classification={
                "incident_type": "performance",
                "urgency": "P3"
            },
            resolution="Optimized database queries and added caching. Reduced load time from 45s to 3s."
        )
        print(f"✓ Stored second ticket: {ticket_result_2}")
        print()
        
        # Test 7: Cross-user search (find patterns)
        print("8. Searching across all users for timeout issues...")
        cross_user_result = await tools.find_similar_tickets(
            query="timeout problems",
            user_id="all_users",  # Search across all users
            limit=5
        )
        print(f"✓ Cross-user search:")
        if cross_user_result.get('status') == 'success':
            print(f"   Found {cross_user_result['count']} related tickets:")
            for i, ticket in enumerate(cross_user_result.get('similar_tickets', []), 1):
                print(f"   {i}. Similarity: {ticket['similarity']:.2f}")
                print(f"      {ticket['content'][:100]}...")
        else:
            print(f"   {cross_user_result.get('message')}")
        print()
        
        print("=" * 60)
        print("✓ All tests completed successfully!")
        print("=" * 60)
        print()
        print("Next steps:")
        print("1. Start the Memory Agent: python -m agents.memory_agent.__main__")
        print("2. Start other agents to integrate with the system")
        print("3. Check MEMORY_AGENT_GUIDE.md for detailed documentation")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_memory_agent())
