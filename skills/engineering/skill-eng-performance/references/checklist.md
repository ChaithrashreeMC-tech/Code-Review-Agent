# Performance Review Checklist & Detailed Rule Guidance

This reference provides detailed detection criteria, evidence requirements, false-positive
guidance, severity classification, remediation advice, and technology-specific adaptations
for all 14 engineering performance rules (PERF01–PERF14).

Use this guide during Step 4 of the Review Workflow in `SKILL.md`.

---

## Rule Disambiguation & Overlap Boundaries

To prevent duplicate findings for related symptoms, use these boundary principles:

| Overlap Pair | Primary Distinction | Guidance |
|---|---|---|
| **PERF01 vs. PERF07** | Blocking / sequential execution vs. concurrency control | Use **PERF01** when single-threaded I/O blocks an event loop or executes avoidable work sequentially. Use **PERF07** when independent operations could be executed in parallel or when concurrent execution lacks bounds (semaphores) or thread-safety. |
| **PERF02 vs. PERF08** | Database queries in loops vs. general computation/service calls | Use **PERF02** specifically for database ORM and query round trips in loops (N+1). Use **PERF08** for repeated external HTTP calls, redundant AI tool calls, repeated regex compilation, or duplicate in-memory calculations. |
| **PERF09 vs. PERF10** | Query plan and indexing vs. result volume and pagination | Use **PERF09** when the query itself has a poor execution plan (missing index, full scan, function on column). Use **PERF10** when the query lacks a `LIMIT`, returns unbounded rows, or uses deep `OFFSET` pagination. |
| **PERF11 vs. PERF14** | DOM rendering & virtualization vs. state subscription & updates | Use **PERF11** for large DOM node counts, missing virtualization, or expensive JSX renders. Use **PERF14** for overly broad store subscriptions, un-memoized selectors returning new references, or unthrottled state updates. |

---

## Detailed Rule Specifications

### PERF01 — Execution Efficiency

* **Objective & Scope:** Eliminate blocking operations, synchronous delays, and unneeded CPU work in request handlers, background jobs, and event-loop threads.
* **Detection Criteria:**
  - Synchronous I/O (file, network, DB) inside `async` routines without awaiting or offloading.
  - Blocking sleep (`time.sleep()`, `Thread.Sleep()`) on hot request paths.
  - Heavy CPU computations executed synchronously on an event-loop thread.
  - Long-running batch work executed inline in a user-facing HTTP request instead of deferred.
* **Evidence Requirements:** Visible synchronous call in an `async` context or hot path; observable latency impact inferable from call patterns.
* **False-Positive Guidance:** One-time startup or initialization routines; CLI scripts; bounded CPU work on tiny inputs; test setup/teardown code.
* **Severity Guidance:** Critical if blocking an event loop in a hot path; High if serializing operations that delay user-facing requests; Medium if repeated computation is bounded; Low on cold paths.
* **Remediation Guidance:** Use async equivalents (`httpx`, `asyncpg`), offload to worker pools (`run_in_executor`, `Task.Run`), or defer long tasks to background queues.
* **Technology Adaptation:**
  - *Python*: Replace `requests` with `httpx`; offload CPU work via `loop.run_in_executor()`.
  - *.NET/C#*: Avoid `.Result` and `.Wait()`; use `await` with `ConfigureAwait(false)`.
  - *Java*: Avoid blocking calls inside Project Reactor or RxJava pipelines.
  - *Node.js*: Avoid `fs.readFileSync` and blocking crypto methods in Express/Fastify routes.

---

### PERF02 — Data Access Efficiency

* **Objective & Scope:** Prevent unnecessary database round trips, N+1 query patterns, and unbatched data retrieval in ORMs, repositories, and data-access layers.
* **Detection Criteria:**
  - Database query or ORM access issued inside a loop over entities or IDs.
  - Lazy-loaded navigation properties traversed in loops without eager loading.
  - Multiple sequential queries that could be consolidated into a single `JOIN` or `IN (...)` query.
  - GraphQL resolvers fetching child records individually without DataLoader.
