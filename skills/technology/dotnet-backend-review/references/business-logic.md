# .NET Business Logic Reference

Provides API response contracts, EF Core optimistic concurrency, Outbox pattern, and domain testability rules for **Business Logic Review Agent** (`skill-eng-business-logic`).

---

## Actionable Technology Rules

### DOTNET-BIZ-001: HTTP Response Contract Mismatches
- **Applies To**: ASP.NET Core controllers, Minimal APIs, `IActionResult`, `IResult`.
- **Behavior**: Returning `200 OK` with error payloads (`{ "success": false }`) or `500` for validation errors violates HTTP contracts.
- **Inspect**: Actions returning `Ok(new { success = false, error = "..." })` on validation or domain rule failure.
- **Violation**: `if (req.Amount <= 0) return Ok(new { Success = false, Error = "Amount invalid" }); // HTTP 200 contract mismatch!`
- **Evidence**: Action returning `200 OK` with explicit failure indicator fields (`Success = false`).
- **False Positives**: Custom GraphQL endpoints or legacy RPC wrappers designed around HTTP 200 contracts.
- **Remediation**: Return standard HTTP error status codes (`BadRequest(ProblemDetails)` or `422 UnprocessableEntity`).
- **Engineering Skill Map**: `BIZ01`, `BIZ04`

---

### DOTNET-BIZ-002: DTO Serialization & Property Name Mismatches
- **Applies To**: DTO records/classes, `System.Text.Json` attributes (`[JsonPropertyName]`).
- **Behavior**: Mismatches between C# PascalCase properties and payload contract names without `[JsonPropertyName]` cause silent null deserialization.
- **Inspect**: Custom integration DTOs receiving snake_case/camelCase JSON keys without property mapping attributes.
- **Violation**: `public class WebhookDto { public string TransactionId { get; set; } } // Silent null when JSON has "transaction_id"`
- **Evidence**: DTO property name differing from payload contract key without JSON mapping attribute or converter.
- **False Positives**: Global `System.Text.Json` naming policy (`SnakeCaseLower` or `CamelCase`) configured application-wide.
- **Remediation**: Annotate DTO properties explicitly with `[JsonPropertyName("transaction_id")]`.
- **Engineering Skill Map**: `BIZ02`, `BIZ05`

---

### DOTNET-BIZ-003: EF Core Optimistic Concurrency Controls
- **Applies To**: EF Core entities, `DbContext`, `[Timestamp]`, `byte[] RowVersion`.
- **Behavior**: Mutating shared financial or inventory balances without concurrency tokens permits lost updates under concurrent load.
- **Inspect**: Domain entities with mutable balance/stock properties missing `[Timestamp]` or `IsConcurrencyToken()`.
- **Violation**: `public class Product { public int Id { get; set; } public int Stock { get; set; } } // Missing RowVersion token`
- **Evidence**: Entity with mutable concurrent state lacking `[Timestamp]` or `RowVersion` concurrency token.
- **False Positives**: Append-only audit logs or immutable single-owner entities.
- **Remediation**: Add `[Timestamp] public byte[] RowVersion { get; set; }` and catch `DbUpdateConcurrencyException`.
- **Engineering Skill Map**: `BIZ03`, `BIZ06`

---

### DOTNET-BIZ-004: Outbox Pattern & Event Publishing Consistency
- **Applies To**: MediatR domain events, RabbitMQ/MassTransit message bus, EF Core transactions.
- **Behavior**: Publishing message bus events directly before/after `SaveChangesAsync()` leads to distributed state inconsistencies if DB save fails.
- **Inspect**: Direct `_bus.Publish()` calls in business services outside transactional Outbox handling.
- **Violation**: `await _bus.Publish(new OrderCreated(order.Id)); await _db.SaveChangesAsync(); // Event sent before DB transaction commits!`
- **Evidence**: Message bus `Publish`/`Send` call executed outside a transactional Outbox or before `SaveChangesAsync()`.
- **False Positives**: Usage of a transactional Outbox pattern (MassTransit Outbox or custom Outbox entity in same `DbContext`).
- **Remediation**: Persist domain events to an Outbox table within the same `DbContext` transaction.
- **Engineering Skill Map**: `BIZ07`, `BIZ08`

---

### DOTNET-BIZ-005: Domain Invariants & Aggregate Root Encapsulation
- **Applies To**: Domain entities, aggregate roots, encapsulation.
- **Behavior**: Public setters on entity state properties (`public decimal Balance { get; set; }`) allow external callers to bypass domain validation.
- **Inspect**: Domain entities with public property setters for state governed by business invariant rules.
- **Violation**: `public class Account { public decimal Balance { get; set; } } // Public setter allows direct negative balance`
- **Evidence**: Public setter on domain entity property representing state governed by validation rules.
- **False Positives**: Simple Anemic DTO models used strictly for API data transfer.
- **Remediation**: Use private setters (`public decimal Balance { get; private set; }`) and encapsulate state mutation in domain methods.
- **Engineering Skill Map**: `BIZ02`, `BIZ09`

---

### DOTNET-BIZ-006: Integration Test Isolation & WebApplicationFactory Strategy
- **Applies To**: Integration test suites, `WebApplicationFactory<T>`, `UseInMemoryDatabase`.
- **Behavior**: Using `UseInMemoryDatabase` for integration testing fails to catch relational SQL constraints or EF Core query translation bugs.
- **Inspect**: Integration test suites relying on EF Core `UseInMemoryDatabase` for repository SQL validation.
- **Violation**: `services.AddDbContext<AppDbContext>(o => o.UseInMemoryDatabase("TestDb")); // Fails to enforce SQL constraints`
- **Evidence**: Integration testing setup using `UseInMemoryDatabase` to validate relational database queries.
- **False Positives**: Simple unit tests mocking `IQueryable` via mock frameworks.
- **Remediation**: Use Testcontainers SQL Server or SQLite in-memory for integration tests via `WebApplicationFactory`.
- **Engineering Skill Map**: `BIZ10`, `BIZ12`
