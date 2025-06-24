"""
Comparative Performance Benchmarks: Direct Letta SDK vs MCP Server
Test Agent 6: Performance Validator for Letta MCP Server Release
"""

import os
import pytest
import asyncio
import time
import statistics
import psutil
import threading
from typing import List, Dict, Any, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
import httpx

# Import both approaches
from letta_client import Letta  # Direct SDK
from fastmcp import Client
from letta_mcp.server import LettaMCPServer, LettaConfig

# Test configuration
TEST_API_KEY = "sk-let-MTVhMWI3YmYtNWEzMi00NDQ5LWJiMzAtNTAwZTE5NGQ4N2FjOmEwZjc1NzQwLTU2NjAtNDI0Ny04YThkLTVlM2MyZDNhYjUyNA=="
TEST_AGENT_ID = "agent-01c2ef52-be32-401d-8d8f-edc561b39cbe"
LETTA_BASE_URL = "https://api.letta.com"

# Performance test marker
pytestmark = pytest.mark.skipif(
    not os.getenv("RUN_PERFORMANCE_TESTS", "").lower() in ("1", "true", "yes"),
    reason="Performance tests require RUN_PERFORMANCE_TESTS=1"
)


class PerformanceMetrics:
    """Track performance metrics for comparison"""
    
    def __init__(self, name: str):
        self.name = name
        self.times: List[float] = []
        self.errors: List[str] = []
        self.memory_usage: List[float] = []
        
    def add_timing(self, duration: float):
        self.times.append(duration)
        
    def add_error(self, error: str):
        self.errors.append(error)
        
    def add_memory_sample(self, memory_mb: float):
        self.memory_usage.append(memory_mb)
        
    @property
    def avg_time(self) -> float:
        return statistics.mean(self.times) if self.times else float('inf')
    
    @property
    def median_time(self) -> float:
        return statistics.median(self.times) if self.times else float('inf')
    
    @property
    def min_time(self) -> float:
        return min(self.times) if self.times else float('inf')
    
    @property
    def max_time(self) -> float:
        return max(self.times) if self.times else float('inf')
    
    @property
    def std_dev(self) -> float:
        return statistics.stdev(self.times) if len(self.times) > 1 else 0.0
    
    @property
    def success_rate(self) -> float:
        total = len(self.times) + len(self.errors)
        return len(self.times) / total if total > 0 else 0.0
    
    @property
    def avg_memory(self) -> float:
        return statistics.mean(self.memory_usage) if self.memory_usage else 0.0
    
    def print_summary(self):
        print(f"\n{self.name} Performance Summary:")
        print(f"  Average time: {self.avg_time:.3f}s")
        print(f"  Median time:  {self.median_time:.3f}s")
        print(f"  Min time:     {self.min_time:.3f}s")
        print(f"  Max time:     {self.max_time:.3f}s")
        print(f"  Std deviation: {self.std_dev:.3f}s")
        print(f"  Success rate: {self.success_rate:.1%}")
        print(f"  Errors: {len(self.errors)}")
        print(f"  Avg memory:   {self.avg_memory:.1f} MB")


@pytest.fixture
def direct_letta_client():
    """Direct Letta SDK client for comparison"""
    return Letta(token=TEST_API_KEY)


@pytest.fixture
def mcp_server():
    """MCP Server instance for comparison"""
    config = LettaConfig(
        api_key=TEST_API_KEY,
        base_url=LETTA_BASE_URL,
        timeout=30.0,
        max_retries=3
    )
    return LettaMCPServer(config)


@pytest.fixture
async def mcp_client(mcp_server):
    """MCP Client instance"""
    async with Client(mcp_server) as client:
        yield client


