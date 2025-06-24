"""
Performance benchmarks for Letta MCP Server
"""

import os
import pytest
import asyncio
import time
import statistics
from typing import List
from fastmcp import Client

from letta_mcp.server import LettaMCPServer


# Mark all tests in this module as performance tests
pytestmark = pytest.mark.skipif(
    not os.getenv("RUN_PERFORMANCE_TESTS", "").lower() in ("1", "true", "yes"),
    reason="Performance tests require RUN_PERFORMANCE_TESTS=1"
)


class TestResponseTimeBenchmarks:
    """Benchmark response times for various operations"""
    
    @pytest.mark.asyncio
    async def test_health_check_response_time(self, real_client):
        """Benchmark health check response time"""
        times = []
        num_iterations = 10
        
        for _ in range(num_iterations):
            start_time = time.perf_counter()
            
            await real_client.call_tool("letta_health_check", {})
            
            end_time = time.perf_counter()
            times.append(end_time - start_time)
        
        # Calculate statistics
        avg_time = statistics.mean(times)
        median_time = statistics.median(times)
        min_time = min(times)
        max_time = max(times)
        std_dev = statistics.stdev(times) if len(times) > 1 else 0
        
        print(f"\nHealth Check Performance:")
        print(f"  Average: {avg_time:.3f}s")
        print(f"  Median:  {median_time:.3f}s")
        print(f"  Min:     {min_time:.3f}s")
        print(f"  Max:     {max_time:.3f}s")
        print(f"  Std Dev: {std_dev:.3f}s")
        
        # Performance assertions
        assert avg_time < 2.0, f"Average health check time too slow: {avg_time:.3f}s"
        assert max_time < 5.0, f"Maximum health check time too slow: {max_time:.3f}s"
    
    @pytest.mark.asyncio
    async def test_list_agents_response_time(self, real_client):
        """Benchmark list agents response time"""
        times = []
        num_iterations = 5
        
        for _ in range(num_iterations):
            start_time = time.perf_counter()
            
            await real_client.call_tool("letta_list_agents", {"limit": 10})
            
            end_time = time.perf_counter()
            times.append(end_time - start_time)
        
        avg_time = statistics.mean(times)
        max_time = max(times)
        
        print(f"\nList Agents Performance:")
        print(f"  Average: {avg_time:.3f}s")
        print(f"  Max:     {max_time:.3f}s")
        
        # Performance assertions
        assert avg_time < 3.0, f"Average list agents time too slow: {avg_time:.3f}s"
        assert max_time < 8.0, f"Maximum list agents time too slow: {max_time:.3f}s"
    
    @pytest.mark.asyncio
    async def test_get_agent_response_time(self, real_client):
        """Benchmark get agent details response time"""
        agent_id = "agent-01c2ef52-be32-401d-8d8f-edc561b39cbe"
        times = []
        num_iterations = 5
        
        for _ in range(num_iterations):
            start_time = time.perf_counter()
            
            await real_client.call_tool("letta_get_agent", {"agent_id": agent_id})
            
            end_time = time.perf_counter()
            times.append(end_time - start_time)
        
        avg_time = statistics.mean(times)
        max_time = max(times)
        
        print(f"\nGet Agent Performance:")
        print(f"  Average: {avg_time:.3f}s")
        print(f"  Max:     {max_time:.3f}s")
        
        # Performance assertions
        assert avg_time < 2.5, f"Average get agent time too slow: {avg_time:.3f}s"
        assert max_time < 6.0, f"Maximum get agent time too slow: {max_time:.3f}s"
    
    @pytest.mark.asyncio
    async def test_memory_operations_response_time(self, real_client):
        """Benchmark memory operations response time"""
        agent_id = "agent-01c2ef52-be32-401d-8d8f-edc561b39cbe"
        
        # Test get memory
        start_time = time.perf_counter()
        await real_client.call_tool("letta_get_memory", {"agent_id": agent_id})
        get_memory_time = time.perf_counter() - start_time
        
        print(f"\nMemory Operations Performance:")
        print(f"  Get Memory: {get_memory_time:.3f}s")
        
        # Performance assertions
        assert get_memory_time < 3.0, f"Get memory time too slow: {get_memory_time:.3f}s"


