"""Memory tools for integration with ADK/LangGraph agents."""

import logging
from typing import Any, Dict, List, Optional

from .memory_agent import Mem0MemoryAgent

logger = logging.getLogger(__name__)


class MemoryTools:
    """Tools for mem0 memory operations exposed to other agents."""
    
    def __init__(self, memory_agent: Optional[Mem0MemoryAgent] = None):
        """
        Initialize memory tools.
        
        Args:
            memory_agent: Optional Mem0MemoryAgent instance. If None, creates a new one.
        """
        self.memory_agent = memory_agent or Mem0MemoryAgent()
    
    async def store_context(
        self, 
        information: str, 
        user_id: str, 
        ticket_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Store important information about user interactions.
        
        Use this tool to remember key facts, preferences, or patterns from conversations.
        Mem0 will intelligently extract and store relevant information.
        
        Args:
            information: The information to remember
            user_id: User ID to associate memory with
            ticket_id: Optional ticket ID for context
            
        Returns:
            Status of memory storage
        """
        metadata = {"ticket_id": ticket_id} if ticket_id else {}
        result = self.memory_agent.add_memory(information, user_id, metadata)
        
        if "error" in result:
            return {"status": "failed", "error": result["error"]}
        
        return {
            "status": "success",
            "message": "Information stored in memory",
            "memory_ids": result.get("results", [])
        }
    
    async def recall_context(
        self, 
        query: str, 
        user_id: str,
        limit: int = 5
    ) -> Dict[str, Any]:
        """
        Search for relevant past interactions and information.
        
        Use this tool to recall what you know about a user or similar past issues.
        
        Args:
            query: What to search for
            user_id: User ID to search memories for
            limit: Maximum number of results
            
        Returns:
            Relevant memories
        """
        memories = self.memory_agent.search_memory(query, user_id, limit)
        
        if not memories:
            return {
                "status": "no_results",
                "message": "No relevant memories found"
            }
        
        formatted_memories = []

        for mem in memories:
            if isinstance(mem, dict):
                formatted_memories.append({
                    "content": mem.get("memory", ""),
                    "relevance": mem.get("score", 0.0),
                    "id": mem.get("id", ""),
                    "metadata": mem.get("metadata", {})
                })
            elif isinstance(mem, str):
                formatted_memories.append({
                    "content": mem,
                    "relevance": 0.0,
                    "id": "",
                    "metadata": {}
                })
            else:
                logger.warning(f"Unexpected memory item type: {type(mem)}")
        
        return {
            "status": "success",
            "count": len(formatted_memories),
            "memories": formatted_memories
        }
    
    async def get_user_history(self, user_id: str) -> Dict[str, Any]:
        """
        Get complete interaction history for a user.
        
        Use this to understand a user's full context and interaction patterns.
        
        Args:
            user_id: User ID to retrieve history for
            
        Returns:
            All memories for the user
        """
        memories = self.memory_agent.get_all_memories(user_id)
        
        # Handle dict response
        if isinstance(memories, dict):
            if "results" in memories:
                memories = memories["results"]
            elif "memories" in memories:
                memories = memories["memories"]
        
        if not memories:
            return {
                "status": "no_history",
                "message": f"No interaction history found for user {user_id}"
            }
        
        formatted_memories = []
        for mem in memories:
            formatted_memories.append({
                "id": mem.get("id", ""),
                "content": mem.get("memory", ""),
                "created_at": mem.get("created_at", ""),
                "metadata": mem.get("metadata", {})
            })
        
        return {
            "status": "success",
            "user_id": user_id,
            "total_memories": len(formatted_memories),
            "memories": formatted_memories
        }
    
    async def store_ticket_resolution(
        self,
        ticket_id: str,
        user_id: str,
        query: str,
        classification: Dict[str, Any],
        resolution: str
    ) -> Dict[str, Any]:
        """
        Store a complete ticket with its resolution for future reference.
        
        This creates a comprehensive memory of the support interaction.
        
        Args:
            ticket_id: Ticket ID
            user_id: User ID
            query: Original user query
            classification: Intent classification results
            resolution: How the issue was resolved
            
        Returns:
            Storage result
        """
        result = self.memory_agent.add_ticket_memory(
            ticket_id=ticket_id,
            user_id=user_id,
            query=query,
            classification=classification,
            resolution=resolution
        )
        
        if "error" in result:
            return {"status": "failed", "error": result["error"]}
        
        return {
            "status": "success",
            "message": f"Stored resolution for ticket {ticket_id}",
            "memory_ids": result.get("results", [])
        }
    
    async def find_similar_tickets(
        self,
        query: str,
        user_id: Optional[str] = None,
        limit: int = 3
    ) -> Dict[str, Any]:
        """
        Find similar past tickets to help with current issue.
        
        Use this to find if similar issues have been resolved before.
        
        Args:
            query: Current issue description
            user_id: Optional user ID to scope to specific user
            limit: Number of similar tickets to return
            
        Returns:
            Similar past tickets
        """
        similar = self.memory_agent.recall_similar_tickets(
            query=query,
            user_id=user_id,
            limit=limit
        )
        
        # Handle dict response
        if isinstance(similar, dict):
            if "results" in similar:
                similar = similar["results"]
            elif "similar_tickets" in similar:  # Just in case
                similar = similar["similar_tickets"]
        
        if not similar:
            return {
                "status": "no_matches",
                "message": "No similar past tickets found"
            }
        formatted_results = []
        for item in similar:
            if isinstance(item, dict):
                formatted_results.append({
                    "content": item.get("memory", ""),
                    "similarity": item.get("score", 0.0),
                    "metadata": item.get("metadata", {})
                })
            elif isinstance(item, str):
                formatted_results.append({
                    "content": item,
                    "similarity": 0.0,
                    "metadata": {}
                })
            else:
                logger.warning(f"Unexpected item type in similar tickets keys: {type(item)}")
                
        return {
            "status": "success",
            "count": len(formatted_results),
            "similar_tickets": formatted_results,
            "message": f"Found {len(formatted_results)} similar past tickets"
        }