class TestComparativePerformance:
    """Compare Direct SDK vs MCP Server performance"""
    
    def get_memory_usage(self) -> float:
        """Get current memory usage in MB"""
        process = psutil.Process(os.getpid())
        return process.memory_info().rss / 1024 / 1024
    
    async def time_operation(self, operation, *args, **kwargs) -> Tuple[float, Any, str]:
        """Time an operation and return (duration, result, error)"""
        start_time = time.perf_counter()
        error = ""
        result = None
        
        try:
            if asyncio.iscoroutinefunction(operation):
                result = await operation(*args, **kwargs)
            else:
                result = operation(*args, **kwargs)
        except Exception as e:
            error = str(e)
            
        duration = time.perf_counter() - start_time
        return duration, result, error
    
    @pytest.mark.asyncio
    async def test_agent_listing_performance(self, direct_letta_client, mcp_client):
        """Compare agent listing performance: Direct SDK vs MCP"""
        num_iterations = 10
        
        # Metrics tracking
        direct_metrics = PerformanceMetrics("Direct SDK - List Agents")
        mcp_metrics = PerformanceMetrics("MCP Server - List Agents")
        
        print(f"\n{'='*60}")
        print("AGENT LISTING PERFORMANCE COMPARISON")
        print(f"{'='*60}")
        
        # Test Direct SDK
        for i in range(num_iterations):
            memory_before = self.get_memory_usage()
            
            duration, result, error = await self.time_operation(
                lambda: direct_letta_client.agents.list(limit=10)
            )
            
            memory_after = self.get_memory_usage()
            
            if error:
                direct_metrics.add_error(error)
            else:
                direct_metrics.add_timing(duration)
                direct_metrics.add_memory_sample(memory_after - memory_before)
            
            # Small delay between requests
            await asyncio.sleep(0.1)
        
        # Test MCP Server
        for i in range(num_iterations):
            memory_before = self.get_memory_usage()
            
            duration, result, error = await self.time_operation(
                mcp_client.call_tool, "letta_list_agents", {"limit": 10}
            )
            
            memory_after = self.get_memory_usage()
            
            if error:
                mcp_metrics.add_error(error)
            else:
                mcp_metrics.add_timing(duration)
                mcp_metrics.add_memory_sample(memory_after - memory_before)
            
            await asyncio.sleep(0.1)
        
        # Print results
        direct_metrics.print_summary()
        mcp_metrics.print_summary()
        
        # Calculate improvement
        if direct_metrics.avg_time > 0 and mcp_metrics.avg_time > 0:
            improvement = direct_metrics.avg_time / mcp_metrics.avg_time
            print(f"\nPerformance Improvement: {improvement:.2f}x")
            print(f"README Claim: 4x faster")
            print(f"Validation: {'✅ PASSED' if improvement >= 3.0 else '❌ FAILED'}")
        
        # Assertions
        assert direct_metrics.success_rate >= 0.8, "Direct SDK success rate too low"
        assert mcp_metrics.success_rate >= 0.8, "MCP Server success rate too low"
        assert mcp_metrics.avg_time < direct_metrics.avg_time * 1.2, "MCP should be comparable or faster"
    
    @pytest.mark.asyncio
    async def test_agent_details_performance(self, direct_letta_client, mcp_client):
        """Compare agent details retrieval performance"""
        num_iterations = 8
        
        direct_metrics = PerformanceMetrics("Direct SDK - Get Agent")
        mcp_metrics = PerformanceMetrics("MCP Server - Get Agent")
        
        print(f"\n{'='*60}")
        print("AGENT DETAILS PERFORMANCE COMPARISON")
        print(f"{'='*60}")
        
        # Test Direct SDK
        for i in range(num_iterations):
            duration, result, error = await self.time_operation(
                lambda: direct_letta_client.agents.get(agent_id=TEST_AGENT_ID)
            )
            
            if error:
                direct_metrics.add_error(error)
            else:
                direct_metrics.add_timing(duration)
            
            await asyncio.sleep(0.1)
        
        # Test MCP Server  
        for i in range(num_iterations):
            duration, result, error = await self.time_operation(
                mcp_client.call_tool, "letta_get_agent", {"agent_id": TEST_AGENT_ID}
            )
            
            if error:
                mcp_metrics.add_error(error)
            else:
                mcp_metrics.add_timing(duration)
            
            await asyncio.sleep(0.1)
        
        direct_metrics.print_summary()
        mcp_metrics.print_summary()
        
        if direct_metrics.avg_time > 0 and mcp_metrics.avg_time > 0:
            improvement = direct_metrics.avg_time / mcp_metrics.avg_time
            print(f"\nPerformance Improvement: {improvement:.2f}x")
    
    @pytest.mark.asyncio
    async def test_memory_operations_performance(self, direct_letta_client, mcp_client):
        """Compare memory operations performance"""
        num_iterations = 6
        
        direct_metrics = PerformanceMetrics("Direct SDK - Memory Operations")
        mcp_metrics = PerformanceMetrics("MCP Server - Memory Operations")
        
        print(f"\n{'='*60}")
        print("MEMORY OPERATIONS PERFORMANCE COMPARISON") 
        print(f"{'='*60}")
        
        # Test Direct SDK memory retrieval
        for i in range(num_iterations):
            duration, result, error = await self.time_operation(
                lambda: direct_letta_client.agents.core_memory.get(agent_id=TEST_AGENT_ID)
            )
            
            if error:
                direct_metrics.add_error(error)
            else:
                direct_metrics.add_timing(duration)
            
            await asyncio.sleep(0.2)
        
        # Test MCP Server memory retrieval
        for i in range(num_iterations):
            duration, result, error = await self.time_operation(
                mcp_client.call_tool, "letta_get_memory", {"agent_id": TEST_AGENT_ID}
            )
            
            if error:
                mcp_metrics.add_error(error)
            else:
                mcp_metrics.add_timing(duration)
            
            await asyncio.sleep(0.2)
        
        direct_metrics.print_summary()
        mcp_metrics.print_summary()
        
        if direct_metrics.avg_time > 0 and mcp_metrics.avg_time > 0:
            improvement = direct_metrics.avg_time / mcp_metrics.avg_time
            print(f"\nPerformance Improvement: {improvement:.2f}x")
            print(f"README Claim: 3.7x faster")
            print(f"Validation: {'✅ PASSED' if improvement >= 2.5 else '❌ FAILED'}")
    
    @pytest.mark.asyncio
    async def test_messaging_performance(self, direct_letta_client, mcp_client):
        """Compare message sending performance"""
        num_iterations = 4  # Fewer iterations for messaging due to cost
        test_message = "Quick performance test - please respond briefly."
        
        direct_metrics = PerformanceMetrics("Direct SDK - Send Message")
        mcp_metrics = PerformanceMetrics("MCP Server - Send Message")
        
        print(f"\n{'='*60}")
        print("MESSAGING PERFORMANCE COMPARISON")
        print(f"{'='*60}")
        
        # Test Direct SDK messaging
        for i in range(num_iterations):
            duration, result, error = await self.time_operation(
                lambda: direct_letta_client.agents.messages.create(
                    agent_id=TEST_AGENT_ID,
                    messages=[{"role": "user", "content": test_message}]
                )
            )
            
            if error:
                direct_metrics.add_error(error)
            else:
                direct_metrics.add_timing(duration)
            
            # Longer delay for message operations
            await asyncio.sleep(2.0)
        
        # Test MCP Server messaging
        for i in range(num_iterations):
            duration, result, error = await self.time_operation(
                mcp_client.call_tool, "letta_send_message", {
                    "agent_id": TEST_AGENT_ID,
                    "message": test_message
                }
            )
            
            if error:
                mcp_metrics.add_error(error)
            else:
                mcp_metrics.add_timing(duration)
            
            await asyncio.sleep(2.0)
        
        direct_metrics.print_summary()
        mcp_metrics.print_summary()
        
        if direct_metrics.avg_time > 0 and mcp_metrics.avg_time > 0:
            improvement = direct_metrics.avg_time / mcp_metrics.avg_time
            print(f"\nPerformance Improvement: {improvement:.2f}x")
            print(f"README Claim: 15% faster (1.15x)")
            print(f"Validation: {'✅ PASSED' if improvement >= 1.10 else '❌ FAILED'}")


