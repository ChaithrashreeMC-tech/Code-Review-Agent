# Performance Review Checklist & Detailed Rule Guidance

This reference provides detection criteria, evidence requirements, false-positive guidance, severity classification, remediation advice, and technology adaptations for all 14 engineering performance rules (PERF01–PERF14). Use during Step 4 of the Review Workflow in `SKILL.md`.

---

## 1. Shared Review Principles & Technology Context

- **Infer Technology Context:** Infer runtime, frameworks, ORMs, and libraries from imports, manifests, and surrounding code. Adapt detection patterns to the active stack without requiring technology-specific rule copies.
- **Evidence-Based:** Report bottlenecks only when diff code and execution context substantiate them; record unconfirmed concerns in `uncertainty_notes` (0 deduction).
- **Scale Proportionality:** Weigh findings against actual workload and data volume (e.g., small lookup tables do not need indexes or cursor pagination).
- **Root-Cause Deduplication:** Multiple symptoms sharing a single root cause (e.g. query loop) must produce one primary finding.

### Rule Disambiguation Boundaries

| Overlap Pair | Boundary Guidance |
|---|---|
| **PERF01 vs. PERF07** | **PERF01** for single-threaded I/O blocking an event loop or sequential CPU delay; **PERF07** for independent I/O that should run in parallel, or unbounded concurrency fan-out lacking semaphores. |
| **PERF02 vs. PERF08** | **PERF02** for database queries and ORM navigation round-trips in loops (N+1); **PERF08** for redundant external API calls, duplicate AI tool invocations, inline regex compilation, or repeated in-memory computations. |
| **PERF09 vs. PERF10** | **PERF09** for inefficient query plans, missing indexes, full scans, or functions on filtered columns; **PERF10** for missing `LIMIT` clauses, unbounded result sets, or deep `OFFSET` pagination. |
| **PERF11 vs. PERF14** | **PERF11** for large DOM node counts, missing virtualization, or expensive JSX renders; **PERF14** for broad store subscriptions, un-memoized selectors returning new object references, or unthrottled state updates. |

---

## 2. Performance Rules (PERF01–PERF14)

### PERF01 — Execution Efficiency
- **Objective & Scope:** Eliminate blocking operations, synchronous delays, and unneeded CPU work in request handlers, background jobs, and event-loop threads.
- **Detection Criteria:** Synchronous I/O (file, network, DB) inside `async` routines without awaiting; blocking sleep (`time.sleep()`, `Thread.Sleep()`) on hot paths; or long batch work executed inline in user-facing HTTP requests.
- **Evidence Requirements:** Visible synchronous or blocking call site in an `async` context or latency-critical request path.
- **False-Positive Guidance:** One-time startup routines, CLI scripts, bounded CPU work on tiny inputs, or test setup/teardown code.
- **Severity Guidance:** Critical if blocking an event loop in a hot path; High if serializing operations that delay user requests; Medium for bounded CPU work.
- **Remediation Guidance:** Use async I/O drivers (`httpx`, `asyncpg`), offload CPU tasks to worker pools (`run_in_executor`, `Task.Run`), or defer to background queues.
- **Technology Adaptation:** *Python:* replace `requests` with `httpx`; *C#:* avoid `.Result`/`.Wait()`; *Java:* avoid blocking in Reactor/RxJava; *Node.js:* avoid `fs.readFileSync` in web routes.

