# .NET Performance Reference

Provides async execution, EF Core query optimization, and memory efficiency rules for **Performance Review Agent** (`skill-eng-performance`).

---

## Actionable Technology Rules

### DOTNET-PERF-001: Sync-Over-Async Blocking & Thread Pool Starvation
- **Applies To**: ASP.NET Core controllers, MediatR handlers, background services.
- **Behavior**: Calling `.Result`, `.Wait()`, or `.GetAwaiter().GetResult()` blocks thread pool threads, leading to starvation under load.
- **Inspect**: Synchronous methods or endpoints calling `.GetAwaiter().GetResult()` or `.Result` on async Tasks.
- **Violation**: `var order = _orderService.GetOrderAsync(id).GetAwaiter().GetResult(); // Blocks thread pool thread!`
- **Evidence**: Call site executing `.Result`, `.Wait()`, or `.GetAwaiter().GetResult()` on a `Task`/`ValueTask`.
- **False Positives**: Main entry points in legacy CLI tools or completed tasks wrapped in `Task.FromResult()`.
- **Remediation**: Make method `async Task<IActionResult>` and `await` the asynchronous task.
- **Engineering Skill Map**: `PERF01`, `PERF03`

---

### DOTNET-PERF-002: EF Core N+1 Queries & Tracking Overhead
- **Applies To**: EF Core queries, LINQ data access, `DbContext` tracking.
- **Behavior**: Omitting `.AsNoTracking()` in read endpoints adds memory overhead; executing queries inside loops triggers N+1 SQL calls.
- **Inspect**: Read-only endpoints returning tracked entities and LINQ queries/Count calls executed inside `foreach` loops.
- **Violation**:
  ```csharp
  var users = await _db.Users.ToListAsync(); // Tracked query in read endpoint
  foreach (var u in users) { var count = await _db.Orders.CountAsync(o => o.UserId == u.Id); } // N+1 DB calls
  ```
- **Evidence**: LINQ query executing SQL inside a `foreach`/`for` loop or missing `.AsNoTracking()` on read queries.
- **False Positives**: Entities fetched for immediate update/delete within an active transaction.
- **Remediation**: Use `.AsNoTracking()` and project queries into DTOs before looping (`Select(u => ...)`).
- **Engineering Skill Map**: `PERF02`, `PERF04`

---

### DOTNET-PERF-003: HttpClient Direct Instantiation & Socket Exhaustion
- **Applies To**: Outbound REST integrations, `HttpClient`, `IHttpClientFactory`.
- **Behavior**: Instantiating `new HttpClient()` per request exhausts OS socket descriptors (`TIME_WAIT` state) under high load.
- **Inspect**: Local method variables declaring `using var client = new HttpClient();`.
- **Violation**: `using var client = new HttpClient(); var data = await client.GetFromJsonAsync<Catalog>(url);`
- **Evidence**: Instantiation of `new HttpClient()` inside method calls or transient services.
- **False Positives**: Clients registered via `builder.Services.AddHttpClient()` or short-lived console scripts.
- **Remediation**: Inject `IHttpClientFactory` or use typed clients registered via `AddHttpClient<TClient>()`.
- **Engineering Skill Map**: `PERF05`, `PERF08`

---

### DOTNET-PERF-004: Large Object Heap (LOH) Allocations & String Concatenation
- **Applies To**: Byte buffers, string manipulation, `Span<T>`, `ArrayPool<T>`.
- **Behavior**: Allocations >85,000 bytes or repeated string concatenation in loops land on LOH, causing full Gen2 GC pauses.
- **Inspect**: String concatenation (`str += item`) inside loops and large unpooled array allocations (`new byte[100000]`).
- **Violation**: `string csv = ""; foreach (var log in logs) { csv += $"{log.Id},{log.Msg}\n"; } // GC pressure`
- **Evidence**: String concatenation using `+=` inside loops or large unpooled byte array allocations.
- **False Positives**: Fixed string concatenation of 2–3 small literals outside loops.
- **Remediation**: Use `StringBuilder` or `Span<char>` / `ArrayPool<T>.Shared`.
- **Engineering Skill Map**: `PERF06`, `PERF09`

---

### DOTNET-PERF-005: EF Core Split Queries & SaveChanges Batching
- **Applies To**: EF Core multi-collection `Include()` queries, bulk updates, `SaveChangesAsync()`.
- **Behavior**: Joining multiple collection `Include()` branches causes Cartesian explosion; calling `SaveChangesAsync()` in loops executes N transactions.
- **Inspect**: Queries with multiple collection `.Include()` calls missing `.AsSplitQuery()` and `SaveChangesAsync()` inside loops.
- **Violation**: `foreach (var u in updates) { var p = await _db.Products.FindAsync(u.Id); p.Price = u.Price; await _db.SaveChangesAsync(); }`
- **Evidence**: `await _dbContext.SaveChangesAsync()` called inside a `for` or `foreach` loop.
- **False Positives**: Isolated updates requiring independent transaction boundaries per item.
- **Remediation**: Batch entity updates and call `SaveChangesAsync()` once outside the loop, or use EF Core 7+ `ExecuteUpdateAsync()`.
- **Engineering Skill Map**: `PERF02`, `PERF07`

---

### DOTNET-PERF-006: BackgroundService Unbounded Channels & Queue Limits
- **Applies To**: `.NET BackgroundService`, `Channel<T>`, background workers.
- **Behavior**: Using `Channel.CreateUnbounded<T>()` in high-throughput consumers allows infinite memory growth and OOM crashes.
- **Inspect**: Instantiation of `Channel.CreateUnbounded<T>()` in event queues or background workers.
- **Violation**: `private readonly Channel<WorkItem> _channel = Channel.CreateUnbounded<WorkItem>(); // Memory leak under producer pressure`
- **Evidence**: `Channel.CreateUnbounded<T>()` in event queue mechanisms lacking backpressure bounds.
- **False Positives**: Low-throughput queues protected by upstream rate limiters.
- **Remediation**: Use `Channel.CreateBounded<T>(capacity)` with `BoundedChannelFullMode.Wait`.
- **Engineering Skill Map**: `PERF03`, `PERF10`
