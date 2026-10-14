# .NET Security Reference

Provides ASP.NET Core authentication, authorization, raw SQL injection, and secrets protection rules for **Security Review Agent** (`skill-eng-security`).

---

## Actionable Technology Rules

### DOTNET-SEC-001: ASP.NET Core JWT Bearer Validation Flaws
- **Applies To**: `JwtBearerOptions`, `TokenValidationParameters`, `Program.cs`.
- **Behavior**: Disabling security validation flags (`ValidateIssuer = false`, `ValidateAudience = false`) allows forged or expired JWT tokens.
- **Inspect**: `TokenValidationParameters` properties set to `false` in authentication setup.
- **Violation**:
  ```csharp
  builder.Services.AddAuthentication().AddJwtBearer(o => {
      o.TokenValidationParameters = new TokenValidationParameters { ValidateIssuer = false, ValidateAudience = false };
  });
  ```
- **Evidence**: Setting `ValidateIssuer`, `ValidateAudience`, or `ValidateLifetime` to `false`.
- **False Positives**: Internal microservices behind an API gateway that terminates and validates JWTs upstream.
- **Remediation**: Enable all token validation flags and bind parameters to configuration settings.
- **Engineering Skill Map**: `SEC01`, `SEC04`

---

### DOTNET-SEC-002: Authorization Bypass & Missing [Authorize] Guards
- **Applies To**: ASP.NET Core controllers, Minimal APIs (`MapPost`, `MapDelete`).
- **Behavior**: Exposing sensitive mutation endpoints without `[Authorize]` or `.RequireAuthorization()` allows unauthenticated access.
- **Inspect**: Controller actions or Minimal API routes lacking authorization policies and unintended `[AllowAnonymous]`.
- **Violation**: `app.MapDelete("/api/users/{id}", async (int id, UserDbContext db) => { ... }); // Missing authorization!`
- **Evidence**: Sensitive endpoint signature lacking `[Authorize]` attributes or `.RequireAuthorization()`.
- **False Positives**: Explicit public endpoints (`/healthz`, `/login`) or global `FallbackPolicy` requiring authentication by default.
- **Remediation**: Attach explicit authorization requirements (`.RequireAuthorization("AdminPolicy")` or `[Authorize]`).
- **Engineering Skill Map**: `SEC02`, `SEC05`

---

### DOTNET-SEC-003: Mass Assignment & Model Binding Overposting
- **Applies To**: ASP.NET Core model binding, controllers, Minimal APIs, EF Core entities.
- **Behavior**: Accepting raw EF Core entities as action parameters allows clients to bind internal fields (`IsAdmin: true`).
- **Inspect**: Public controller actions accepting DB entity types directly in parameter signatures.
- **Violation**:
  ```csharp
  [HttpPost] public async Task<IActionResult> UpdateProfile([FromBody] User user) { // Overposting risk!
      _db.Users.Update(user); await _db.SaveChangesAsync(); return Ok();
  }
  ```
- **Evidence**: Action method parameter accepting a raw EF Core entity mapped to database tables.
- **False Positives**: Action parameters using dedicated request DTOs with explicit client-editable fields.
- **Remediation**: Bind dedicated request DTO records (`public record UpdateProfileRequest(...)`) and map properties explicitly.
- **Engineering Skill Map**: `SEC03`, `SEC07`

---

### DOTNET-SEC-004: EF Core SQL Injection via FromSqlRaw & Concatenation
- **Applies To**: `FromSqlRaw`, `ExecuteSqlRaw`, raw SQL queries in EF Core.
- **Behavior**: Concatenating strings (`"WHERE Name = '" + input + "'"` ) into raw SQL queries executes unsanitized user input.
- **Inspect**: Invocations of `FromSqlRaw` or `ExecuteSqlRaw` using string concatenation `+` or string interpolation `$"..."`.
- **Violation**: `_db.Users.FromSqlRaw("SELECT * FROM Users WHERE Username = '" + input + "'"); // SQL Injection!`
- **Evidence**: `FromSqlRaw` call site where the SQL parameter is dynamically concatenated with non-parameterized strings.
- **False Positives**: Using `FromSqlInterpolated` which automatically parameterizes C# interpolated strings `$"..."`.
- **Remediation**: Use `FromSqlInterpolated` or explicit `SqlParameter` arrays.
- **Engineering Skill Map**: `SEC03`, `SEC06`

---

### DOTNET-SEC-005: Permissive CORS & Transport Security Flaws
- **Applies To**: `app.UseCors()`, `app.UseHsts()`, `app.UseHttpsRedirection()`.
- **Behavior**: Configuring CORS with `.AllowAnyOrigin()` alongside credentials exposes APIs to unauthorized cross-origin calls.
- **Inspect**: CORS definitions containing `AllowAnyOrigin()` and pipeline missing `app.UseHsts()`.
- **Violation**: `builder.Services.AddCors(o => o.AddPolicy("All", p => p.AllowAnyOrigin().AllowAnyMethod()));`
- **Evidence**: CORS policy containing `.AllowAnyOrigin()` on authenticated API endpoints.
- **False Positives**: Public open APIs designed explicitly for cross-origin access without ambient cookies/credentials.
- **Remediation**: Restrict origins to explicitly configured domain arrays (`WithOrigins(allowedOrigins)`).
- **Engineering Skill Map**: `SEC08`, `SEC09`

---

### DOTNET-SEC-006: Hardcoded Secrets & Plaintext Credentials
- **Applies To**: `appsettings.json`, C# source code, `IDataProtectionProvider`.
- **Behavior**: Storing passwords, API keys, or connection strings in source code risks credential leaks.
- **Inspect**: Hardcoded secret strings (`"sk_live_12345..."`) or plaintext database connection strings in `.csproj`/`.cs`.
- **Violation**: `public class TokenService { private const string SecretKey = "HardcodedSecretKeyValueInCode"; }`
- **Evidence**: Hardcoded high-entropy secret string inside source code or committed configuration files.
- **False Positives**: Dummy placeholder keys in `appsettings.Development.json` or sample test configurations.
- **Remediation**: Inject settings via `IConfiguration` backed by Environment Variables, User Secrets, or Key Vault.
- **Engineering Skill Map**: `SEC10`, `SEC11`
