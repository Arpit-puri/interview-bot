import httpx
import os
import time
import asyncio
import json
from typing import List, Dict, Any
from collections import deque
from config.constants import OPENROUTER_API_URL, DEFAULT_MODEL, DEFAULT_TEMPERATURE, DEFAULT_MAX_TOKENS

class RateLimitExceeded(Exception):
    """Custom exception for rate limit exceeded"""
    pass

class AIService:
    def __init__(self):
        self.api_key = os.getenv('OPENROUTER_API_KEY')
        self.api_url = OPENROUTER_API_URL
        self.model = DEFAULT_MODEL
        self.temperature = DEFAULT_TEMPERATURE
        self.max_tokens = DEFAULT_MAX_TOKENS
        
        # Rate limiting: 10 requests per minute
        self.max_requests_per_minute = 10
        self.request_timestamps = deque()
        
        # Timeout settings
        self.request_timeout = 30.0
        
        # Retry Configuration
        self.max_retries = 3                    # Maximum number of retry attempts
        self.base_delay = 1.0                   # Base delay between retries (seconds)
        self.max_delay = 60.0                   # Maximum delay between retries
        self.backoff_factor = 2.0               # Exponential backoff multiplier
        
        # Which HTTP status codes should trigger a retry
        self.retryable_status_codes = {
            429,  # Too Many Requests
            500,  # Internal Server Error
            502,  # Bad Gateway
            503,  # Service Unavailable
            504,  # Gateway Timeout
        }
    
    def _check_rate_limit(self):
        current_time = time.time()
        
        while self.request_timestamps and current_time - self.request_timestamps[0] > 60:
            self.request_timestamps.popleft()
        
        if len(self.request_timestamps) >= self.max_requests_per_minute:
            raise RateLimitExceeded("Rate limit exceeded. Please try again in a moment.")
        
        self.request_timestamps.append(current_time)
    
    def _calculate_retry_delay(self, attempt: int) -> float:
        delay = self.base_delay * (self.backoff_factor ** attempt)
        return min(delay, self.max_delay)
    
    def _is_retryable_error(self, exception) -> bool:
        if isinstance(exception, RateLimitExceeded):
            return False  # Don't retry our own rate limiting
        
        if isinstance(exception, httpx.TimeoutException):
            return True  # Retry timeouts
        
        if isinstance(exception, httpx.HTTPStatusError):
            return exception.response.status_code in self.retryable_status_codes
        
        if isinstance(exception, httpx.RequestError):
            return True  # Retry network errors
        
        return False  # Don't retry other errors
    
    async def _make_request_with_retry(self, headers: dict, payload: dict) -> dict:
        last_exception = None
        
        for attempt in range(self.max_retries + 1):  # 0, 1, 2, 3 (4 total attempts)
            try:
                async with httpx.AsyncClient(timeout=self.request_timeout) as client:
                    response = await client.post(self.api_url, headers=headers, json=payload)
                    response.raise_for_status()
                    return response.json()  # Success! Return the response
                    
            except Exception as e:
                last_exception = e
                
                # If this is the last attempt, don't retry
                if attempt == self.max_retries:
                    break
                
                # Check if this error is worth retrying
                if not self._is_retryable_error(e):
                    break  # Don't retry non-retryable errors
                
                # Calculate delay before next attempt
                delay = self._calculate_retry_delay(attempt)
                
                # Log the retry attempt (in production, use proper logging)
                print(f"Request failed (attempt {attempt + 1}/{self.max_retries + 1}): {str(e)}")
                print(f"Retrying in {delay} seconds...")
                
                # Wait before retrying
                await asyncio.sleep(delay)
        
        # If we get here, all retry attempts failed
        # Re-raise the last exception with context about retries
        if isinstance(last_exception, httpx.TimeoutException):
            raise Exception("Request timed out after multiple attempts. Please try again later.")
        elif isinstance(last_exception, httpx.HTTPStatusError):
            if last_exception.response.status_code == 429:
                raise RateLimitExceeded("API rate limit exceeded after multiple attempts. Please try again in a moment.")
            elif last_exception.response.status_code >= 500:
                raise Exception("Service temporarily unavailable after multiple attempts. Please try again later.")
            else:
                raise Exception(f"API request failed after retries: {last_exception.response.status_code}")
        elif isinstance(last_exception, httpx.RequestError):
            raise Exception("Network error persisted after multiple attempts. Please check your connection and try again.")
        else:
            raise Exception("Request failed after multiple attempts. Please try again later.")
    
    async def generate_response(self, messages: List[Dict[str, str]], phase_context: str = None) -> str:
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY not found in environment variables")
        
        # Check rate limit before making request
        try:
            self._check_rate_limit()
        except RateLimitExceeded:
            raise RateLimitExceeded("Too many requests. Please wait a moment before trying again.")
        
        # Add phase context to system prompt if provided
        enhanced_messages = messages.copy()
        if phase_context and len(enhanced_messages) > 0 and enhanced_messages[0]["role"] == "system":
            enhanced_messages[0]["content"] += f"\n\n{phase_context}"
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": enhanced_messages,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens
        }

        try:
            # Use the retry mechanism
            response_json = await self._make_request_with_retry(headers, payload)
            return response_json["choices"][0]["message"]["content"]
            
        except ValueError as e:  # API key missing
            raise e  # Re-raise as-is
        except RateLimitExceeded as e:  # Rate limiting
            raise e  # Re-raise as-is
        except Exception as e:  # All other errors (already processed by retry logic)
            raise e  # Re-raise the final error from retry attempts

    async def stream_response(self, messages: List[Dict[str, str]], phase_context: str = None):
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY not found in environment variables")
        
        # Check rate limit before making request
        try:
            self._check_rate_limit()
        except RateLimitExceeded:
            raise RateLimitExceeded("Too many requests. Please wait a moment before trying again.")
        
        # Add phase context to system prompt if provided
        enhanced_messages = messages.copy()
        if phase_context and len(enhanced_messages) > 0 and enhanced_messages[0]["role"] == "system":
            enhanced_messages[0]["content"] += f"\n\n{phase_context}"
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": enhanced_messages,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "stream": True
        }

        # Retry logic for establishing the streaming connection
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                async with httpx.AsyncClient(timeout=self.request_timeout) as client:
                    async with client.stream("POST", self.api_url, headers=headers, json=payload) as response:
                        response.raise_for_status()
                        
                        # Connection established successfully, start streaming
                        async for line in response.aiter_lines():
                            if not line or not line.startswith("data:"):
                                continue
                            data = line[len("data: "):]
                            if data.strip() == "[DONE]":
                                break
                            try:
                                chunk = json.loads(data)
                                delta = chunk["choices"][0]["delta"].get("content", "")
                                if delta:
                                    yield delta
                            except Exception:
                                continue
                        
                        # If we get here, streaming completed successfully
                        return
                        
            except Exception as e:
                last_exception = e
                
                # If this is the last attempt, don't retry
                if attempt == self.max_retries:
                    break
                
                # Check if this error is worth retrying
                if not self._is_retryable_error(e):
                    break
                
                # Only retry if we haven't started yielding tokens yet
                # (In practice, this retry only helps with connection establishment)
                delay = self._calculate_retry_delay(attempt)
                print(f"Streaming connection failed (attempt {attempt + 1}/{self.max_retries + 1}): {str(e)}")
                print(f"Retrying in {delay} seconds...")
                await asyncio.sleep(delay)
        
        # If we get here, all retry attempts failed
        if isinstance(last_exception, httpx.TimeoutException):
            raise Exception("Streaming request timed out after multiple attempts. Please try again later.")
        elif isinstance(last_exception, httpx.HTTPStatusError):
            if last_exception.response.status_code == 429:
                raise RateLimitExceeded("API rate limit exceeded for streaming. Please try again in a moment.")
            elif last_exception.response.status_code >= 500:
                raise Exception("Streaming service temporarily unavailable. Please try again later.")
            else:
                raise Exception(f"Streaming request failed: {last_exception.response.status_code}")
        elif isinstance(last_exception, httpx.RequestError):
            raise Exception("Network error prevented streaming. Please check your connection and try again.")
        else:
            raise Exception("Streaming failed after multiple attempts. Please try again later.")

# Global AI service instance
ai_service = AIService()
