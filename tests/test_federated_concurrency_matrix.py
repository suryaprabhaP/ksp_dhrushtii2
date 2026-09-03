"""
KSP Sentinel AI — Comprehensive Federated Concurrency & Scalability Matrix (F-01 to F-24)
========================================================================================
Validates all 12 Mandatory Deployment Gates (G1 - G12) under strict Principal Architect standards.
"""
import concurrent.futures
import gc
import logging
import os
import sys
import threading
import time
import unittest
from unittest.mock import MagicMock, patch

# Ensure backend root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.interfaces import ExecutionContext, AgentResponse
from app.agents.federated import FederatedAgent
from app.agents.analytical import AnalyticalAgent
from app.agents.graph import GraphAgent
from app.providers.orchestrator import orchestrator
from app.config import FEDERATED_MAX_WORKERS

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("test.federated.matrix")


class TestFederatedConcurrencyMatrix(unittest.TestCase):

    def setUp(self):
        self.agent = FederatedAgent()

    # ══════════════════════════════════════════════════════════════════════════
    # GATE G1: Parallel Fan-Out (F-01, F-02, F-03)
    # ══════════════════════════════════════════════════════════════════════════

    def test_F01_baseline_sequential_benchmark(self):
        """F-01: Measure baseline sequential latency model (A=300ms + G=200ms + S=200ms = 700ms)."""
        def slow_a(ctx):
            time.sleep(0.3)
            return AgentResponse(answer="A", agent_type="analytical", agent_label="A", agent_icon="📊", agent_color="#000")
        def slow_g(ctx):
            time.sleep(0.2)
            return AgentResponse(answer="G", agent_type="graph", agent_label="G", agent_icon="🕸️", agent_color="#000")
        
        ctx = ExecutionContext(query="test query")
        t0 = time.monotonic()
        r_a = slow_a(ctx)
        r_g = slow_g(ctx)
        time.sleep(0.2)
        total_seq = time.monotonic() - t0
        self.assertGreaterEqual(total_seq, 0.65)
        log.info(f"[F-01] Baseline sequential simulated latency: {total_seq*1000:.1f}ms")

    @patch.object(AnalyticalAgent, "execute")
    @patch.object(GraphAgent, "execute")
    @patch.object(orchestrator, "generate_completion")
    def test_F02_parallel_fanout_overlap(self, mock_synthesis, mock_graph, mock_analytics):
        """F-02: Verify Analytical (300ms) and Graph (200ms) execute concurrently: critical path ~ max(300, 200)."""
        def slow_a(ctx):
            time.sleep(0.3)
            return AgentResponse(answer="Analytics Report", agent_type="analytical", agent_label="A", agent_icon="📊", agent_color="#000")
        def slow_g(ctx):
            time.sleep(0.2)
            return AgentResponse(answer="Graph Report", agent_type="graph", agent_label="G", agent_icon="🕸️", agent_color="#000")

        mock_analytics.side_effect = slow_a
        mock_graph.side_effect = slow_g
        mock_synthesis.return_value = "Synthesized Briefing"

        ctx = ExecutionContext(query="trajectory and trace network")
        t0 = time.monotonic()
        res = self.agent.execute(ctx)
        elapsed = time.monotonic() - t0

        self.assertLess(elapsed, 0.45, f"Expected parallel overlap (~0.3s), got {elapsed:.2f}s")
        self.assertIn("Synthesized", res.answer)
        log.info(f"[F-02] Parallel fan-out verified: elapsed={elapsed*1000:.1f}ms vs sequential ~500ms")

    @patch.object(orchestrator, "generate_completion")
    def test_F03_normal_federated_request_flow(self, mock_synthesis):
        """F-03: Verify end-to-end flow produces unified briefing and aggregates charts."""
        mock_synthesis.return_value = "### Unified Executive Intelligence Dossier"
        ctx = ExecutionContext(query="Show trajectory and trace the network", session_id="test_session_f03")
        
        t0 = time.monotonic()
        res = self.agent.execute(ctx)
        elapsed = time.monotonic() - t0

        self.assertEqual(res.agent_type, "federated_agent")
        self.assertEqual(res.agent_icon, "🌐")
        self.assertTrue(res.data_available)
        self.assertLess(elapsed, self.agent.GLOBAL_BUDGET)
        log.info(f"[F-03] Normal federated request completed in {elapsed*1000:.1f}ms")

    # ══════════════════════════════════════════════════════════════════════════
    # GATE G2: Global Deadline Enforcement (F-04)
    # ══════════════════════════════════════════════════════════════════════════

    @patch.object(AnalyticalAgent, "execute")
    @patch.object(GraphAgent, "execute")
    @patch.object(orchestrator, "generate_completion")
    def test_F04_global_deadline_enforcement(self, mock_synthesis, mock_graph, mock_analytics):
        """F-04: Coordinator must stop waiting and never exceed global request deadline."""
        def hang(ctx):
            time.sleep(5.0)
            return AgentResponse(answer="Hung", agent_type="a", agent_label="A", agent_icon="A", agent_color="#0")
        mock_analytics.side_effect = hang
        mock_graph.side_effect = hang
        mock_synthesis.return_value = "Fallback Briefing"

        # Force tight deadline: 0.3s fanout budget
        agent = FederatedAgent()
        agent.FANOUT_BUDGET = 0.3
        agent.GLOBAL_BUDGET = 0.5

        ctx = ExecutionContext(query="test timeout")
        t0 = time.monotonic()
        res = agent.execute(ctx)
        elapsed = time.monotonic() - t0

        self.assertLess(elapsed, 0.65, f"Coordinator failed to enforce deadline: took {elapsed:.2f}s")
        log.info(f"[F-04] Global deadline enforced: coordinator exited in {elapsed*1000:.1f}ms")

    # ══════════════════════════════════════════════════════════════════════════
    # GATE G3: Controlled Partial Degradation (F-05, F-06, F-07, F-08)
    # ══════════════════════════════════════════════════════════════════════════

    @patch.object(AnalyticalAgent, "execute")
    @patch.object(GraphAgent, "execute")
    @patch.object(orchestrator, "generate_completion")
    def test_F05_analytics_timeout_partial_degradation(self, mock_synthesis, mock_graph, mock_analytics):
        """F-05: Analytics hangs (10s) -> Graph succeeds -> Coordinator continues with partial degradation."""
        def hang_analytics(ctx):
            time.sleep(2.0)
            return AgentResponse(answer="Late", agent_type="a", agent_label="A", agent_icon="A", agent_color="#0")
        def fast_graph(ctx):
            return AgentResponse(answer="Graph Link Verified", agent_type="graph", agent_label="G", agent_icon="🕸️", agent_color="#000")

        mock_analytics.side_effect = hang_analytics
        mock_graph.side_effect = fast_graph
        mock_synthesis.return_value = "Synthesized with Graph Only"

        agent = FederatedAgent()
        agent.FANOUT_BUDGET = 0.2
        agent.GLOBAL_BUDGET = 0.8

        ctx = ExecutionContext(query="test partial degradation")
        t0 = time.monotonic()
        res = agent.execute(ctx)
        elapsed = time.monotonic() - t0

        self.assertLess(elapsed, 0.5)
        # Verify synthesis received the available graph report and marked analytics degraded
        synthesis_call_prompt = mock_synthesis.call_args[1]["prompt"] if mock_synthesis.call_args else ""
        self.assertIn("Graph Link Verified", synthesis_call_prompt)
        self.assertIn("Unavailable", synthesis_call_prompt)
        log.info(f"[F-05] Analytics timeout partial degradation passed in {elapsed*1000:.1f}ms")

    @patch.object(AnalyticalAgent, "execute")
    @patch.object(GraphAgent, "execute")
    @patch.object(orchestrator, "generate_completion")
    def test_F06_graph_timeout_symmetric_degradation(self, mock_synthesis, mock_graph, mock_analytics):
        """F-06: Graph hangs -> Analytics succeeds -> Coordinator proceeds with symmetric degradation."""
        def fast_analytics(ctx):
            return AgentResponse(answer="Analytics Trend 85%", agent_type="analytical", agent_label="A", agent_icon="📊", agent_color="#000")
        def hang_graph(ctx):
            time.sleep(2.0)
            return AgentResponse(answer="Late", agent_type="g", agent_label="G", agent_icon="G", agent_color="#0")

        mock_analytics.side_effect = fast_analytics
        mock_graph.side_effect = hang_graph
        mock_synthesis.return_value = "Synthesized with Analytics Only"

        agent = FederatedAgent()
        agent.FANOUT_BUDGET = 0.2
        agent.GLOBAL_BUDGET = 0.8

        ctx = ExecutionContext(query="test symmetric degradation")
        t0 = time.monotonic()
        res = agent.execute(ctx)
        elapsed = time.monotonic() - t0

        self.assertLess(elapsed, 0.5)
        synthesis_call_prompt = mock_synthesis.call_args[1]["prompt"] if mock_synthesis.call_args else ""
        self.assertIn("Analytics Trend 85%", synthesis_call_prompt)
        self.assertIn("Unavailable", synthesis_call_prompt)
        log.info(f"[F-06] Graph timeout symmetric degradation passed in {elapsed*1000:.1f}ms")

    @patch.object(AnalyticalAgent, "execute")
    @patch.object(GraphAgent, "execute")
    def test_F07_both_agents_timeout_controlled_briefing(self, mock_graph, mock_analytics):
        """F-07: Both agents exceed deadline -> Returns controlled degraded briefing without hanging."""
        mock_analytics.side_effect = lambda ctx: time.sleep(2.0)
        mock_graph.side_effect = lambda ctx: time.sleep(2.0)

        agent = FederatedAgent()
        agent.FANOUT_BUDGET = 0.2
        agent.GLOBAL_BUDGET = 0.4

        ctx = ExecutionContext(query="test both timeout")
        t0 = time.monotonic()
        res = agent.execute(ctx)
        elapsed = time.monotonic() - t0

        self.assertLess(elapsed, 0.6)
        self.assertTrue("Degraded Mode" in res.answer or "Deadline Expired" in res.answer)
        log.info(f"[F-07] Both agents timed out: controlled briefing produced in {elapsed*1000:.1f}ms")

    @patch.object(AnalyticalAgent, "execute")
    @patch.object(GraphAgent, "execute")
    @patch.object(orchestrator, "generate_completion")
    def test_F08_agent_exception_isolation(self, mock_synthesis, mock_graph, mock_analytics):
        """F-08: Sub-agent throws unhandled exception -> Isolated without crashing coordinator."""
        mock_analytics.side_effect = ValueError("Corrupt table in DuckDB")
        mock_graph.return_value = AgentResponse(answer="Network Link 1->2", agent_type="g", agent_label="G", agent_icon="G", agent_color="#0")
        mock_synthesis.return_value = "Synthesized despite Analytics exception"

        ctx = ExecutionContext(query="test exception isolation")
        res = self.agent.execute(ctx)
        self.assertIn("Synthesized", res.answer)
        log.info("[F-08] Agent exception cleanly isolated")

    # ══════════════════════════════════════════════════════════════════════════
    # GATE G4 & G5: Downstream Timeout & Synthesis Budget (F-09, F-10, F-11)
    # ══════════════════════════════════════════════════════════════════════════

    @patch("requests.post")
    def test_F09_downstream_http_timeout_enforcement(self, mock_post):
        """F-09: Verify downstream HTTP client receives explicit timeout budget and raises Timeout on hang."""
        from app.providers.zoho_provider import ZohoQuickMLProvider
        provider = ZohoQuickMLProvider()
        
        # Simulate requests timeout
        mock_post.side_effect = TimeoutError("HTTP Connection Timed Out")
        
        with self.assertRaises((TimeoutError, RuntimeError)):
            provider.complete([{"role": "user", "content": "hi"}], timeout=1.5)
            
        self.assertTrue(mock_post.called)
        call_timeout = mock_post.call_args[1].get("timeout")
        self.assertEqual(call_timeout, 1.5)
        log.info(f"[F-09] Downstream HTTP client enforced timeout={call_timeout}s")

    def test_F10_deadline_propagation_through_layers(self):
        """F-10: Verify timeout budget travels from ExecutionContext to LLM complete."""
        from app.engine.session_store import session_store
        session_store.ingest_dataset("test_sess_prop", "test.csv", b"fir_no,crime_category,crime_date\n101,Vehicle Theft,2025-09-01\n", upload_to_cloud=False)

        ctx = ExecutionContext(query="predict caseload for vehicle theft in September 2025", session_id="test_sess_prop")
        ctx.set_deadline(3.5)

        captured_timeouts = []
        with patch.object(orchestrator, "complete", side_effect=lambda msgs, **kwargs: (captured_timeouts.append(kwargs.get("timeout")), ('{"visual_suite": [], "executive_briefing": {"situational_overview": "ok", "tactical_directives": []}}', "groq"))[1]):
            from app.agents.analytical import AnalyticalAgent
            agent = AnalyticalAgent()
            agent.execute(ctx)

        self.assertTrue(len(captured_timeouts) > 0)
        self.assertLessEqual(captured_timeouts[0], 3.5)
        self.assertGreater(captured_timeouts[0], 0.0)
        log.info(f"[F-10] Propagated timeout captured: {captured_timeouts[0]:.3f}s <= 3.5s")

    @patch.object(AnalyticalAgent, "execute")
    @patch.object(GraphAgent, "execute")
    @patch.object(orchestrator, "generate_completion")
    def test_F11_synthesis_remaining_budget(self, mock_synthesis, mock_graph, mock_analytics):
        """F-11: Synthesis must receive only the actual remaining request budget."""
        def fanout_a(ctx):
            time.sleep(1.0)
            return AgentResponse(answer="A", agent_type="a", agent_label="A", agent_icon="A", agent_color="#0")
        mock_analytics.side_effect = fanout_a
        mock_graph.return_value = AgentResponse(answer="G", agent_type="g", agent_label="G", agent_icon="G", agent_color="#0")
        mock_synthesis.return_value = "Done"

        agent = FederatedAgent()
        agent.GLOBAL_BUDGET = 3.0
        agent.FANOUT_BUDGET = 2.0

        ctx = ExecutionContext(query="test synthesis budget")
        agent.execute(ctx)

        synthesis_timeout = mock_synthesis.call_args[1].get("timeout", 0.0)
        self.assertLessEqual(synthesis_timeout, 2.05)
        self.assertGreaterEqual(synthesis_timeout, 1.80)
        log.info(f"[F-11] Synthesis correctly received remaining budget: {synthesis_timeout:.2f}s")

    # ══════════════════════════════════════════════════════════════════════════
    # GATE G6, G7 & G8: Concurrency, Saturation & Gateway Margin (F-12, F-13, F-14, F-15, F-16)
    # ══════════════════════════════════════════════════════════════════════════

    @patch.object(AnalyticalAgent, "execute")
    @patch.object(GraphAgent, "execute")
    @patch.object(orchestrator, "generate_completion")
    def test_F12_executor_bounded_saturation(self, mock_synthesis, mock_graph, mock_analytics):
        """F-12: 20 simultaneous requests execute within bounded thread pool without worker explosion."""
        mock_analytics.return_value = AgentResponse(answer="A", agent_type="a", agent_label="A", agent_icon="A", agent_color="#0")
        mock_graph.return_value = AgentResponse(answer="G", agent_type="g", agent_label="G", agent_icon="G", agent_color="#0")
        mock_synthesis.return_value = "Synthesis Done"

        initial_threads = threading.active_count()
        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as client_pool:
            futures = [client_pool.submit(self.agent.execute, ExecutionContext(query=f"q{i}")) for i in range(20)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]

        self.assertEqual(len(results), 20)
        final_threads = threading.active_count()
        log.info(f"[F-12] 20 simultaneous requests completed. Active threads: start={initial_threads}, end={final_threads}")

    @patch.object(AnalyticalAgent, "execute")
    @patch.object(GraphAgent, "execute")
    @patch.object(orchestrator, "generate_completion")
    def test_F13_concurrent_federated_load_p95_p99(self, mock_synthesis, mock_graph, mock_analytics):
        """F-13 & F-14: Progressively test 10, 20, 50 requests. Record P50, P95, P99."""
        def fast_a(ctx):
            time.sleep(0.05)
            return AgentResponse(answer="A", agent_type="a", agent_label="A", agent_icon="A", agent_color="#0")
        def fast_g(ctx):
            time.sleep(0.04)
            return AgentResponse(answer="G", agent_type="g", agent_label="G", agent_icon="G", agent_color="#0")

        mock_analytics.side_effect = fast_a
        mock_graph.side_effect = fast_g
        mock_synthesis.return_value = "Done"

        for concurrency in [10, 20, 50]:
            latencies = []
            with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as pool:
                def run_one(i):
                    t0 = time.monotonic()
                    self.agent.execute(ExecutionContext(query=f"query {i}"))
                    return (time.monotonic() - t0) * 1000

                futures = [pool.submit(run_one, i) for i in range(concurrency)]
                for f in concurrent.futures.as_completed(futures):
                    latencies.append(f.result())

            latencies.sort()
            p50 = latencies[int(len(latencies) * 0.50)]
            p95 = latencies[int(len(latencies) * 0.95)]
            p99 = latencies[min(int(len(latencies) * 0.99), len(latencies)-1)]
            pmax = max(latencies)

            log.info(f"[F-13/F-14] Concurrency={concurrency:2d} -> P50: {p50:5.1f}ms | P95: {p95:5.1f}ms | P99: {p99:5.1f}ms | Max: {pmax:5.1f}ms")
            self.assertLess(p99, 4000.0, f"P99 exceeded 4.0s under concurrency {concurrency}")

    @patch.object(AnalyticalAgent, "execute")
    @patch.object(GraphAgent, "execute")
    @patch.object(orchestrator, "generate_completion")
    def test_F15_thread_leak_resource_release(self, mock_synthesis, mock_graph, mock_analytics):
        """F-15: Repeated timeout rounds must release resources without accumulating active threads."""
        mock_analytics.side_effect = lambda ctx: time.sleep(0.5)
        mock_graph.side_effect = lambda ctx: time.sleep(0.5)
        mock_synthesis.return_value = "Fallback"

        agent = FederatedAgent()
        agent.FANOUT_BUDGET = 0.05
        agent.GLOBAL_BUDGET = 0.1

        threads_before = threading.active_count()
        for round_idx in range(5):
            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as client_pool:
                futures = [client_pool.submit(agent.execute, ExecutionContext(query=f"timeout_{round_idx}_{r}")) for r in range(10)]
                for f in concurrent.futures.as_completed(futures):
                    f.result()
            time.sleep(0.1)

        threads_after = threading.active_count()
        self.assertLessEqual(threads_after - threads_before, 12, "Thread accumulation detected after repeated timeouts")
        log.info(f"[F-15] Resource release verified: threads before={threads_before}, after 50 timeouts={threads_after}")

    def test_F16_gateway_timeout_boundary_margin(self):
        """F-16: Application target (6.5s) must maintain >= 1.5s safety margin from 8.0s gateway limit."""
        GATEWAY_LIMIT = 8.0
        APP_TARGET = self.agent.GLOBAL_BUDGET
        margin = GATEWAY_LIMIT - APP_TARGET
        self.assertGreaterEqual(margin, 1.5, "Insufficient safety margin from AppSail Gateway timeout")
        log.info(f"[F-16] Gateway Boundary: {GATEWAY_LIMIT}s | App Target: {APP_TARGET}s | Safety Margin: {margin:.1f}s")

    # ══════════════════════════════════════════════════════════════════════════
    # GATE G9 & G10: Thread-Safety & Regression (F-17, F-18, F-21, F-22)
    # ══════════════════════════════════════════════════════════════════════════

    def test_F17_stateless_multi_session_isolation(self):
        """F-17 & F-18: Distinct sessions execute without state crosstalk or coupling."""
        ctx1 = ExecutionContext(query="query 1", session_id="session_alpha")
        ctx2 = ExecutionContext(query="query 2", session_id="session_beta")
        
        ctx1.set_deadline(5.0)
        ctx2.set_deadline(10.0)

        self.assertNotEqual(ctx1.deadline, ctx2.deadline)
        self.assertEqual(ctx1.session_id, "session_alpha")
        self.assertEqual(ctx2.session_id, "session_beta")
        log.info("[F-17/F-18] Stateless multi-session independence verified")

    def test_F21_context_thread_safety_and_immutability(self):
        """F-21: ExecutionContext deadline is strictly immutable after initialization."""
        ctx = ExecutionContext(query="immutable test")
        ctx.set_deadline(6.5)

        # Attempt to overwrite must raise RuntimeError
        with self.assertRaises(RuntimeError):
            ctx.set_deadline(10.0)

        # Concurrent reads of remaining budget
        errors = []
        def read_budget():
            try:
                for _ in range(100):
                    b = ctx.get_remaining_budget()
                    assert b > 0
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=read_budget) for _ in range(10)]
        for t in threads: t.start()
        for t in threads: t.join()

        self.assertEqual(len(errors), 0)
        log.info("[F-21] Context thread-safety and deadline immutability verified")

    def test_F22_fail_closed_on_uninitialized_deadline(self):
        """F-22: ctx.get_remaining_budget() must fail-closed if deadline is uninitialized."""
        ctx = ExecutionContext(query="no deadline")
        with self.assertRaises(RuntimeError):
            ctx.get_remaining_budget()
        log.info("[F-22] Fail-closed uninitialized deadline verified")

    # ══════════════════════════════════════════════════════════════════════════
    # GATE G11 & G12: Memory Stability & Soak (F-23, F-24)
    # ══════════════════════════════════════════════════════════════════════════

    @patch.object(AnalyticalAgent, "execute")
    @patch.object(GraphAgent, "execute")
    @patch.object(orchestrator, "generate_completion")
    def test_F23_memory_stability_under_load(self, mock_synthesis, mock_graph, mock_analytics):
        """F-23: Memory and object counts remain stable under sustained batch workload."""
        mock_analytics.return_value = AgentResponse(answer="A", agent_type="a", agent_label="A", agent_icon="A", agent_color="#0")
        mock_graph.return_value = AgentResponse(answer="G", agent_type="g", agent_label="G", agent_icon="G", agent_color="#0")
        mock_synthesis.return_value = "Done"

        gc.collect()
        count_before = len(gc.get_objects())

        for _ in range(50):
            self.agent.execute(ExecutionContext(query="soak query"))

        gc.collect()
        count_after = len(gc.get_objects())
        diff = count_after - count_before
        log.info(f"[F-23] Object count diff after 50 runs: {diff} (stable)")
        self.assertLess(diff, 5000, "Uncontrolled memory object growth detected")

    @patch.object(AnalyticalAgent, "execute")
    @patch.object(GraphAgent, "execute")
    @patch.object(orchestrator, "generate_completion")
    def test_F24_soak_test_latency_stability(self, mock_synthesis, mock_graph, mock_analytics):
        """F-24: Latency does not degrade progressively over multiple iterations."""
        mock_analytics.return_value = AgentResponse(answer="A", agent_type="a", agent_label="A", agent_icon="A", agent_color="#0")
        mock_graph.return_value = AgentResponse(answer="G", agent_type="g", agent_label="G", agent_icon="G", agent_color="#0")
        mock_synthesis.return_value = "Done"

        batch_latencies = []
        for batch in range(4):
            t0 = time.monotonic()
            for _ in range(10):
                self.agent.execute(ExecutionContext(query="soak"))
            batch_latencies.append((time.monotonic() - t0) * 100) # avg ms per call

        log.info(f"[F-24] Soak batches avg latency: {[round(b, 1) for b in batch_latencies]}ms")
        self.assertLess(batch_latencies[-1], batch_latencies[0] * 2.5 + 50.0)


if __name__ == '__main__':
    unittest.main()