* **Evidence Requirements:** Code loop containing database access; unbounded or dynamically sized collection; lack of eager loading or batching in surrounding scope.
* **False-Positive Guidance:** Loops over small constant sets (1–3 items); per-item write operations where no batch API exists; access against a warmed in-memory cache.
* **Severity Guidance:** High if query count scales with unbounded collection size in user-facing endpoints; Medium if collection is bounded but non-trivial; Low in background batch jobs with relaxed SLAs.
* **Remediation Guidance:** Use eager loading (`selectinload`, `.Include()`, `JOIN FETCH`), batch with `WHERE id IN (...)`, or introduce DataLoader in GraphQL.
* **Technology Adaptation:**
  - *Python/SQLAlchemy*: Apply `joinedload()` or `selectinload()`; avoid lazy relationship access in loops.
  - *.NET/EF Core*: Add `.Include()` or `.ThenInclude()`; use projected queries via `.Select()`.
  - *Java/Hibernate*: Use `JOIN FETCH` in JPQL, `@BatchSize`, or `EntityGraph`.
  - *Node/Prisma*: Use `include` and `select`; batch lookups with `findMany({ where: { id: { in: ids } } })`.

---

### PERF03 — Memory and Resource Management

* **Objective & Scope:** Prevent unbounded memory accumulation, large object allocations, and resource leaks (connections, streams, file descriptors).
* **Detection Criteria:**
  - Reading entire files or response bodies into memory when streaming is feasible.
  - Materializing full database result sets in RAM before writing CSVs or exports.
  - Missing resource disposal (`with`, `using`, `try-with-resources`, `defer`).
  - Unbounded collection accumulation across iterations without size limits.
* **Evidence Requirements:** Unbounded read or collection append; missing disposal syntax; plausible scenario of large payload or high-frequency invocation.
* **False-Positive Guidance:** Small bounded configurations (< 4 KB); resources managed by dependency injection or framework lifecycle; explicit size-bounded buffers.
* **Severity Guidance:** Critical if unbounded user payloads cause server OOM under load; High for large unstreamed exports; Medium for inconsistent disposal; Low in small utilities.
* **Remediation Guidance:** Stream large payloads via generators or chunked transfers; enclose resources in deterministic disposal blocks; apply batch limits.
* **Technology Adaptation:**
  - *Python*: Use `yield_per()` and generators for streaming; wrap I/O in `with` statements.
  - *.NET/C#*: Use `IAsyncEnumerable<T>`, `Stream`, and `using` declarations.
  - *Java*: Use Java Streams with chunking; apply `try-with-resources`.
  - *Node.js*: Pipe streams with `pipeline()`; avoid `Buffer.concat()` on large streams.

---

### PERF04 — Caching Strategy

* **Objective & Scope:** Ensure caching is effectively applied for repeated, expensive computations and data retrievals, with proper TTL and invalidation semantics.
* **Detection Criteria:**
  - Repeated expensive queries or external API calls for static or slowly changing data without caching.
  - Cache entries created for mutable entities without a TTL or expiration policy.
  - Missing cache invalidation or eviction hooks on write/update paths.
  - Per-request cache initialization overhead that exceeds the cost of direct computation.
* **Evidence Requirements:** Visible expensive or high-frequency operation with stable inputs; missing cache key/TTL; or mutable cache entry lacking invalidation.
* **False-Positive Guidance:** Rapidly changing or user-personalized data; fast in-memory operations (< 1 ms); paths where cache consistency risk outweighs latency gain.
* **Severity Guidance:** High for hot endpoints querying slow databases without caching; Medium for missing TTL on mutable cached data; Low for cold administrative paths.
* **Remediation Guidance:** Introduce in-memory or distributed cache (Redis) with appropriate TTL; ensure write mutations invalidate corresponding cache keys.
* **Technology Adaptation:**
  - *Python*: Use `functools.lru_cache` for pure in-process functions; Redis with `ex=` TTL for distributed cache.
  - *.NET/C#*: Use `IMemoryCache` or `IDistributedCache` with sliding/absolute expirations.
  - *Java/Spring*: Apply `@Cacheable` and `@CacheEvict` with Caffeine or Redis.
  - *Node.js*: Use Redis or memory caches with explicit TTLs; configure HTTP `Cache-Control` headers.