class TestConnectionPoolingBenefits:
    """Test connection pooling performance benefits"""
    
    @pytest.mark.asyncio
    async def test_concurrent_operations_scaling(self, mcp_client):
        """Test how MCP server handles concurrent operations"""
        print(f"\n{'='*60}")
        print("CONNECTION POOLING PERFORMANCE TEST")
        print(f"{'='*60}")
        
        concurrent_levels = [1, 5, 10, 20]
        results = {}
        
        for concurrent_count in concurrent_levels:
            start_time = time.perf_counter()
            
            # Create concurrent health check tasks
            tasks = [
                mcp_client.call_tool("letta_health_check", {})
                for _ in range(concurrent_count)
            ]
            
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            
            end_time = time.perf_counter()
            total_time = end_time - start_time
            
            successful = sum(1 for r in responses if not isinstance(r, Exception))
            throughput = successful / total_time
            
            results[concurrent_count] = {
                'total_time': total_time,
                'successful': successful,
                'throughput': throughput,
                'success_rate': successful / concurrent_count
            }
            
            print(f"Concurrent {concurrent_count:2d}: {total_time:.3f}s, "
                  f"{successful:2d}/{concurrent_count} success, {throughput:.1f} req/s")
        
        # Validate scaling characteristics
        baseline_throughput = results[1]['throughput']
        peak_throughput = max(r['throughput'] for r in results.values())
        scaling_factor = peak_throughput / baseline_throughput
        
        print(f"\nScaling Analysis:")
        print(f"  Baseline throughput (1 concurrent): {baseline_throughput:.2f} req/s")
        print(f"  Peak throughput: {peak_throughput:.2f} req/s")
        print(f"  Scaling factor: {scaling_factor:.2f}x")
        
        # Connection pooling should provide better than linear scaling
        assert scaling_factor >= 2.0, f"Poor scaling factor: {scaling_factor:.2f}x"
        
        # Success rates should remain high
        for level, metrics in results.items():
            assert metrics['success_rate'] >= 0.9, f"Low success rate at {level} concurrent: {metrics['success_rate']:.1%}"
    
    @pytest.mark.asyncio
    async def test_resource_efficiency_under_load(self, mcp_client):
        """Test resource efficiency under sustained load"""
        print(f"\n{'='*60}")
        print("RESOURCE EFFICIENCY UNDER LOAD")
        print(f"{'='*60}")
        
        duration_seconds = 20
        request_interval = 0.3  # ~3 requests per second
        
        process = psutil.Process(os.getpid())
        memory_samples = []
        cpu_samples = []
        response_times = []
        error_count = 0
        
        start_time = time.time()
        print(f"Running sustained load test for {duration_seconds} seconds...")
        
        while (time.time() - start_time) < duration_seconds:
            # Sample system resources
            memory_mb = process.memory_info().rss / 1024 / 1024
            cpu_percent = process.cpu_percent()
            memory_samples.append(memory_mb)
            cpu_samples.append(cpu_percent)
            
            # Make request
            request_start = time.perf_counter()
            try:
                await mcp_client.call_tool("letta_health_check", {})
                response_time = time.perf_counter() - request_start
                response_times.append(response_time)
            except Exception as e:
                error_count += 1
                print(f"Request failed: {e}")
            
            await asyncio.sleep(request_interval)
        
        # Analyze results
        if response_times:
            avg_response_time = statistics.mean(response_times)
            p95_response_time = sorted(response_times)[int(len(response_times) * 0.95)]
        else:
            avg_response_time = float('inf')
            p95_response_time = float('inf')
        
        avg_memory = statistics.mean(memory_samples) if memory_samples else 0
        peak_memory = max(memory_samples) if memory_samples else 0
        avg_cpu = statistics.mean(cpu_samples) if cpu_samples else 0
        peak_cpu = max(cpu_samples) if cpu_samples else 0
        
        total_requests = len(response_times) + error_count
        success_rate = len(response_times) / total_requests if total_requests > 0 else 0
        
        print(f"\nResource Efficiency Results:")
        print(f"  Total requests: {total_requests}")
        print(f"  Success rate: {success_rate:.1%}")
        print(f"  Average response time: {avg_response_time:.3f}s") 
        print(f"  95th percentile response time: {p95_response_time:.3f}s")
        print(f"  Average memory usage: {avg_memory:.1f} MB")
        print(f"  Peak memory usage: {peak_memory:.1f} MB")
        print(f"  Average CPU usage: {avg_cpu:.1f}%")
        print(f"  Peak CPU usage: {peak_cpu:.1f}%")
        
        # Performance assertions
        assert success_rate >= 0.95, f"Success rate too low: {success_rate:.1%}"
        assert avg_response_time < 2.0, f"Average response time too high: {avg_response_time:.3f}s"
        assert peak_memory < avg_memory + 50, f"Memory usage too variable: peak={peak_memory:.1f}, avg={avg_memory:.1f}"
        assert peak_cpu < 70, f"CPU usage too high: {peak_cpu:.1f}%"