### PERF02 — Data Access Efficiency
- **Objective & Scope:** Prevent unnecessary database round trips, N+1 query patterns, and unbatched data retrieval in ORMs and repositories.
- **Detection Criteria:** Database query or ORM relationship access inside loops over entities or IDs; lazy-loaded navigation properties traversed in loops; or GraphQL resolvers fetching child records without DataLoader.
- **Evidence Requirements:** Code loop issuing database queries over an unbounded or dynamically sized collection without eager loading or batching.
- **False-Positive Guidance:** Loops over small constant sets (1–3 items), per-item writes where no batch API exists, or access against a warmed in-memory cache.
- **Severity Guidance:** High if query count scales linearly with collection size in user-facing endpoints; Medium if bounded but non-trivial; Low in background batch jobs.
- **Remediation Guidance:** Use eager loading (`selectinload`, `.Include()`, `JOIN FETCH`), batch with `WHERE id IN (...)`, or introduce GraphQL DataLoader.
- **Technology Adaptation:** *SQLAlchemy:* use `joinedload()`/`selectinload()`; *EF Core:* add `.Include()`; *Hibernate:* use `JOIN FETCH` or `@BatchSize`; *Prisma:* batch with `in: ids`.

### PERF03 — Memory and Resource Management
- **Objective & Scope:** Prevent unbounded memory accumulation, large object allocations, and unclosed resource handles (streams, connections, file descriptors).
- **Detection Criteria:** Reading entire large files or responses into memory when streaming is feasible; materializing full DB result sets in RAM for exports; missing deterministic disposal (`with`, `using`, `try-with-resources`).
- **Evidence Requirements:** Unbounded read or collection append in diff; missing resource disposal syntax under high-frequency or large-payload paths.
- **False-Positive Guidance:** Small bounded configurations (< 4 KB), resources managed by framework DI containers, or explicit size-bounded buffers.
- **Severity Guidance:** Critical if unbounded user payloads cause server OOM under load; High for large unstreamed exports; Medium for inconsistent disposal.
- **Remediation Guidance:** Stream large payloads via generators or chunked streams; wrap resource allocations in deterministic disposal blocks; apply batch limits.
- **Technology Adaptation:** *Python:* use `yield_per()` and `with`; *C#:* use `IAsyncEnumerable<T>` and `using`; *Java:* use Streams with `try-with-resources`; *Node.js:* use `stream.pipeline()`.

### PERF04 — Caching Strategy
- **Objective & Scope:** Ensure caching is applied for repeated, expensive computations and data retrievals, with proper TTL and invalidation semantics.
- **Detection Criteria:** Repeated expensive queries or external API calls for static/slow-moving data without caching; cache entries created for mutable entities without TTL; or missing cache invalidation on write/update paths.
- **Evidence Requirements:** High-frequency expensive operation with stable inputs lacking caching; or mutable cache entry lacking TTL or invalidation hooks.
- **False-Positive Guidance:** Rapidly changing or user-personalized data; fast in-memory operations (< 1 ms); or paths where consistency risk outweighs latency gain.
- **Severity Guidance:** High for hot endpoints querying slow databases without caching; Medium for missing TTL on mutable cached data; Low for cold administrative paths.
- **Remediation Guidance:** Introduce in-memory or distributed cache (Redis) with appropriate TTL; ensure write mutations invalidate corresponding cache keys.
- **Technology Adaptation:** *Python:* use `functools.lru_cache` or Redis with `ex=` TTL; *C#:* use `IMemoryCache`/`IDistributedCache`; *Spring:* use `@Cacheable`/`@CacheEvict`.

### PERF05 — Timeouts and Resilience
- **Objective & Scope:** Guard external network calls, database queries, and asynchronous operations against indefinite hangs and cascading pool exhaustion.
- **Detection Criteria:** HTTP/RPC clients or database connections initialized without timeouts; retry loops lacking maximum attempt limits or exponential backoff; or async wait constructs without timeout wrappers.
- **Evidence Requirements:** External I/O call site visible in diff lacking timeout configuration or surrounding timeout policy.
- **False-Positive Guidance:** Global client factory or middleware already enforcing timeouts; startup health checks polling until ready; internal in-memory waits.
- **Severity Guidance:** High if unbounded network call can exhaust thread/connection pools; Medium if retries lack backoff caps; Low for supervised low-frequency utilities.
- **Remediation Guidance:** Configure explicit connection and read timeouts; cap retries with exponential backoff and jitter; propagate cancellation tokens.
- **Technology Adaptation:** *Python:* set `timeout=` in `httpx` or wrap with `asyncio.wait_for()`; *C#:* pass `CancellationToken` and configure `HttpClient.Timeout`; *Node.js:* use `AbortSignal.timeout(ms)`.

