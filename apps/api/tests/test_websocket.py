from src.websocket_manager import ConnectionManager


def test_connection_manager():
    mgr = ConnectionManager()
    assert mgr.active_connections == {}