---

### PERF05 — Timeouts and Resilience

* **Objective & Scope:** Guard external network calls, database queries, and asynchronous operations against indefinite hangs, resource exhaustion, and cascading failure.
* **Detection Criteria:**
  - HTTP clients, RPC clients, or database connections initialized without timeouts.
  - Retry loops lacking maximum attempt limits (`max_retries`) or exponential backoff.
  - Async waiting constructs (`asyncio.wait`, `Task.WhenAll`, `Promise.all`) without timeout wrappers or cancellation tokens.
  - LLM API calls executed without client timeouts or retry budgets.
* **Evidence Requirements:** External I/O call site visible in diff lacking timeout argument or surrounding timeout policy.
* **False-Positive Guidance:** Global client factory or middleware already enforcing timeouts; startup health checks intentionally polling until ready; internal in-memory waits.
* **Severity Guidance:** High if unbounded network call can exhaust thread/connection pools; Medium if retries lack backoff/caps; Low for supervised low-frequency utilities.
* **Remediation Guidance:** Configure explicit connection and read timeouts; cap retries with exponential backoff and jitter; propagate cancellation tokens.
* **Technology Adaptation:**
  - *Python*: Set `timeout=` in `httpx.AsyncClient`; wrap with `asyncio.wait_for()`; cap `tenacity` retries.
  - *.NET/C#*: Set `HttpClient.Timeout`; pass `CancellationToken`; use Polly retry policies.
  - *Java*: Configure connect/read timeouts on `RestTemplate`/`WebClient`; use Resilience4j.
  - *Node.js*: Supply `AbortController.signal` with `AbortSignal.timeout(ms)` to `fetch()`.

---

### PERF06 — LLM and Context Efficiency

* **Objective & Scope:** Minimize token consumption, context-window saturation, latency, and cost in LLM interactions and AI-agent orchestration.
* **Detection Criteria:**
  - Injecting full conversation histories into model prompts without windowing or summarization.
  - Calling LLMs in a loop for individual items instead of batching into a single structured prompt.
  - Embedding massive static documents verbatim into every system prompt.
  - Calling embedding APIs repeatedly on identical text without vector caching.
* **Evidence Requirements:** Unbounded message array passed to LLM; per-item prompt invocation in diff; large static text injected unconditionally.
* **False-Positive Guidance:** Short bounded chats (< 5 turns); genuinely independent per-item tasks that are properly parallelized; small system prompts (< 500 tokens).
* **Severity Guidance:** High if runaway token growth risks context overflow errors or severe cost escalation; Medium for unbatched prompts; Low for minor prompt redundancies.
* **Remediation Guidance:** Implement rolling context windows or summary memory; batch item evaluations; cache embeddings; enforce token ceilings.
* **Technology Adaptation:**
  - *LangChain*: Use `ConversationSummaryBufferMemory` with `max_token_limit`.
  - *OpenAI SDK*: Trim message lists using `tiktoken` budget checks; batch structured outputs.
  - *Semantic Kernel*: Implement history truncation filters before model invocation.

---

### PERF07 — Concurrency and Parallelism

* **Objective & Scope:** Exploit safe parallel execution for independent operations while preventing unbounded concurrency and concurrency-related safety risks.
* **Detection Criteria:**
  - Sequential `await` calls for independent network/DB operations that do not depend on each other's results.
  - Unbounded fan-out (`asyncio.gather(*tasks)`, `Promise.all`) launching thousands of concurrent tasks without a semaphore.
  - Concurrent tasks mutating shared state without synchronization primitives.
  - Synchronous parallel execution saturating CPU thread pools.
