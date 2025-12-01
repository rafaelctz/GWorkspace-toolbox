"""
API retry logic inspired by GAM (Google Apps Manager)
Handles transient errors, SSL issues, and connection problems with exponential backoff
"""
import time
import random
from typing import Callable, Any
from googleapiclient.errors import HttpError
import ssl


class APIRetryHandler:
    """Handles API retries with exponential backoff, inspired by GAM"""

    # HTTP status codes that should be retried
    RETRY_STATUS_CODES = {
        403,  # Rate limit exceeded, user rate limit exceeded
        429,  # Too many requests
        500,  # Internal server error
        502,  # Bad gateway
        503,  # Service unavailable
        504,  # Gateway timeout
    }

    # Retry reasons from Google API errors
    RETRY_REASONS = {
        'rateLimitExceeded',
        'userRateLimitExceeded',
        'backendError',
        'internalError',
    }

    # SSL errors that should trigger retry
    SSL_ERRORS = (
        ssl.SSLError,
        ConnectionResetError,
        ConnectionAbortedError,
        BrokenPipeError,
    )

    def __init__(self, max_retries: int = 5, base_delay: float = 1.0):
        """
        Initialize retry handler

        Args:
            max_retries: Maximum number of retry attempts
            base_delay: Base delay in seconds for exponential backoff
        """
        self.max_retries = max_retries
        self.base_delay = base_delay

    def execute_with_retry(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute a function with automatic retry on transient errors

        Args:
            func: The function to execute
            *args: Positional arguments for the function
            **kwargs: Keyword arguments for the function

        Returns:
            The result of the function call

        Raises:
            Exception: If all retries are exhausted
        """
        last_error = None

        for attempt in range(self.max_retries + 1):
            try:
                return func(*args, **kwargs)

            except HttpError as e:
                last_error = e

                # Check if this error should be retried
                if not self._should_retry_http_error(e):
                    raise

                if attempt < self.max_retries:
                    delay = self._calculate_backoff(attempt, e)
                    print(f"[APIRetry] HTTP {e.resp.status} error, retrying in {delay:.1f}s (attempt {attempt + 1}/{self.max_retries})")
                    time.sleep(delay)
                else:
                    print(f"[APIRetry] Max retries exhausted for HTTP error: {str(e)}")
                    raise

            except self.SSL_ERRORS as e:
                last_error = e

                if attempt < self.max_retries:
                    delay = self._calculate_backoff(attempt)
                    print(f"[APIRetry] SSL/Connection error, retrying in {delay:.1f}s (attempt {attempt + 1}/{self.max_retries}): {type(e).__name__}")
                    time.sleep(delay)
                else:
                    print(f"[APIRetry] Max retries exhausted for SSL/Connection error: {str(e)}")
                    raise

            except Exception as e:
                # For 'NoneType' errors and other unexpected errors
                if "'NoneType' object has no attribute" in str(e):
                    last_error = e
                    if attempt < self.max_retries:
                        delay = self._calculate_backoff(attempt)
                        print(f"[APIRetry] NoneType error (service may need recreation), retrying in {delay:.1f}s (attempt {attempt + 1}/{self.max_retries})")
                        time.sleep(delay)
                    else:
                        print(f"[APIRetry] Max retries exhausted for NoneType error")
                        raise
                else:
                    # Don't retry other exceptions
                    raise

        # This shouldn't be reached, but just in case
        raise last_error if last_error else Exception("Unknown retry error")

    def _should_retry_http_error(self, error: HttpError) -> bool:
        """Check if an HTTP error should be retried"""
        status_code = error.resp.status

        # Check status code
        if status_code in self.RETRY_STATUS_CODES:
            return True

        # Check error reason
        try:
            error_details = error.error_details
            if isinstance(error_details, list):
                for detail in error_details:
                    if detail.get('reason') in self.RETRY_REASONS:
                        return True
        except:
            pass

        return False

    def _calculate_backoff(self, attempt: int, error: HttpError = None) -> float:
        """
        Calculate backoff delay using exponential backoff with jitter
        Inspired by GAM's retry logic
        """
        # Check if the error includes a Retry-After header
        if error and hasattr(error, 'resp') and 'Retry-After' in error.resp:
            try:
                retry_after = int(error.resp['Retry-After'])
                return retry_after
            except:
                pass

        # Exponential backoff: base_delay * (2 ^ attempt)
        delay = self.base_delay * (2 ** attempt)

        # Add jitter (random variation) to prevent thundering herd
        jitter = random.uniform(0, delay * 0.1)

        # Cap at 60 seconds maximum
        return min(delay + jitter, 60.0)
