import { useState, useEffect, useRef, useCallback } from 'react';

/**
 * Custom hook for managing WebSocket connections with auto-reconnect functionality
 * @param {string} url - WebSocket server URL
 * @param {Object} options - Configuration options
 * @param {boolean} options.autoConnect - Whether to connect automatically
 * @param {number} options.reconnectAttempts - Maximum number of reconnection attempts
 * @param {number} options.reconnectInterval - Time between reconnection attempts (ms)
 * @param {Function} options.onMessage - Callback for incoming messages
 * @param {Function} options.onOpen - Callback for connection open
 * @param {Function} options.onClose - Callback for connection close
 * @param {Function} options.onError - Callback for connection errors
 */
const useWebSocket = (url, options = {}) => {
  const {
    autoConnect = true,
    reconnectAttempts = 5,
    reconnectInterval = 3000,
    onMessage,
    onOpen,
    onClose,
    onError
  } = options;

  const [isConnected, setIsConnected] = useState(false);
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);
  const [connectionStatus, setConnectionStatus] = useState('disconnected');

  const wsRef = useRef(null);
  const reconnectTimeoutRef = useRef(null);
  const attemptCountRef = useRef(0);
  const reconnectAttemptsLeftRef = useRef(reconnectAttempts);

  // Clean up function
  const cleanup = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
  }, []);

  // Connect function
  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      return;
    }

    try {
      setConnectionStatus('connecting');
      setError(null);

      const ws = new WebSocket(url);
      wsRef.current = ws;

      ws.onopen = (event) => {
        console.log('WebSocket connected:', url);
        setIsConnected(true);
        setConnectionStatus('connected');
        setError(null);
        attemptCountRef.current = 0;
        reconnectAttemptsLeftRef.current = reconnectAttempts;

        if (onOpen) {
          onOpen(event);
        }
      };

      ws.onmessage = (event) => {
        try {
          const messageData = JSON.parse(event.data);
          setData(messageData);

          if (onMessage) {
            onMessage(messageData);
          }
        } catch (parseError) {
          console.error('Failed to parse WebSocket message:', parseError);
          setError('Failed to parse message data');
        }
      };

      ws.onclose = (event) => {
        console.log('WebSocket closed:', event.code, event.reason);
        setIsConnected(false);
        setConnectionStatus('disconnected');

        if (onClose) {
          onClose(event);
        }

        // Attempt to reconnect if not intentionally closed
        if (event.code !== 1000 && reconnectAttemptsLeftRef.current > 0) {
          const delay = reconnectInterval * Math.pow(2, attemptCountRef.current);
          console.log(`Reconnecting in ${delay}ms... (${reconnectAttemptsLeftRef.current} attempts left)`);

          reconnectTimeoutRef.current = setTimeout(() => {
            attemptCountRef.current++;
            reconnectAttemptsLeftRef.current--;
            connect();
          }, delay);
        } else if (reconnectAttemptsLeftRef.current <= 0) {
          setError('Max reconnection attempts reached');
          setConnectionStatus('failed');
        }
      };

      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        setError('WebSocket connection error');
        setConnectionStatus('error');

        if (onError) {
          onError(error);
        }
      };

    } catch (connectionError) {
      console.error('Failed to create WebSocket connection:', connectionError);
      setError('Failed to establish connection');
      setConnectionStatus('error');
    }
  }, [url, reconnectAttempts, reconnectInterval, onOpen, onClose, onError, onMessage]);

  // Disconnect function
  const disconnect = useCallback(() => {
    cleanup();
    setIsConnected(false);
    setConnectionStatus('disconnected');
  }, [cleanup]);

  // Send message function
  const sendMessage = useCallback((message) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      try {
        const messageString = typeof message === 'string' ? message : JSON.stringify(message);
        wsRef.current.send(messageString);
        return true;
      } catch (sendError) {
        console.error('Failed to send WebSocket message:', sendError);
        setError('Failed to send message');
        return false;
      }
    } else {
      console.warn('WebSocket is not connected');
      return false;
    }
  }, []);

  // Reconnect function
  const reconnect = useCallback(() => {
    disconnect();
    setTimeout(() => {
      attemptCountRef.current = 0;
      reconnectAttemptsLeftRef.current = reconnectAttempts;
      connect();
    }, 100);
  }, [disconnect, connect, reconnectAttempts]);

  // Heartbeat function
  const sendHeartbeat = useCallback(() => {
    sendMessage({
      type: 'heartbeat',
      timestamp: Date.now()
    });
  }, [sendMessage]);

  // Auto-connect on mount
  useEffect(() => {
    if (autoConnect) {
      connect();
    }

    // Set up heartbeat interval
    const heartbeatInterval = setInterval(() => {
      if (isConnected) {
        sendHeartbeat();
      }
    }, 30000); // Send heartbeat every 30 seconds

    // Cleanup on unmount
    return () => {
      cleanup();
      clearInterval(heartbeatInterval);
    };
  }, [autoConnect, connect, cleanup, isConnected, sendHeartbeat]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      cleanup();
    };
  }, [cleanup]);

  return {
    isConnected,
    data,
    error,
    connectionStatus,
    connect,
    disconnect,
    reconnect,
    sendMessage,
    sendHeartbeat
  };
};

export default useWebSocket;