class TestThroughputBenchmarks:
    """Benchmark throughput for concurrent operations"""
    
    @pytest.mark.asyncio
    async def test_concurrent_health_checks(self, real_client):
        """Benchmark concurrent health check throughput"""
        num_concurrent = 10
        
        start_time = time.perf_counter()
        
        # Execute concurrent health checks
        tasks = [
            real_client.call_tool("letta_health_check", {})
            for _ in range(num_concurrent)
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        end_time = time.perf_counter()
        total_time = end_time - start_time
        
        # Count successful requests
        successful = sum(1 for r in results if not isinstance(r, Exception))
        
        throughput = successful / total_time
        avg_time_per_request = total_time / successful if successful > 0 else float('inf')
        
        print(f"\nConcurrent Health Checks:")
        print(f"  Concurrent requests: {num_concurrent}")
        print(f"  Successful: {successful}")
        print(f"  Total time: {total_time:.3f}s")
        print(f"  Throughput: {throughput:.2f} requests/second")
        print(f"  Avg time per request: {avg_time_per_request:.3f}s")
        
        # Performance assertions
        assert successful >= num_concurrent * 0.8, f"Too many failed requests: {successful}/{num_concurrent}"
        assert throughput >= 2.0, f"Throughput too low: {throughput:.2f} requests/second"
    
    @pytest.mark.asyncio
    async def test_mixed_operation_throughput(self, real_client):
        """Benchmark throughput with mixed operations"""
        agent_id = "agent-01c2ef52-be32-401d-8d8f-edc561b39cbe"
        
        # Create mixed workload
        tasks = [
            real_client.call_tool("letta_health_check", {}),
            real_client.call_tool("letta_list_agents", {"limit": 5}),
            real_client.call_tool("letta_get_agent", {"agent_id": agent_id}),
            real_client.call_tool("letta_get_memory", {"agent_id": agent_id}),
            real_client.call_tool("letta_list_tools", {}),
        ]
        
        start_time = time.perf_counter()
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        end_time = time.perf_counter()
        total_time = end_time - start_time
        
        successful = sum(1 for r in results if not isinstance(r, Exception))
        
        print(f"\nMixed Operations Throughput:")
        print(f"  Operations: {len(tasks)}")
        print(f"  Successful: {successful}")
        print(f"  Total time: {total_time:.3f}s")
        print(f"  Operations per second: {successful/total_time:.2f}")
        
        # Should complete mixed operations efficiently
        assert successful >= len(tasks) * 0.8
        assert total_time < 15.0, f"Mixed operations took too long: {total_time:.3f}s"


class TestMemoryUsageBenchmarks:
    """Benchmark memory usage characteristics"""
    
    @pytest.mark.asyncio
    async def test_server_memory_footprint(self, real_server):
        """Test server memory footprint"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        
        # Measure initial memory
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Create multiple clients and perform operations
        clients = []
        for _ in range(5):
            client = Client(real_server)
            clients.append(client)
        
        # Perform operations with all clients
        for client in clients:
            async with client:
                await client.call_tool("letta_health_check", {})
        
        # Measure memory after operations
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        print(f"\nMemory Usage:")
        print(f"  Initial: {initial_memory:.1f} MB")
        print(f"  Final: {final_memory:.1f} MB")
        print(f"  Increase: {memory_increase:.1f} MB")
        
        # Memory increase should be reasonable
        assert memory_increase < 100, f"Memory increase too high: {memory_increase:.1f} MB"
        assert final_memory < 500, f"Total memory usage too high: {final_memory:.1f} MB"
    
    @pytest.mark.asyncio
    async def test_long_running_stability(self, real_client):
        """Test memory stability over extended operations"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        memory_samples = []
        
        # Take memory samples over time while performing operations
        for i in range(20):
            # Perform operation
            await real_client.call_tool("letta_health_check", {})
            
            # Sample memory
            memory_mb = process.memory_info().rss / 1024 / 1024
            memory_samples.append(memory_mb)
            
            # Small delay between operations
            await asyncio.sleep(0.1)
        
        # Analyze memory trend
        initial_memory = memory_samples[0]
        final_memory = memory_samples[-1]
        max_memory = max(memory_samples)
        memory_growth = final_memory - initial_memory
        
        print(f"\nLong-running Stability:")
        print(f"  Initial memory: {initial_memory:.1f} MB")
        print(f"  Final memory: {final_memory:.1f} MB")
        print(f"  Max memory: {max_memory:.1f} MB")
        print(f"  Memory growth: {memory_growth:.1f} MB")
        
        # Memory should remain stable (no significant leaks)
        assert memory_growth < 50, f"Memory growth indicates leak: {memory_growth:.1f} MB"
        assert max_memory < initial_memory + 100, f"Peak memory too high: {max_memory:.1f} MB"


class TestScalabilityBenchmarks:
    """Benchmark scalability characteristics"""
    
    @pytest.mark.asyncio
    async def test_increasing_load_performance(self, real_client):
        """Test performance under increasing load"""
        load_sizes = [1, 5, 10, 20]
        results = {}
        
        for load_size in load_sizes:
            start_time = time.perf_counter()
            
            # Create concurrent tasks
            tasks = [
                real_client.call_tool("letta_health_check", {})
                for _ in range(load_size)
            ]
            
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            
            end_time = time.perf_counter()
            total_time = end_time - start_time
            
            successful = sum(1 for r in responses if not isinstance(r, Exception))
            success_rate = successful / load_size
            throughput = successful / total_time
            
            results[load_size] = {
                'total_time': total_time,
                'success_rate': success_rate,
                'throughput': throughput
            }
            
            print(f"\nLoad {load_size}: {total_time:.3f}s, {success_rate:.1%} success, {throughput:.2f} req/s")
        
        # Analyze scalability
        for load_size, metrics in results.items():
            assert metrics['success_rate'] >= 0.8, f"Success rate too low at load {load_size}: {metrics['success_rate']:.1%}"
            
            # Throughput should scale reasonably
            if load_size > 1:
                expected_min_throughput = 1.0  # At least 1 request per second
                assert metrics['throughput'] >= expected_min_throughput, f"Throughput too low at load {load_size}: {metrics['throughput']:.2f}"
    
    @pytest.mark.asyncio
    async def test_sustained_load_performance(self, real_client):
        """Test performance under sustained load"""
        duration_seconds = 30
        request_interval = 0.2  # 5 requests per second
        
        start_time = time.time()
        response_times = []
        error_count = 0
        
        print(f"\nSustained load test for {duration_seconds} seconds...")
        
        while (time.time() - start_time) < duration_seconds:
            request_start = time.perf_counter()
            
            try:
                await real_client.call_tool("letta_health_check", {})
                request_end = time.perf_counter()
                response_times.append(request_end - request_start)
            except Exception as e:
                error_count += 1
                print(f"Request failed: {e}")
            
            await asyncio.sleep(request_interval)
        
        # Calculate statistics
        total_requests = len(response_times) + error_count
        success_rate = len(response_times) / total_requests if total_requests > 0 else 0
        
        if response_times:
            avg_response_time = statistics.mean(response_times)
            p95_response_time = sorted(response_times)[int(len(response_times) * 0.95)]
        else:
            avg_response_time = float('inf')
            p95_response_time = float('inf')
        
        print(f"\nSustained Load Results:")
        print(f"  Duration: {duration_seconds}s")
        print(f"  Total requests: {total_requests}")
        print(f"  Successful: {len(response_times)}")
        print(f"  Success rate: {success_rate:.1%}")
        print(f"  Average response time: {avg_response_time:.3f}s")
        print(f"  95th percentile: {p95_response_time:.3f}s")
        print(f"  Errors: {error_count}")
        
        # Performance assertions for sustained load
        assert success_rate >= 0.9, f"Success rate under sustained load too low: {success_rate:.1%}"
        assert avg_response_time < 3.0, f"Average response time under load too high: {avg_response_time:.3f}s"
        assert p95_response_time < 8.0, f"95th percentile response time too high: {p95_response_time:.3f}s"


class TestResourceUtilizationBenchmarks:
    """Benchmark resource utilization"""
    
    @pytest.mark.asyncio
    async def test_cpu_utilization_under_load(self, real_client):
        """Test CPU utilization under load"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        
        # Measure baseline CPU
        process.cpu_percent()  # First call to initialize
        await asyncio.sleep(1)
        baseline_cpu = process.cpu_percent()
        
        # Apply load and measure CPU
        start_time = time.perf_counter()
        
        tasks = [
            real_client.call_tool("letta_health_check", {})
            for _ in range(20)
        ]
        
        await asyncio.gather(*tasks, return_exceptions=True)
        
        end_time = time.perf_counter()
        load_duration = end_time - start_time
        
        # Measure CPU after load
        await asyncio.sleep(1)
        load_cpu = process.cpu_percent()
        
        print(f"\nCPU Utilization:")
        print(f"  Baseline: {baseline_cpu:.1f}%")
        print(f"  Under load: {load_cpu:.1f}%")
        print(f"  Load duration: {load_duration:.3f}s")
        
        # CPU usage should be reasonable
        assert load_cpu < 80, f"CPU usage too high under load: {load_cpu:.1f}%"
    
    @pytest.mark.asyncio
    async def test_connection_handling(self, real_server):
        """Test connection handling efficiency"""
        num_clients = 10
        clients = []
        
        start_time = time.perf_counter()
        
        # Create multiple concurrent clients
        for _ in range(num_clients):
            client = Client(real_server)
            clients.append(client)
        
        # Use all clients concurrently
        tasks = []
        for client in clients:
            async def use_client(c):
                async with c:
                    return await c.call_tool("letta_health_check", {})
            tasks.append(use_client(client))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        end_time = time.perf_counter()
        total_time = end_time - start_time
        
        successful = sum(1 for r in results if not isinstance(r, Exception))
        
        print(f"\nConnection Handling:")
        print(f"  Concurrent clients: {num_clients}")
        print(f"  Successful connections: {successful}")
        print(f"  Total time: {total_time:.3f}s")
        print(f"  Time per connection: {total_time/num_clients:.3f}s")
        
        # Connection handling should be efficient
        assert successful >= num_clients * 0.9, f"Too many connection failures: {successful}/{num_clients}"
        assert total_time < 10.0, f"Connection handling too slow: {total_time:.3f}s"