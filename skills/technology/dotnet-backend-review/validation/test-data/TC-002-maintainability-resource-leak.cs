using System.IO;
using System.Threading.Tasks;

namespace DotNetReview.TestFixtures.Maintainability;

public class UnmanagedResourceLeak
{
    // Violation: FileStream instantiated without using declaration
    public async Task<byte[]> ReadFileUnsafeAsync(string path)
    {
        var stream = File.OpenRead(path);
        var buffer = new byte[stream.Length];
        await stream.ReadAsync(buffer, 0, buffer.Length);
        return buffer;
    }
}

public class SafeUsingDeclaration
{
    // Safe Counterpart: Disposable resource managed with await using
    public async Task<byte[]> ReadFileSafeAsync(string path)
    {
        await using var stream = File.OpenRead(path);
        var buffer = new byte[stream.Length];
        await stream.ReadAsync(buffer, 0, buffer.Length);
        return buffer;
    }
}

