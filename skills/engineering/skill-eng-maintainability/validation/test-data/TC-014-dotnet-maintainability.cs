// TC-014: .NET Maintainability (MAINT05, MAINT14)
// Demonstrates .NET captive dependency anti-pattern and tight coupling vs. clean DI registration

using System;
using System.Threading.Tasks;

namespace EnterpriseApp.Services
{
    public interface IScopedTenantContext
    {
        string TenantId { get; set; }
    }

    public class ScopedTenantContext : IScopedTenantContext
    {
        public string TenantId { get; set; } = "default";
    }

    // --- VIOLATION ---
    // VIOLATION: Captive dependency (MAINT14 / MAINT05).
    // Singleton service directly holds a reference to a Scoped tenant dependency,
    // causing cross-tenant data leaks and concurrency bugs.
    public class GlobalCacheServiceViolation
    {
        private readonly IScopedTenantContext _tenantContext; // VIOLATION: Scoped dependency in Singleton

        public GlobalCacheServiceViolation(IScopedTenantContext tenantContext)
        {
            _tenantContext = tenantContext;
        }

        public string GetCacheKey(string itemKey)
        {
            return $"{_tenantContext.TenantId}:{itemKey}";
        }
    }

    // --- SAFE IMPLEMENTATION ---
    public interface ITenantContextProvider
    {
        string GetCurrentTenantId();
    }

    public class GlobalCacheServiceSafe
    {
        private readonly ITenantContextProvider _provider;

        public GlobalCacheServiceSafe(ITenantContextProvider provider)
        {
            _provider = provider;
        }

        public string GetCacheKey(string itemKey)
        {
            return $"{_provider.GetCurrentTenantId()}:{itemKey}";
        }
    }
}