class TestRealisticWorkloadScenarios:
    """Test realistic dealer/agent workload scenarios"""
    
    @pytest.mark.asyncio
    async def test_dealer_analysis_workflow(self, mcp_client):
        """Simulate realistic dealer analysis workflow"""
        print(f"\n{'='*60}")
        print("REALISTIC DEALER ANALYSIS WORKFLOW")
        print(f"{'='*60}")
        
        workflow_steps = [
            ("health_check", "letta_health_check", {}),
            ("get_agent", "letta_get_agent", {"agent_id": TEST_AGENT_ID}),
            ("get_memory", "letta_get_memory", {"agent_id": TEST_AGENT_ID}),
            ("list_tools", "letta_list_tools", {}),
            ("get_agent_tools", "letta_get_agent_tools", {"agent_id": TEST_AGENT_ID}),
        ]
        
        total_start_time = time.perf_counter()
        step_times = {}
        
        for step_name, tool_name, params in workflow_steps:
            step_start = time.perf_counter()
            
            try:
                result = await mcp_client.call_tool(tool_name, params)
                step_duration = time.perf_counter() - step_start
                step_times[step_name] = step_duration
                
                print(f"  {step_name}: {step_duration:.3f}s ✅")
                
            except Exception as e:
                step_duration = time.perf_counter() - step_start
                step_times[step_name] = step_duration
                print(f"  {step_name}: {step_duration:.3f}s ❌ ({str(e)[:50]})")
            
            # Small delay between steps
            await asyncio.sleep(0.1)
        
        total_duration = time.perf_counter() - total_start_time
        
        print(f"\nWorkflow Summary:")
        print(f"  Total workflow time: {total_duration:.3f}s")
        print(f"  Average step time: {statistics.mean(step_times.values()):.3f}s")
        print(f"  Slowest step: {max(step_times.values()):.3f}s")
        print(f"  Fastest step: {min(step_times.values()):.3f}s")
        
        # Workflow should complete efficiently
        assert total_duration < 10.0, f"Workflow too slow: {total_duration:.3f}s"
        assert max(step_times.values()) < 5.0, f"Slowest step too slow: {max(step_times.values()):.3f}s"
    
    @pytest.mark.asyncio
    async def test_multi_agent_scenario(self, mcp_client):
        """Test performance with multiple agent interactions"""
        print(f"\n{'='*60}")
        print("MULTI-AGENT INTERACTION SCENARIO")
        print(f"{'='*60}")
        
        # Simulate managing multiple agents (even if we only have one real agent)
        agent_operations = [
            ("agent_list", "letta_list_agents", {"limit": 20}),
            ("agent_details_1", "letta_get_agent", {"agent_id": TEST_AGENT_ID}),
            ("agent_memory_1", "letta_get_memory", {"agent_id": TEST_AGENT_ID}),
            ("tools_list", "letta_list_tools", {}),
            ("agent_tools_1", "letta_get_agent_tools", {"agent_id": TEST_AGENT_ID}),
        ]
        
        # Run operations concurrently to simulate real usage
        start_time = time.perf_counter()
        
        tasks = [
            mcp_client.call_tool(tool_name, params)
            for _, tool_name, params in agent_operations
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        end_time = time.perf_counter()
        total_time = end_time - start_time
        
        successful = sum(1 for r in results if not isinstance(r, Exception))
        failed = len(results) - successful
        
        print(f"\nMulti-Agent Scenario Results:")
        print(f"  Total operations: {len(agent_operations)}")
        print(f"  Successful: {successful}")
        print(f"  Failed: {failed}")
        print(f"  Total time: {total_time:.3f}s")
        print(f"  Operations per second: {successful/total_time:.2f}")
        print(f"  Average time per operation: {total_time/successful:.3f}s")
        
        # Multi-agent operations should be efficient
        assert successful >= len(agent_operations) * 0.8, f"Too many failures: {failed}/{len(agent_operations)}"
        assert total_time < 8.0, f"Multi-agent scenario too slow: {total_time:.3f}s"
        assert successful/total_time >= 1.0, f"Operations per second too low: {successful/total_time:.2f}"


if __name__ == "__main__":
    print("Letta MCP Server Performance Validation")
    print("Set RUN_PERFORMANCE_TESTS=1 to enable performance tests")