### PERF06 — LLM and Context Efficiency
- **Objective & Scope:** Minimize token consumption, context-window saturation, latency, and cost in LLM interactions and AI-agent orchestration.
- **Detection Criteria:** Injecting full conversation histories into model prompts without windowing or summarization; calling LLMs in a loop for individual items instead of batching; embedding massive static documents verbatim into every prompt.
- **Evidence Requirements:** Unbounded message array passed to LLM; per-item prompt invocation in diff; large static text injected unconditionally.
- **False-Positive Guidance:** Short bounded chats (< 5 turns); genuinely independent per-item tasks properly parallelized; small system prompts (< 500 tokens).
- **Severity Guidance:** High if runaway token growth risks context overflow errors or severe cost escalation; Medium for unbatched prompts; Low for minor redundancies.
- **Remediation Guidance:** Implement rolling context windows or summary memory; batch item evaluations into structured prompts; cache embeddings; enforce token ceilings.
- **Technology Adaptation:** *LangChain:* use `ConversationSummaryBufferMemory`; *OpenAI SDK:* trim message lists using `tiktoken` budget checks; *Semantic Kernel:* apply history filters.

### PERF07 — Concurrency and Parallelism
- **Objective & Scope:** Exploit safe parallel execution for independent operations while preventing unbounded concurrency and shared-state race conditions.
- **Detection Criteria:** Sequential `await` calls for independent network/DB operations; unbounded fan-out (`asyncio.gather(*tasks)`, `Promise.all`) launching thousands of concurrent tasks without a semaphore; concurrent tasks mutating shared state without synchronization.
- **Evidence Requirements:** Independent async operations awaited sequentially; or unbounded task array passed to gather/Promise.all without concurrency limiting.
- **False-Positive Guidance:** Operations with strict sequential data dependencies; small fixed lists (≤ 3 items) where parallel dispatch overhead exceeds savings.
- **Severity Guidance:** High if race conditions risk state corruption or unbounded fan-out crashes pools; Medium for sequential I/O in hot paths; Low on cold paths.
- **Remediation Guidance:** Parallelize independent calls with `asyncio.gather` or `Promise.all`; throttle concurrency with semaphores (`asyncio.Semaphore`, `p-limit`).
- **Technology Adaptation:** *Python:* use `asyncio.gather()` with `asyncio.Semaphore`; *C#:* use `Task.WhenAll()` with `SemaphoreSlim`; *Node.js:* use `Promise.all()` bounded by `p-limit`.

### PERF08 — Call and Computation Efficiency
- **Objective & Scope:** Eliminate redundant external calls, repeated expensive calculations, and avoidable work that can be cached, hoisted, or combined.
- **Detection Criteria:** Calling the same service or endpoint multiple times with identical parameters within a single request; recompiling regular expressions or schemas inside hot loops; reading configuration files or static assets from disk on every incoming request.
- **Evidence Requirements:** Duplicate call invocations in the same execution scope; inline regex compilation in loops; per-request file reads.
- **False-Positive Guidance:** Operations where outputs change between calls; intentional re-checks after state mutations; microsecond operations with negligible overhead.
- **Severity Guidance:** High for redundant AI tool or external API calls multiplying request latency; Medium for hot-loop regex recompilation; Low for trivial computations.
- **Remediation Guidance:** Hoist compiled regexes to module level; memoize identical request-scoped lookups; cache configuration during application startup.
- **Technology Adaptation:** *Python:* compile patterns via `re.compile()` at module level; *C#:* use `static readonly Regex` or source generators; *Java:* store in `static final Pattern`.

