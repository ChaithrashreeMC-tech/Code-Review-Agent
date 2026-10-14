# .NET Maintainability Reference

Provides C# language idioms, nullability, exception handling, and resource rules for **Maintainability Review Agent** (`skill-eng-maintainability`).

---

## Actionable Technology Rules

### DOTNET-MAINT-001: Modern C# Idioms & Pattern Matching
- **Applies To**: C# source files (`.cs`), C# 10–13 features (.NET 6–9).
- **Behavior**: Legacy type casting, verbose class DTOs, and nested null checks increase code verbosity and maintenance cost.
- **Inspect**: Legacy `switch` statements, manual type casts after `is` checks, and verbose class DTOs.
- **Violation**:
  ```csharp
  public class UserDto { public string Name { get; set; } } // Verbose class DTO
  if (u.Role is AdminRole) { var a = (AdminRole)u.Role; return a.Title; } // Verbose cast
  ```
- **Evidence**: Multi-line type check and manual cast patterns in C# 10+ codebases.
- **False Positives**: Explicit legacy C# constraints (`<LangVersion>` < 10) or mutable EF Core tracked entities.
- **Remediation**: Use positional records (`public record UserDto(string Name);`), switch expressions, and property patterns.
- **Engineering Skill Map**: `MAINT01`, `MAINT03`

---

### DOTNET-MAINT-002: Nullable Reference Types & Null-Forgiving Misuse
- **Applies To**: C# projects with `<Nullable>enable</Nullable>`.
- **Behavior**: Indiscriminate use of `!` (`name!`) or `#pragma warning disable CS8618` bypasses compiler static safety.
- **Inspect**: `!` appended to properties/parameters without validation and `#pragma warning disable` for nullability.
- **Violation**: `string email = dto.Customer.Email!; // Unvalidated null suppression`
- **Evidence**: Use of `!` operator on reference types that can legally be null without prior guard checks.
- **False Positives**: EF Core entity navigation properties initialized by proxies (`public Customer Customer { get; set; } = null!;`).
- **Remediation**: Use `ArgumentNullException.ThrowIfNull()` or null-coalescing fallbacks (`??`).
- **Engineering Skill Map**: `MAINT02`, `MAINT05`

---

### DOTNET-MAINT-003: IDisposable / IAsyncDisposable Resource Leaks
- **Applies To**: Streams, database connections, `CancellationTokenSource`, `HttpResponseMessage`.
- **Behavior**: Instantiating disposable objects without `using` statements causes handle leaks and memory growth.
- **Inspect**: Local variable instantiations of `IDisposable` or `IAsyncDisposable` lacking `using`.
- **Violation**:
  ```csharp
  var stream = File.OpenRead(path); // Unhandled handle leak!
  var buffer = new byte[stream.Length]; await stream.ReadAsync(buffer);
  ```
- **Evidence**: Local variable creation of `IDisposable` type missing `using` declaration or `.Dispose()`.
- **False Positives**: Resource lifecycle transferred to caller/factory or `HttpClient` from `IHttpClientFactory`.
- **Remediation**: Use C# 8+ `using var` declarations or `await using var`.
- **Engineering Skill Map**: `MAINT04`, `MAINT08`

---

### DOTNET-MAINT-004: Exception Handling & Stack Preservation
- **Applies To**: `try-catch` blocks, exception re-throwing (`throw;` vs `throw ex;`).
- **Behavior**: Re-throwing exceptions with `throw ex;` destroys original stack traces, obscuring root cause file line numbers.
- **Inspect**: Catch blocks containing `throw ex;` or empty catch blocks swallowing exceptions.
- **Violation**: `catch (Exception ex) { logger.LogError(ex); throw ex; } // Destroys stack trace!`
- **Evidence**: Catch block containing `throw ex;` or `throw e;`.
- **False Positives**: Wrapping caught exception as `innerException` in custom exception (`throw new DomainException("Error", ex);`).
- **Remediation**: Use parameterless `throw;` to preserve original stack trace.
- **Engineering Skill Map**: `MAINT06`, `MAINT07`

---

### DOTNET-MAINT-005: Roslyn Analyzer Compliance & Pragma Misuse
- **Applies To**: `.editorconfig`, `.csproj` properties, Roslyn compiler warnings.
- **Behavior**: Indiscriminate `#pragma warning disable` without technical rationale hides underlying quality defects.
- **Inspect**: `#pragma warning disable` directives suppressing CS/CA rules without comments.
- **Evidence**: `#pragma warning disable` without explaining comment or tracked issue ID.
- **False Positives**: Auto-generated files (EF Core migrations, gRPC, OpenAPI clients).
- **Remediation**: Fix underlying issue or configure severity globally in `.editorconfig`.
- **Engineering Skill Map**: `MAINT01`, `MAINT09`

---

### DOTNET-MAINT-006: DTO and Contract Versioning Compatibility
- **Applies To**: Public API DTOs, NuGet package references, target framework updates.
- **Behavior**: Removing properties or changing types on public DTOs breaks downstream client compatibility.
- **Inspect**: Breaking changes to public DTO properties or mismatched target framework package updates.
- **Evidence**: Breaking modifications on public contract models or mismatched framework references in `.csproj`.
- **False Positives**: Internal DTOs strictly scoped within a single service module refactored atomically.
- **Remediation**: Mark deprecated members with `[Obsolete]` or introduce versioned API contracts (`V1/OrderDto.cs`).
- **Engineering Skill Map**: `MAINT10`, `MAINT12`