* **Evidence Requirements:** Independent async operations awaited sequentially; or unbounded task array passed to gather/Promise.all without concurrency limiting.
* **False-Positive Guidance:** Operations with strict sequential data dependencies; small fixed lists (≤ 3 items) where parallel dispatch overhead exceeds savings.
* **Severity Guidance:** High if race conditions risk state corruption or unbounded fan-out crashes pools; Medium for sequential I/O in hot paths; Low on cold paths.
* **Remediation Guidance:** Parallelize independent calls with `asyncio.gather` or `Promise.all`; throttle concurrency with semaphores (`asyncio.Semaphore`, `p-limit`).
* **Technology Adaptation:**
  - *Python*: Use `asyncio.gather()` with `asyncio.Semaphore(max_concurrency)`.
  - *.NET/C#*: Use `Task.WhenAll()` with `SemaphoreSlim` or `Parallel.ForEachAsync()`.
  - *Java*: Use `CompletableFuture.allOf()` with bounded `ExecutorService` or Virtual Threads.
  - *Node.js*: Use `Promise.all()` bounded by `p-limit`.

---

### PERF08 — Call and Computation Efficiency

* **Objective & Scope:** Eliminate redundant external calls, repeated expensive calculations, and avoidable work that can be cached, hoisted, or combined.
* **Detection Criteria:**
  - Calling the same service or endpoint multiple times with identical parameters within a single request.
  - Recompiling regular expressions or schemas inside hot loops or per-request handlers.
  - Reading configuration files or static assets from disk on every incoming request.
  - AI agents re-invoking tools with identical arguments across adjacent steps.
* **Evidence Requirements:** Duplicate call invocations in the same execution scope; inline regex compilation in loops; per-request file reads.
* **False-Positive Guidance:** Operations where outputs change between calls; intentional re-checks after state mutations; microsecond operations with negligible overhead.
* **Severity Guidance:** High for redundant AI tool or external API calls multiplying request latency; Medium for hot-loop regex recompilation; Low for trivial computations.
* **Remediation Guidance:** Hoist compiled regexes to module level; memoize identical request-scoped lookups; cache configuration during application startup.
* **Technology Adaptation:**
  - *Python*: Compile patterns at module level via `re.compile()`; use `@lru_cache()`.
  - *.NET/C#*: Use `static readonly Regex` (or source generators); cache with `Lazy<T>`.
  - *Java*: Store `Pattern.compile()` in static final constants; parse configuration in `@PostConstruct`.
  - *Node.js*: Declare top-level constants for patterns and static configs.

---

### PERF09 — Database Query and Index Efficiency

* **Objective & Scope:** Ensure queries have efficient execution plans, leverage covering indexes, and avoid table scans and over-fetching.
* **Detection Criteria:**
  - Filtering or ordering by unindexed columns on high-volume tables.
  - `SELECT *` in hot queries retrieving unused text/blob columns.
  - Leading wildcard searches (`LIKE '%keyword'`) that force full table scans.
  - Functions applied to indexed columns in `WHERE` clauses (e.g. `LOWER(email) = ...`) preventing index usage.
  - Foreign key columns involved in frequent joins lacking supporting indexes.
* **Evidence Requirements:** SQL query in diff filtering on columns missing indexes in schema; function wrappers on filtered columns; `SELECT *` on wide tables.
* **False-Positive Guidance:** Small lookup tables (< 1,000 rows) where full scans are cheaper than index lookups; write-heavy tables where index maintenance cost exceeds read savings.
* **Severity Guidance:** High for unindexed queries on large production tables in hot request paths; Medium for missing foreign-key indexes; Low on small tables.
* **Remediation Guidance:** Add composite or functional indexes (`CREATE INDEX CONCURRENTLY`); project specific columns instead of `SELECT *`; use full-text search extensions.
* **Technology Adaptation:**
  - *PostgreSQL*: Create functional indexes (`LOWER(col)`); use `pg_trgm` for pattern matching; check `EXPLAIN (ANALYZE, BUFFERS)`.
  - *MySQL*: Create composite indexes matching `WHERE` + `ORDER BY` column order.
  - *SQL Server*: Use filtered indexes or index column hints where appropriate.

