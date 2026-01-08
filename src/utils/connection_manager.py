"""
WebSocket Connection Manager for real-time progress updates.
Manages WebSocket connections and broadcasts progress updates to connected clients.
"""

import json
import logging
from typing import Dict, List, Set, Optional
from fastapi import WebSocket, WebSocketDisconnect
from dataclasses import dataclass, field
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class ConnectionInfo:
    """Information about a WebSocket connection."""
    websocket: WebSocket
    project_id: Optional[int] = None
    workflow_ids: Set[str] = field(default_factory=set)
    connected_at: datetime = field(default_factory=datetime.utcnow)


class ConnectionManager:
    """
    Manages WebSocket connections for real-time progress updates.
    
    Connections can subscribe to:
    - Specific workflow IDs
    - All workflows for a specific project
    """

    def __init__(self):
        # Map of connection_id -> ConnectionInfo
        self._connections: Dict[str, ConnectionInfo] = {}
        # Map of workflow_id -> set of connection_ids
        self._workflow_subscribers: Dict[str, Set[str]] = {}
        # Map of project_id -> set of connection_ids
        self._project_subscribers: Dict[int, Set[str]] = {}
        # Counter for generating connection IDs
        self._connection_counter = 0

    def _generate_connection_id(self) -> str:
        """Generate a unique connection ID."""
        self._connection_counter += 1
        return f"conn_{self._connection_counter}_{datetime.utcnow().timestamp()}"

    async def connect(
        self,
        websocket: WebSocket,
        project_id: Optional[int] = None,
        workflow_id: Optional[str] = None
    ) -> str:
        """
        Accept a new WebSocket connection and register it.
        
        Args:
            websocket: The WebSocket connection
            project_id: Optional project ID to subscribe to
            workflow_id: Optional specific workflow ID to subscribe to
        
        Returns:
            The connection ID
        """
        await websocket.accept()
        
        connection_id = self._generate_connection_id()
        workflow_ids = {workflow_id} if workflow_id else set()
        
        self._connections[connection_id] = ConnectionInfo(
            websocket=websocket,
            project_id=project_id,
            workflow_ids=workflow_ids
        )
        
        # Subscribe to project updates
        if project_id is not None:
            if project_id not in self._project_subscribers:
                self._project_subscribers[project_id] = set()
            self._project_subscribers[project_id].add(connection_id)
        
        # Subscribe to specific workflow
        if workflow_id:
            if workflow_id not in self._workflow_subscribers:
                self._workflow_subscribers[workflow_id] = set()
            self._workflow_subscribers[workflow_id].add(connection_id)
        
        logger.info(f"WebSocket connected: {connection_id} (project: {project_id}, workflow: {workflow_id})")
        
        # Send initial connection confirmation
        await self.send_personal_message(
            connection_id,
            {
                "type": "connected",
                "connection_id": connection_id,
                "project_id": project_id,
                "workflow_id": workflow_id,
                "message": "Connected to progress updates"
            }
        )
        
        return connection_id

    def disconnect(self, connection_id: str):
        """
        Disconnect and unregister a WebSocket connection.
        
        Args:
            connection_id: The connection ID to disconnect
        """
        if connection_id not in self._connections:
            return
        
        conn_info = self._connections[connection_id]
        
        # Remove from project subscribers
        if conn_info.project_id is not None:
            if conn_info.project_id in self._project_subscribers:
                self._project_subscribers[conn_info.project_id].discard(connection_id)
                if not self._project_subscribers[conn_info.project_id]:
                    del self._project_subscribers[conn_info.project_id]
        
        # Remove from workflow subscribers
        for workflow_id in conn_info.workflow_ids:
            if workflow_id in self._workflow_subscribers:
                self._workflow_subscribers[workflow_id].discard(connection_id)
                if not self._workflow_subscribers[workflow_id]:
                    del self._workflow_subscribers[workflow_id]
        
        # Remove connection
        del self._connections[connection_id]
        
        logger.info(f"WebSocket disconnected: {connection_id}")

    async def subscribe_to_workflow(self, connection_id: str, workflow_id: str):
        """
        Subscribe a connection to a specific workflow's updates.
        
        Args:
            connection_id: The connection ID
            workflow_id: The workflow ID to subscribe to
        """
        if connection_id not in self._connections:
            return
        
        self._connections[connection_id].workflow_ids.add(workflow_id)
        
        if workflow_id not in self._workflow_subscribers:
            self._workflow_subscribers[workflow_id] = set()
        self._workflow_subscribers[workflow_id].add(connection_id)
        
        logger.debug(f"Connection {connection_id} subscribed to workflow {workflow_id}")

    async def send_personal_message(self, connection_id: str, message: dict):
        """
        Send a message to a specific connection.
        
        Args:
            connection_id: The connection ID
            message: The message to send (will be JSON encoded)
        """
        if connection_id not in self._connections:
            return
        
        try:
            websocket = self._connections[connection_id].websocket
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"Failed to send message to {connection_id}: {e}")
            self.disconnect(connection_id)

    async def broadcast_workflow_progress(
        self,
        workflow_id: str,
        project_id: int,
        progress_data: dict
    ):
        """
        Broadcast progress update to all connections subscribed to the workflow or project.
        
        Args:
            workflow_id: The workflow ID
            project_id: The project ID
            progress_data: The progress data to broadcast
        """
        message = {
            "type": "progress_update",
            "workflow_id": workflow_id,
            "project_id": project_id,
            "timestamp": datetime.utcnow().isoformat(),
            **progress_data
        }
        
        # Get all relevant connection IDs
        connection_ids = set()
        
        # Add workflow-specific subscribers
        if workflow_id in self._workflow_subscribers:
            connection_ids.update(self._workflow_subscribers[workflow_id])
        
        # Add project-wide subscribers
        if project_id in self._project_subscribers:
            connection_ids.update(self._project_subscribers[project_id])
        
        # Send to all relevant connections
        disconnected = []
        for connection_id in connection_ids:
            if connection_id in self._connections:
                try:
                    websocket = self._connections[connection_id].websocket
                    await websocket.send_json(message)
                except Exception as e:
                    logger.error(f"Failed to broadcast to {connection_id}: {e}")
                    disconnected.append(connection_id)
        
        # Clean up disconnected connections
        for connection_id in disconnected:
            self.disconnect(connection_id)

    async def broadcast_to_project(self, project_id: int, message: dict):
        """
        Broadcast a message to all connections subscribed to a project.
        
        Args:
            project_id: The project ID
            message: The message to broadcast
        """
        if project_id not in self._project_subscribers:
            return
        
        disconnected = []
        for connection_id in self._project_subscribers[project_id]:
            if connection_id in self._connections:
                try:
                    websocket = self._connections[connection_id].websocket
                    await websocket.send_json(message)
                except Exception as e:
                    logger.error(f"Failed to broadcast to {connection_id}: {e}")
                    disconnected.append(connection_id)
        
        for connection_id in disconnected:
            self.disconnect(connection_id)

    def get_active_connections_count(self) -> int:
        """Get the number of active connections."""
        return len(self._connections)

    def get_project_connections_count(self, project_id: int) -> int:
        """Get the number of connections for a specific project."""
        if project_id not in self._project_subscribers:
            return 0
        return len(self._project_subscribers[project_id])


# Global connection manager instance
connection_manager = ConnectionManager()