### PERF09 — Database Query and Index Efficiency
- **Objective & Scope:** Ensure queries have efficient execution plans, leverage covering indexes, and avoid table scans and over-fetching.
- **Detection Criteria:** Filtering or ordering by unindexed columns on high-volume tables; `SELECT *` in hot queries retrieving unused text/blob columns; leading wildcard searches (`LIKE '%keyword'`); functions applied to indexed columns in `WHERE` clauses (e.g. `LOWER(email)`).
- **Evidence Requirements:** SQL query in diff filtering on unindexed columns on large tables; function wrappers preventing index usage; `SELECT *` on wide tables.
- **False-Positive Guidance:** Small lookup tables (< 1,000 rows) where full scans are cheaper than index lookups; write-heavy tables where index maintenance cost exceeds read savings.
- **Severity Guidance:** High for unindexed queries on large production tables in hot request paths; Medium for missing foreign-key indexes; Low on small tables.
- **Remediation Guidance:** Add composite or functional indexes (`CREATE INDEX CONCURRENTLY`); project specific columns instead of `SELECT *`; use full-text search extensions.
- **Technology Adaptation:** *PostgreSQL:* create functional indexes (`LOWER(col)`) and use `pg_trgm`; *MySQL:* build composite indexes matching `WHERE` + `ORDER BY` column order.

### PERF10 — Data Retrieval and Pagination
- **Objective & Scope:** Bound query result sets, prevent excessive network transfer, and apply scalable pagination patterns to growing collections.
- **Detection Criteria:** List queries executing without `LIMIT`, `Take()`, or page size caps; deep offset pagination (`OFFSET 100000`) on large tables causing degrading scans; client-side pagination where backend transfers all rows; unbounded user-supplied `limit` parameters.
- **Evidence Requirements:** Missing limit clause in list query or handler; unbounded query returning collections; unbounded `limit`/`page_size` parameter.
- **False-Positive Guidance:** Intentional bulk data export endpoints (with streaming); administrative endpoints with fixed small datasets; internal queries with known cardinality bounds.
- **Severity Guidance:** High for public list endpoints returning unbounded rows; Medium for missing maximum clamp on page size; Low for internal administrative tools.
- **Remediation Guidance:** Enforce default and maximum `LIMIT` caps; use cursor/keyset pagination (`WHERE id > cursor`) for large or continuously growing datasets.
- **Technology Adaptation:** *SQLAlchemy:* enforce `.limit(min(page_size, 100))`; *EF Core:* apply `.Take(Math.Min(size, 100))`; *Spring Data:* use `Slice<T>` or `ScrollPosition`.

### PERF11 — Frontend Rendering Efficiency
- **Objective & Scope:** Prevent excessive virtual DOM diffing, UI thread blocking, and unnecessary re-render cascades in client-side applications.
- **Detection Criteria:** Rendering large collections (> 100 items) directly in the DOM without list virtualization; inline object/array literals in JSX props triggering child re-renders; expensive CPU computations (sorting/filtering large lists) executed directly in component render bodies without memoization.
- **Evidence Requirements:** Large array mapped to DOM elements without virtualization; inline literals passed to memoized children in frequently rendered components.
- **False-Positive Guidance:** Small lists (< 20 items); simple UI components without child hierarchies; pre-emptive memoization suggestions where re-renders are negligible.
- **Severity Guidance:** High if thousands of DOM elements freeze the UI thread; Medium for noticeable render cascades; Low for isolated, cheap component renders.
- **Remediation Guidance:** Virtualize large lists with `react-window` or `@tanstack/virtual`; stabilize hook dependencies and props; memoize expensive calculations with `useMemo`.
- **Technology Adaptation:** *React:* use `FixedSizeList` (`react-window`) and `useMemo()`; *Vue:* apply `v-memo` directive and `vue-virtual-scroller`; *Angular:* use `cdk-virtual-scroll-viewport`.

