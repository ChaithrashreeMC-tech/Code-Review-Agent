# .NET Modularity & Architecture Reference

Provides .NET dependency injection, boundary, and modularity rules for **Modularity Review Agent** (`skill-eng-modularity`).

---

## Actionable Technology Rules

### DOTNET-MOD-001: Captive Dependency in ASP.NET Core DI
- **Applies To**: `IServiceCollection`, `Singleton`, `Scoped`, `BackgroundService`.
- **Behavior**: Singletons capturing Scoped services (`DbContext`) cause state corruption, memory leaks, and concurrency crashes.
- **Inspect**: `AddSingleton<T>` / `AddHostedService<T>` constructors accepting `AddScoped<T>` dependencies.
- **Violation**:
  ```csharp
  builder.Services.AddSingleton<ICacheWarmer, CacheWarmer>(); // Scoped DbContext captured!
  public class CacheWarmer(AppDbContext db) : ICacheWarmer { ... }
  ```
- **Evidence**: `AddSingleton`/`AddHostedService` registration site + constructor with `AddScoped` dependency.
- **False Positives**: Resolving scope via `IServiceScopeFactory.CreateScope()` inside execution methods.
- **Remediation**: Inject `IServiceScopeFactory` and create a short-lived scope inside execution methods.
- **Engineering Skill Map**: `MOD02`, `MOD04`

---

### DOTNET-MOD-002: Service Locator Anti-Pattern via IServiceProvider
- **Applies To**: Application services, MediatR handlers, domain classes.
- **Behavior**: Direct `IServiceProvider.GetService()` calls hide dependencies and break constructor contracts.
- **Inspect**: Classes passing `IServiceProvider` or calling `GetRequiredService<T>()` in business methods.
- **Violation**:
  ```csharp
  public class OrderProcessor(IServiceProvider provider) {
      public void Process(Order o) => provider.GetRequiredService<IPaymentService>().Charge(o.Total);
  }
  ```
- **Evidence**: Constructor taking `IServiceProvider` + execution body resolving business services.
- **False Positives**: Composition roots, custom middleware/binders, plugin resolution factories.
- **Remediation**: Declare dependencies explicitly in constructor parameters.
- **Engineering Skill Map**: `MOD01`, `MOD02`

---

### DOTNET-MOD-003: EF Core DbContext Leakage Across Boundaries
- **Applies To**: Web API controllers, domain entities, `DbContext`, `DbSet<T>`.
- **Behavior**: Exposing `DbContext`, `DbSet<T>`, or raw `IQueryable<T>` directly to API layers leaks persistence details.
- **Inspect**: Public controller actions returning `IQueryable<TEntity>` or domain projects referencing EF Core.
- **Violation**:
  ```csharp
  [HttpGet] public IQueryable<User> GetUsers() => _dbContext.Users; // Leaks DbContext to HTTP client
  ```
- **Evidence**: Controller signature returning `IQueryable<TEntity>` of an internal DB entity.
- **False Positives**: Vertical slices projecting `IQueryable` via `.Select()` or `.ProjectTo<Dto>()` before returning.
- **Remediation**: Project queries to typed DTOs (`List<UserDto>`) using `.Select()` and `.ToListAsync()`.
- **Engineering Skill Map**: `MOD03`, `MOD09`

---

### DOTNET-MOD-004: Circular Project and Assembly Dependencies
- **Applies To**: `.csproj` files, assembly references, Clean/Layered architectures.
- **Behavior**: Domain projects referencing Infrastructure packages or persistence assemblies breaks dependency inversion.
- **Inspect**: `<ProjectReference>` nodes in `.csproj` files and Infrastructure imports in Core/Domain namespaces.
- **Violation**: `Domain.csproj` containing `<ProjectReference Include="..\Infrastructure\Infrastructure.csproj" />`.
- **Evidence**: Reference to Infrastructure project inside Domain `.csproj`.
- **False Positives**: Monolithic integration test projects referencing all layers.
- **Remediation**: Invert dependencies by declaring interfaces in Domain/Application and implementations in Infrastructure.
- **Engineering Skill Map**: `MOD02`, `MOD12`

---

### DOTNET-MOD-005: Options Pattern & Configuration Coupling
- **Applies To**: `IConfiguration`, `IOptions<T>`, `IOptionsSnapshot<T>`, `IOptionsMonitor<T>`.
- **Behavior**: Injecting raw `IConfiguration` into domain services creates tight coupling to raw string keys (`_config["Key"]`).
- **Inspect**: Constructors taking `IConfiguration` and string indexer lookups in business methods.
- **Violation**:
  ```csharp
  public class StripeService(IConfiguration config) {
      private readonly string _key = config["Stripe:ApiKey"]!; // Unvalidated string lookup
  }
  ```
- **Evidence**: Service constructor taking `IConfiguration` + string indexer lookups for settings.
- **False Positives**: Startup code in `Program.cs` or custom `AddOptions<T>()` validation extensions.
- **Remediation**: Bind configuration to strongly-typed POCOs and inject `IOptions<T>`.
- **Engineering Skill Map**: `MOD01`, `MOD08`

---

### DOTNET-MOD-006: Monolithic Program.cs Composition
- **Applies To**: ASP.NET Core startup (`Program.cs`), `IServiceCollection` extensions.
- **Behavior**: Placing hundreds of inline service registrations directly in `Program.cs` creates unmaintainable God files.
- **Inspect**: `Program.cs` >150 lines with unorganized inline registrations lacking extension modularization.
- **Evidence**: `Program.cs` containing monolithic inline service, DB, auth, and HTTP client registrations.
- **False Positives**: Microservices or Minimal APIs with fewer than 5 total registered services.
- **Remediation**: Extract registrations into layer-specific extension methods (e.g., `services.AddInfrastructure()`).
- **Engineering Skill Map**: `MOD05`, `MOD11`
