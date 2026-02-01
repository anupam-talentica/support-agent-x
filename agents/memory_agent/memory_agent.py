"""Memory Agent powered by mem0 for intelligent conversational memory."""

import json
import logging
import os
from typing import Any, Dict, List, Optional

from mem0 import Memory

from .mem0_config import get_mem0_config

logger = logging.getLogger(__name__)


class Mem0MemoryAgent:
    """Memory agent powered by mem0 for intelligent fact extraction and recall."""
    
    def __init__(self):
        """Initialize mem0 memory agent with ChromaDB backend."""
        logger.info("Initializing Mem0 Memory Agent...")
        
        try:
            config = get_mem0_config()
            self.memory = Memory.from_config(config)
            logger.info("Successfully initialized mem0 with ChromaDB")
        except Exception as e:
            logger.error(f"Failed to initialize mem0: {e}")
            raise
    
    def add_memory(
        self, 
        message: str, 
        user_id: str, 
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Add a memory for a specific user/ticket.
        
        Mem0 will intelligently extract facts from the message and store them.
        
        Args:
            message: The message or context to remember
            user_id: User ID or ticket ID to associate memory with
            metadata: Additional metadata (e.g., ticket_id, timestamp)
            
        Returns:
            Result from mem0 with memory IDs
        """
        try:
            messages = [{"role": "user", "content": message}]
            result = self.memory.add(messages, user_id=user_id, metadata=metadata)
            logger.info(f"Added memory for user {user_id}: {result}")
            return result
        except Exception as e:
            logger.error(f"Failed to add memory: {e}")
            return {"error": str(e)}
    
    def search_memory(
        self, 
        query: str, 
        user_id: str, 
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Search memories for a user using semantic search.
        
        Args:
            query: Search query
            user_id: User ID to search memories for
            limit: Maximum number of results
            
        Returns:
            List of relevant memories with scores
        """
        try:
            results = self.memory.search(query, user_id=user_id, limit=limit)
            logger.info(f"Found {len(results)} memories for query: {query[:50]}...")
            return results
        except Exception as e:
            logger.error(f"Failed to search memory: {e}")
            return []
    
    def get_all_memories(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Get all memories for a specific user.
        
        Args:
            user_id: User ID to retrieve memories for
            
        Returns:
            List of all memories for the user
        """
        try:
            results = self.memory.get_all(user_id=user_id)
            logger.info(f"Retrieved {len(results)} total memories for user {user_id}")
            return results
        except Exception as e:
            logger.error(f"Failed to get all memories: {e}")
            return []
    
    def update_memory(self, memory_id: str, data: str) -> Dict[str, Any]:
        """
        Update a specific memory.
        
        Args:
            memory_id: ID of the memory to update
            data: New data for the memory
            
        Returns:
            Update result
        """
        try:
            result = self.memory.update(memory_id, data)
            logger.info(f"Updated memory {memory_id}")
            return result
        except Exception as e:
            logger.error(f"Failed to update memory: {e}")
            return {"error": str(e)}
    
    def delete_memory(self, memory_id: str) -> Dict[str, Any]:
        """
        Delete a specific memory.
        
        Args:
            memory_id: ID of the memory to delete
            
        Returns:
            Deletion result
        """
        try:
            result = self.memory.delete(memory_id)
            logger.info(f"Deleted memory {memory_id}")
            return result
        except Exception as e:
            logger.error(f"Failed to delete memory: {e}")
            return {"error": str(e)}
    
    def add_ticket_memory(
        self,
        ticket_id: str,
        user_id: str,
        query: str,
        classification: Optional[Dict[str, Any]] = None,
        resolution: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Add memory for a support ticket interaction.
        
        Args:
            ticket_id: Ticket ID
            user_id: User ID
            query: User's query/issue
            classification: Intent classification results
            resolution: Resolution provided (if any)
            
        Returns:
            Memory addition result
        """
        # Build context message
        context_parts = [f"Ticket {ticket_id}: User reported issue - {query}"]
        
        if classification is not None:
            # Planner may pass classification as JSON string; normalize to dict
            if isinstance(classification, str):
                try:
                    parsed = json.loads(classification) if classification.strip() else {}
                    classification = parsed if isinstance(parsed, dict) else {}
                except (json.JSONDecodeError, AttributeError):
                    classification = {}
            if isinstance(classification, dict) and classification:
                intent_type = classification.get('incident_type', 'unknown')
                urgency = classification.get('urgency', 'unknown')
                context_parts.append(f"Classified as {intent_type} with {urgency} urgency")
        
        if resolution:
            context_parts.append(f"Resolution: {resolution}")
        
        message = ". ".join(context_parts)
        
        metadata = {
            "ticket_id": ticket_id,
            "type": "support_ticket"
        }
        
        return self.add_memory(message, user_id=user_id, metadata=metadata)
    
    def recall_similar_tickets(
        self,
        query: str,
        user_id: Optional[str] = None,
        limit: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Recall similar past tickets/issues.
        
        Args:
            query: Current issue description
            user_id: Optional user ID to scope search
            limit: Number of similar tickets to return
            
        Returns:
            List of similar past issues with context
        """
        # If no user_id, search across all users
        search_user = user_id if user_id else "all_users"
        
        return self.search_memory(query, user_id=search_user, limit=limit)