### PERF12 — Code and Module Delivery
- **Objective & Scope:** Minimize initial JavaScript/CSS bundle sizes through code splitting, dynamic imports, and effective tree-shaking.
- **Detection Criteria:** Eagerly importing large third-party libraries (PDF viewers, charting engines, rich text editors) in the critical entry bundle; absence of route-level code splitting (`React.lazy`, dynamic `import()`) on secondary pages; barrel/wildcard imports defeating tree-shaking.
- **Evidence Requirements:** Top-level import of heavy libraries (> 50 KB) in initial app entry or common layout; missing lazy loading on non-critical feature routes.
- **False-Positive Guidance:** Small utilities (< 5 KB gzipped); libraries already proven to be tree-shaken by bundler; simple single-page apps with trivial overall bundle size.
- **Severity Guidance:** High if critical bundle size balloons by hundreds of kilobytes, delaying initial paint; Medium for heavy routes missing lazy loading; Low for minor package imports.
- **Remediation Guidance:** Use dynamic `import()` and `React.lazy()` with `Suspense`; replace heavy libraries with lighter alternatives; import specific submodules.
- **Technology Adaptation:** *React/Vite:* wrap routes in `lazy(() => import('./Route'))`; *Next.js:* use `next/dynamic` with `{ ssr: false }`; *Node:* replace `lodash` with `lodash-es`.

### PERF13 — Asset and Network Efficiency
- **Objective & Scope:** Optimize asset delivery, image payloads, font loading, and network transfer efficiency to protect Core Web Vitals (LCP, CLS, INP).
- **Detection Criteria:** Unoptimized images (large PNG, BMP) used where modern WebP/AVIF formats would cut transfer size; `<img>` tags missing explicit `width` and `height` or `aspect-ratio` attributes causing Cumulative Layout Shift (CLS); web fonts loaded without `font-display: swap` blocking text rendering.
- **Evidence Requirements:** Visible asset references without dimensions; blocking font stylesheets; uncompressed or oversized media in public page paths.
- **False-Positive Guidance:** Small icons (< 2 KB, SVG); hero images already managed by an optimized CDN pipeline; non-blocking background asset downloads.
- **Severity Guidance:** High if asset delays directly cause failing Core Web Vitals (LCP > 2.5s, CLS > 0.1); Medium for missing image dimensions; Low for minor asset suggestions.
- **Remediation Guidance:** Specify image dimensions; use `<picture>` with WebP/AVIF sources or modern framework image components (`next/image`); add `font-display: swap`.
- **Technology Adaptation:** *Next.js:* use `next/image` for automatic resizing and CLS prevention; *HTML/CSS:* add `width`, `height`, `loading="lazy"`, and `font-display: swap`.

### PERF14 — State and Update Efficiency
- **Objective & Scope:** Optimize state management architectures, selector granularity, and update frequencies to prevent unnecessary recomputations and renders.
- **Detection Criteria:** Components subscribing to entire state slices when only a single primitive property is required; Redux/Zustand selectors returning newly allocated object/array references on every invocation defeating memoization; firing `setState` or dispatching actions on high-frequency events (keystrokes, scroll) without debouncing.
- **Evidence Requirements:** Selector creating new object references on every call; high-frequency input handler dispatching without debounce; context provider passing unstabilized object literal.
- **False-Positive Guidance:** Cheap primitive state subscriptions; low-frequency user interactions (click events); small components with no dependent child subtrees.
- **Severity Guidance:** High if state updates trigger rapid render cascades freezing input responsiveness; Medium for un-memoized selectors returning new objects; Low for isolated state updates.
- **Remediation Guidance:** Use fine-grained selectors (`createSelector`, selector callbacks); debounce high-frequency updates (`useDebounce`); memoize context values with `useMemo`.
- **Technology Adaptation:** *Redux Toolkit:* memoize derived selectors with `createSelector()`; *Zustand:* use fine-grained selectors `useStore(s => s.prop)`; *Context:* wrap provider `value` in `useMemo()`.
