using System.Threading.Tasks;

namespace DotNetReview.TestFixtures.Performance;

public interface IDataService
{
    Task<string> GetDataAsync();
}

public class SyncOverAsyncBlocking
{
    private readonly IDataService _dataService;
    public SyncOverAsyncBlocking(IDataService dataService) => _dataService = dataService;

    // Violation: Task.GetAwaiter().GetResult() blocks execution thread
    public string FetchData()
    {
        return _dataService.GetDataAsync().GetAwaiter().GetResult();
    }
}

public class SafeAsyncAwaitPattern
{
    private readonly IDataService _dataService;
    public SafeAsyncAwaitPattern(IDataService dataService) => _dataService = dataService;

    // Safe Counterpart: Proper async/await non-blocking call
    public async Task<string> FetchDataAsync()
    {
        return await _dataService.GetDataAsync();
    }
}

