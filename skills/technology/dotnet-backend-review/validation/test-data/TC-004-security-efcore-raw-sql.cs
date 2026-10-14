using System.Collections.Generic;
using System.Threading.Tasks;

namespace DotNetReview.TestFixtures.Security;

public class User { public string Username { get; set; } = string.Empty; }

public class DummySet
{
    public Task<List<User>> FromSqlRaw(string sql) => Task.FromResult(new List<User>());
    public Task<List<User>> FromSqlInterpolated(System.FormattableString sql) => Task.FromResult(new List<User>());
}

public class UnsafeRawSqlInjection
{
    private readonly DummySet _users = new();

    // Violation: String concatenation in FromSqlRaw causes SQL injection
    public async Task<List<User>> SearchUsersAsync(string userInput)
    {
        string rawQuery = "SELECT * FROM Users WHERE Username = '" + userInput + "'";
        return await _users.FromSqlRaw(rawQuery);
    }
}

public class SafeSqlInterpolatedPattern
{
    private readonly DummySet _users = new();

    // Safe Counterpart: FromSqlInterpolated creates parameterized SQL
    public async Task<List<User>> SearchUsersAsync(string userInput)
    {
        return await _users.FromSqlInterpolated($"SELECT * FROM Users WHERE Username = {userInput}");
    }
}

