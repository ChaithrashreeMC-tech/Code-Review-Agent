using System;
using Microsoft.Extensions.DependencyInjection;

namespace DotNetReview.TestFixtures.Modularity;

public class AppDbContext { }

// Violation: Captive dependency - Singleton holding Scoped AppDbContext captive
public class CaptiveDependencyViolation
{
    private readonly AppDbContext _db;

    public CaptiveDependencyViolation(AppDbContext db)
    {
        _db = db;
    }

    public void Execute()
    {
        Console.WriteLine(_db.ToString());
    }
}

// Safe Counterpart: Singleton using IServiceScopeFactory
public class SafeScopeFactoryPattern
{
    private readonly IServiceScopeFactory _scopeFactory;

    public SafeScopeFactoryPattern(IServiceScopeFactory scopeFactory)
    {
        _scopeFactory = scopeFactory;
    }

    public void Execute()
    {
        using var scope = _scopeFactory.CreateScope();
        var db = scope.ServiceProvider.GetRequiredService<AppDbContext>();
        Console.WriteLine(db.ToString());
    }
}

