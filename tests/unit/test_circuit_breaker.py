"""
Tests for CircuitBreaker in VectorStore.
"""

import time
import logging
import unittest
from unittest.mock import MagicMock, patch

logging.disable(logging.CRITICAL)


class TestCircuitBreaker(unittest.TestCase):
    """Unit tests for the CircuitBreaker class."""

    def setUp(self):
        from foton_system.core.memory.vector_store import CircuitBreaker
        self.cb = CircuitBreaker(failure_threshold=3, recovery_timeout=60.0)

    def test_initial_state_closed(self):
        self.assertEqual(self.cb.state, "CLOSED")

    def test_single_call_success(self):
        def ok():
            return "result"
        self.assertEqual(self.cb.call(ok), "result")
        self.assertEqual(self.cb.state, "CLOSED")

    def test_three_failures_opens_circuit(self):
        def fail():
            raise ValueError("test error")
        for _ in range(3):
            with self.assertRaises(ValueError):
                self.cb.call(fail)
        self.assertEqual(self.cb.state, "OPEN")

    def test_open_circuit_raises_breaker_error(self):
        def fail():
            raise ValueError("test error")
        for _ in range(3):
            with self.assertRaises(ValueError):
                self.cb.call(fail)

        from foton_system.core.memory.vector_store import CircuitBreakerOpenError
        with self.assertRaises(CircuitBreakerOpenError):
            self.cb.call(fail)

    def test_recovery_after_timeout(self):
        real_time = time.time

        def fail():
            raise ValueError("test error")

        try:
            time.time = lambda: real_time()
            for _ in range(3):
                with self.assertRaises(ValueError):
                    self.cb.call(fail)
            self.assertEqual(self.cb.state, "OPEN")

            time.time = lambda: real_time() + 61.0

            def succeed():
                return "ok"
            result = self.cb.call(succeed)
            self.assertEqual(result, "ok")
            self.assertEqual(self.cb.state, "CLOSED")
        finally:
            time.time = real_time

    def test_half_open_failure_goes_back_to_open(self):
        real_time = time.time

        def fail():
            raise ValueError("test error")

        try:
            time.time = lambda: real_time()
            for _ in range(3):
                with self.assertRaises(ValueError):
                    self.cb.call(fail)
            self.assertEqual(self.cb.state, "OPEN")

            time.time = lambda: real_time() + 61.0

            with self.assertRaises(ValueError):
                self.cb.call(fail)
            self.assertEqual(self.cb.state, "OPEN")
        finally:
            time.time = real_time

    def test_failure_below_threshold_recovers(self):
        def fail():
            raise ValueError("test error")

        with self.assertRaises(ValueError):
            self.cb.call(fail)
        with self.assertRaises(ValueError):
            self.cb.call(fail)

        def ok():
            return "result"
        self.assertEqual(self.cb.call(ok), "result")
        self.assertEqual(self.cb.state, "CLOSED")

    def test_success_resets_last_exception(self):
        def fail():
            raise ValueError("test error")
        with self.assertRaises(ValueError):
            self.cb.call(fail)
        self.assertIsNotNone(self.cb.last_exception)

        def ok():
            return "result"
        self.cb.call(ok)
        self.assertIsNone(self.cb.last_exception)

    def test_last_exception_tracks_reason(self):
        def fail():
            raise ValueError("test error")
        with self.assertRaises(ValueError):
            self.cb.call(fail)
        self.assertIn("test error", self.cb.last_exception or "")


class TestVectorStoreCircuitBreaker(unittest.TestCase):
    """Tests for VectorStore integration with circuit breaker."""

    def test_add_documents_handles_open_circuit_gracefully(self):
        from foton_system.core.memory.vector_store import VectorStore
        store = VectorStore.__new__(VectorStore)
        store._initialized = True
        store._breaker = MagicMock()
        store._breaker.call.side_effect = [
            __import__('foton_system.core.memory.vector_store', fromlist=['CircuitBreakerOpenError']).CircuitBreakerOpenError("OPEN")
        ]

        result = store.add_documents(
            documents=["test"],
            metadatas=[{"source": "test.md"}],
            ids=["1"]
        )
        self.assertIsNone(result)

    def test_query_handles_open_circuit_gracefully(self):
        from foton_system.core.memory.vector_store import VectorStore
        store = VectorStore.__new__(VectorStore)
        store._initialized = True
        store._breaker = MagicMock()
        from foton_system.core.memory.vector_store import CircuitBreakerOpenError
        store._breaker.call.side_effect = CircuitBreakerOpenError("OPEN")

        result = store.query("test query")
        self.assertEqual(result, {"documents": [[]], "metadatas": [[]], "distances": [[]], "ids": [[]]})

    def test_delete_handles_open_circuit_gracefully(self):
        from foton_system.core.memory.vector_store import VectorStore
        store = VectorStore.__new__(VectorStore)
        store._initialized = True
        store._breaker = MagicMock()
        from foton_system.core.memory.vector_store import CircuitBreakerOpenError
        store._breaker.call.side_effect = CircuitBreakerOpenError("OPEN")

        result = store.delete(["1"])
        self.assertIsNone(result)

    def test_count_handles_open_circuit_gracefully(self):
        from foton_system.core.memory.vector_store import VectorStore
        store = VectorStore.__new__(VectorStore)
        store._initialized = True
        store._breaker = MagicMock()
        from foton_system.core.memory.vector_store import CircuitBreakerOpenError
        store._breaker.call.side_effect = CircuitBreakerOpenError("OPEN")

        result = store.count()
        self.assertEqual(result, 0)


if __name__ == '__main__':
    unittest.main()
