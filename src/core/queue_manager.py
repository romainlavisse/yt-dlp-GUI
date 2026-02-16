import queue
import typing

"""
Global Thread-Safe Event Queue.

This queue is used for communication between background threads (DownloadWorker) 
and the main UI thread (App).

Usage:
- Background threads put messages (dict) into 'event_queue'.
- Main thread periodically checks 'event_queue' and updates the UI accordingly.

Message Format (Dict):
{
    "type": "progress" | "status" | "error",
    "task_id": str,
    "payload": Any
}
"""

event_queue: queue.Queue = queue.Queue()

def put_message(msg_type: str, payload: typing.Any, task_id: str = ""):
    """
    Helper function to push a standard message to the event queue.
    
    Args:
        msg_type (str): The category of the message (e.g., 'progress', 'error').
        payload (Any): The data associated with the message (e.g., progress dict, error string).
        task_id (str): The ID of the task originating the message.
    """
    event_queue.put({
        "type": msg_type,
        "payload": payload,
        "task_id": task_id
    })
