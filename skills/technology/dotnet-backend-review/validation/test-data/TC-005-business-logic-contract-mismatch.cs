namespace DotNetReview.TestFixtures.BusinessLogic;

public class ApiResponse
{
    public bool Success { get; set; }
    public string Error { get; set; } = string.Empty;
}

public class ProblemDetails
{
    public string Title { get; set; } = string.Empty;
    public string Detail { get; set; } = string.Empty;
}

public class Http200ErrorPayloadMismatch
{
    // Violation: Returning HTTP 200 OK with success=false payload for validation failure
    public ApiResponse Checkout(decimal amount)
    {
        if (amount <= 0)
        {
            return new ApiResponse { Success = false, Error = "Amount must be positive" };
        }
        return new ApiResponse { Success = true };
    }
}

public class SafeProblemDetailsContract
{
    // Safe Counterpart: Standard ProblemDetails response for invalid domain input
    public ProblemDetails Checkout(decimal amount)
    {
        if (amount <= 0)
        {
            return new ProblemDetails { Title = "Invalid Amount", Detail = "Amount must be positive" };
        }
        return new ProblemDetails { Title = "Success" };
    }
}