---

### PERF10 — Data Retrieval and Pagination

* **Objective & Scope:** Bound query result sets, prevent excessive network transfer, and apply scalable pagination patterns to growing collections.
* **Detection Criteria:**
  - List queries or endpoints executing without `LIMIT`, `Take()`, or page size caps.
  - Deep offset pagination (`OFFSET 100000`) on large tables causing degrading scan times.
  - Client-side pagination where the backend transfers all rows and the client filters.
  - Pagination parameters accepting arbitrarily large user-supplied `limit` values without a maximum clamp.
* **Evidence Requirements:** Missing limit clause in query or handler; unbounded query returning collections; unbounded `limit`/`page_size` parameter.
* **False-Positive Guidance:** Intentional bulk data export endpoints (with streaming); administrative endpoints with fixed small datasets; internal queries with known cardinality bounds.
* **Severity Guidance:** High for public list endpoints returning unbounded rows; Medium for missing maximum clamp on page size; Low for internal administrative tools.
* **Remediation Guidance:** Enforce default and maximum `LIMIT` caps; use cursor/keyset pagination (`WHERE id > cursor`) for large or continuously growing datasets.
* **Technology Adaptation:**
  - *Python/SQLAlchemy*: Enforce `.limit(min(page_size, 100))`; implement keyset queries.
  - *.NET/EF Core*: Apply `.Take(Math.Min(size, 100))`; use cursor tokens.
  - *Java/Spring Data*: Use `Slice<T>` or `ScrollPosition` for keyset pagination instead of heavy `Page<T>` count queries.
  - *GraphQL*: Follow Relay connection specification with cursor-based arguments (`first`, `after`).

---

### PERF11 — Frontend Rendering Efficiency

* **Objective & Scope:** Prevent excessive virtual DOM diffing, UI thread blocking, and unnecessary re-render cascades in client-side applications.
* **Detection Criteria:**
  - Rendering large collections (> 100 items) directly in the DOM without list virtualization.
  - Inline object/array literals in JSX props causing reference inequality and triggering child re-renders.
  - `useEffect` dependencies containing freshly instantiated object/array literals recreated on every render.
  - Expensive CPU computations (sorting, filtering large lists) executed directly in component render bodies without memoization.
* **Evidence Requirements:** Large array mapped to DOM elements without virtualization; inline literals passed to memoized children or hook dependencies in frequently rendered components.
* **False-Positive Guidance:** Small lists (< 20 items); simple UI components without child hierarchies; pre-emptive memoization suggestions where re-renders are negligible.
* **Severity Guidance:** High if thousands of DOM elements freeze the UI thread; Medium for noticeable render cascades; Low for isolated, cheap component renders.
* **Remediation Guidance:** Virtualize large lists with `react-window` or `@tanstack/virtual`; stabilize hook dependencies and props; memoize expensive calculations with `useMemo`.
* **Technology Adaptation:**
  - *React*: Use `FixedSizeList` (`react-window`); wrap expensive computations in `useMemo()`.
  - *Vue*: Use `v-memo` directive on expensive subtrees; virtualize with `vue-virtual-scroller`.
  - *Angular*: Use `cdk-virtual-scroll-viewport`; implement `trackBy` functions in `*ngFor`.

---

### PERF12 — Code and Module Delivery

* **Objective & Scope:** Minimize initial JavaScript/CSS bundle sizes through code splitting, dynamic imports, and effective tree-shaking.
* **Detection Criteria:**
  - Eagerly importing large third-party libraries (PDF viewers, charting engines, rich text editors) in the critical entry bundle.
  - Absence of route-level code splitting (`React.lazy`, dynamic `import()`) on secondary or rarely visited pages.
  - Barrel/wildcard imports (`import * as _ from 'lodash'`) that defeat tree-shaking mechanisms.
  - Bundling server-only libraries or utilities into client bundles.
