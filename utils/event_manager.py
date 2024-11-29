import asyncio
import threading


class ThreadSafeAsyncEventManager:
    """An event manager that supports both thread safety and async handling."""

    def __init__(self):
        self._events = {}  # Dictionary to hold events and their subscribers
        self._lock = threading.Lock()

    def subscribe(self, event_name, callback):
        """
        Subscribe a callback to an event.

        Args:
            event_name (str): Name of the event.
            callback (callable): The function or coroutine to call when the event is fired.
        """
        with self._lock:
            if event_name not in self._events:
                self._events[event_name] = []
            self._events[event_name].append(callback)

    def unsubscribe(self, event_name, callback):
        """
        Unsubscribe a callback from an event.

        Args:
            event_name (str): Name of the event.
            callback (callable): The function or coroutine to remove.
        """
        with self._lock:
            if event_name in self._events:
                self._events[event_name].remove(callback)
                if not self._events[event_name]:
                    del self._events[event_name]

    def fire(self, event_name, *args, **kwargs):
        """
        Fire an event, calling all subscribed callbacks.

        Args:
            event_name (str): Name of the event being fired.
            *args: Positional arguments to pass to callbacks.
            **kwargs: Keyword arguments to pass to callbacks.
        """
        with self._lock:
            callbacks = self._events.get(event_name, [])

        # Fire callbacks outside the lock to avoid deadlocks
        for callback in callbacks:
            if asyncio.iscoroutinefunction(callback):
                # Run async callbacks
                asyncio.run_coroutine_threadsafe(callback(*args, **kwargs), asyncio.get_event_loop())
            else:
                # Run synchronous callbacks
                callback(*args, **kwargs)
