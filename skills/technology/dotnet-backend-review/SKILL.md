---
name: dotnet-backend-review
description: >-
  Activate when reviewing .NET backend code, C# source files, ASP.NET Core controllers
  or Minimal APIs, Entity Framework Core (EF Core) data access, Dependency Injection registrations,
  LINQ queries, or .NET async/await execution. Provides C#, ASP.NET Core, EF Core, and .NET runtime
  technology guidance to specialist engineering review agents.
---

# .NET Backend Review Technology Skill

## 1. Purpose & Scope

Provides C# language semantics, ASP.NET Core framework mechanics, Entity Framework Core (EF Core) persistence behavior, and .NET runtime execution rules for Code Review Agent workflows.

**Activate when** code changes modify `.cs`, `.csproj`, `appsettings.json`, `Program.cs`, ASP.NET Core controllers/Minimal APIs, EF Core `DbContext` configurations, LINQ database queries, dependency injection setups, background workers, or NuGet package manifests.

## 2. Progressive Disclosure & Agent Selective Loading

This skill separates technology knowledge into five independent reference files. Each specialist review agent consumes **only** the reference corresponding to its review dimension:

| Specialist Review Agent | Engineering Skill | .NET Reference File |
|---|---|---|
| **Modularity Agent** | `skill-eng-modularity` | [`references/modularity.md`](references/modularity.md) |
| **Maintainability Agent** | `skill-eng-maintainability` | [`references/maintainability.md`](references/maintainability.md) |
| **Performance Agent** | `skill-eng-performance` | [`references/performance.md`](references/performance.md) |
| **Security Agent** | `skill-eng-security` | [`references/security.md`](references/security.md) |
| **Business Logic Agent** | `skill-eng-business-logic` | [`references/business-logic.md`](references/business-logic.md) |

### Selective Loading Contract for Orchestration
- Agents MUST load only their assigned dimension reference file during single-dimension review runs.
- Do NOT load all reference files into a single agent prompt context unless cross-dimensional analysis is explicitly commanded by the orchestrator.
- The engineering skills define evaluation principles and scorecard schemas; this technology skill provides framework mechanics and concrete detection rules.

## 3. Technology Guidance vs. Engineering Scoring

- **Technology Skill Responsibility**: Define C#, ASP.NET Core, and EF Core execution mechanics, detection rules (`DOTNET-MOD-001`–`DOTNET-BIZ-006`), false-positive safeguards, and code evidence requirements.
- **Engineering Skill Responsibility**: Evaluate architectural impact, calculate dimension scores (0.0–10.0 scale), enforce deduction formulas, and format findings in the Scorecard Aggregator schema.
- This technology skill does **not** override general engineering scoring rubrics or generate a separate numeric score.

## 4. Version Awareness & Target Framework Detection

Inspect project manifests (`.csproj`, `Directory.Build.props`, `global.json`, `packages.lock.json`) to detect the active .NET runtime version and C# language level before evaluating code:

- **.NET 6 / 7 (LTS / STS)**: C# 10/11 features, Minimal API introduction, EF Core 6/7 compiled models.
- **.NET 8 / 9 (LTS / Modern)**: C# 12/13 features (Primary constructors, Collection expressions, `ref struct` generics), Native AOT compatibility, Keyed services (`[FromKeyedServices]`), Frozen collections, EF Core 8/9 complex types.

*Rule Applicability Guardrail*: Do NOT recommend APIs or syntax unsupported by the repository's target framework (`<TargetFramework>`).

## 5. Supporting References & Validation

- **Modularity Reference**: [`references/modularity.md`](references/modularity.md)
- **Maintainability Reference**: [`references/maintainability.md`](references/maintainability.md)
- **Performance Reference**: [`references/performance.md`](references/performance.md)
- **Security Reference**: [`references/security.md`](references/security.md)
- **Business Logic Reference**: [`references/business-logic.md`](references/business-logic.md)
- **Validation Suite**: [`validation/test-suite.json`](validation/test-suite.json)