* **Evidence Requirements:** Top-level import of heavy libraries (> 50 KB) in initial app entry or common layout; missing lazy loading on non-critical feature routes.
* **False-Positive Guidance:** Small utilities (< 5 KB gzipped); libraries already proven to be tree-shaken by bundler; simple single-page apps with trivial overall bundle size.
* **Severity Guidance:** High if critical bundle size balloons by hundreds of kilobytes, delaying initial paint; Medium for heavy routes missing lazy loading; Low for minor package imports.
* **Remediation Guidance:** Use dynamic `import()` and `React.lazy()` with `Suspense`; replace heavy libraries with lighter alternatives; import specific submodules.
* **Technology Adaptation:**
  - *React/Vite*: Wrap routes in `lazy(() => import('./Route'))`; inspect with `rollup-plugin-visualizer`.
  - *Next.js*: Use `next/dynamic` with `{ ssr: false }` for client-only widgets.
  - *Node/Bundlers*: Replace `lodash` with `lodash-es` or native methods.

---

### PERF13 — Asset and Network Efficiency

* **Objective & Scope:** Optimize asset delivery, image payloads, font loading, and network transfer efficiency to protect Core Web Vitals (LCP, CLS, INP).
* **Detection Criteria:**
  - Unoptimized images (large PNG, BMP) used where modern WebP/AVIF formats would cut transfer size.
  - `<img>` tags missing explicit `width` and `height` or `aspect-ratio` attributes, causing Cumulative Layout Shift (CLS).
  - Web fonts loaded without `font-display: swap`, causing Flash of Invisible Text (FOIT) and blocking text rendering.
  - Multiple small sequential network requests that could be combined or dispatched concurrently.
* **Evidence Requirements:** Visible asset references without dimensions; blocking font stylesheets; uncompressed or oversized media in public page paths.
* **False-Positive Guidance:** Small icons (< 2 KB, SVG); hero images already managed by an optimized CDN pipeline; non-blocking background asset downloads.
* **Severity Guidance:** High if asset delays directly cause failing Core Web Vitals (LCP > 2.5s, CLS > 0.1); Medium for missing image dimensions; Low for minor asset optimization suggestions.
* **Remediation Guidance:** Specify image dimensions; use `<picture>` with WebP/AVIF sources or modern framework image components (`next/image`); add `font-display: swap`.
* **Technology Adaptation:**
  - *Next.js*: Use `next/image` for automatic resizing, format modernizing, and CLS prevention.
  - *HTML/CSS*: Add `width`, `height`, `loading="lazy"`, and `font-display: swap`.
  - *Web APIs*: Leverage HTTP/2 multiplexing; serve assets with long-lived immutable cache headers.

---

### PERF14 — State and Update Efficiency

* **Objective & Scope:** Optimize state management architectures, selector granularity, and update frequencies to prevent unnecessary recomputations and renders.
* **Detection Criteria:**
  - Components subscribing to entire state slices when only a single primitive property is required.
  - Redux/Zustand selectors returning newly allocated object or array references on every invocation, defeating memoization.
  - Firing `setState` or dispatching actions on high-frequency events (keystrokes, mouse move, scroll) without debouncing or throttling.
  - Recreating context value objects on every parent render, forcing all context consumers to re-render.
* **Evidence Requirements:** Selector creating new references; high-frequency input handler dispatching without debounce; context provider passing unstabilized object literal.
* **False-Positive Guidance:** Cheap primitive state subscriptions; low-frequency user interactions (click events); small components with no dependent child subtrees.
* **Severity Guidance:** High if state updates trigger rapid render cascades freezing input responsiveness; Medium for un-memoized selectors returning new objects; Low for isolated state updates.
* **Remediation Guidance:** Use fine-grained selectors (`createSelector`, selector callbacks); debounce high-frequency updates (`useDebounce`); memoize context values with `useMemo`.
* **Technology Adaptation:**
  - *Redux Toolkit*: Memoize derived selectors with `createSelector()`; use fine-grained `useSelector()`.
  - *Zustand*: Use selector form `useStore(state => state.property)` instead of consuming full state.
  - *React Context*: Wrap provider `value` in `useMemo()`; separate frequently changing state into distinct contexts.
