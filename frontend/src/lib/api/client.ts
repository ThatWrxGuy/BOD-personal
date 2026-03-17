// API Client Configuration

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

export interface ApiError {
  message: string;
  type: string;
  statusCode: number;
  retryable: boolean;
  source: string;
}

export interface ApiResponse<T> {
  data?: T;
  error?: ApiError;
}

class ApiClient {
  private baseUrl: string;
  private token: string | null = null;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  setToken(token: string | null) {
    this.token = token;
  }

  private getHeaders(): HeadersInit {
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
    };
    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }
    return headers;
  }

  private async handleResponse<T>(response: Response): Promise<ApiResponse<T>> {
    // Handle HTML responses (upstream failures)
    const contentType = response.headers.get('content-type');
    if (contentType?.includes('text/html')) {
      const text = await response.text();
      if (text.includes('<!DOCTYPE html>') || text.includes('<html')) {
        // This is an HTML error page - sanitize it
        console.error('[API] Received HTML response instead of JSON:', text.substring(0, 200));
        return {
          error: {
            message: 'Upstream service temporarily unavailable. Please try again.',
            type: 'upstream_html_response',
            statusCode: response.status,
            retryable: true,
            source: 'api_client',
          },
        };
      }
    }

    if (!response.ok) {
      let errorMessage = `Request failed with status ${response.status}`;
      try {
        const errorData = await response.json();
        errorMessage = errorData.detail || errorData.message || errorMessage;
      } catch {
        // If we can't parse JSON, use text
        try {
          const errorText = await response.text();
          if (errorText && !errorText.includes('<!DOCTYPE html>')) {
            errorMessage = errorText;
          }
        } catch {
          // Ignore
        }
      }

      return {
        error: {
          message: errorMessage,
          type: 'api_error',
          statusCode: response.status,
          retryable: response.status >= 500 || response.status === 429,
          source: 'api_client',
        },
      };
    }

    try {
      const data = await response.json();
      return { data };
    } catch {
      return { data: undefined as T };
    }
  }

  async get<T>(endpoint: string): Promise<ApiResponse<T>> {
    try {
      const response = await fetch(`${this.baseUrl}${endpoint}`, {
        method: 'GET',
        headers: this.getHeaders(),
      });
      return this.handleResponse<T>(response);
    } catch (error) {
      return {
        error: {
          message: error instanceof Error ? error.message : 'Network error',
          type: 'network_error',
          statusCode: 0,
          retryable: true,
          source: 'api_client',
        },
      };
    }
  }

  async post<T>(endpoint: string, body?: unknown): Promise<ApiResponse<T>> {
    try {
      const response = await fetch(`${this.baseUrl}${endpoint}`, {
        method: 'POST',
        headers: this.getHeaders(),
        body: body ? JSON.stringify(body) : undefined,
      });
      return this.handleResponse<T>(response);
    } catch (error) {
      return {
        error: {
          message: error instanceof Error ? error.message : 'Network error',
          type: 'network_error',
          statusCode: 0,
          retryable: true,
          source: 'api_client',
        },
      };
    }
  }

  async put<T>(endpoint: string, body?: unknown): Promise<ApiResponse<T>> {
    try {
      const response = await fetch(`${this.baseUrl}${endpoint}`, {
        method: 'PUT',
        headers: this.getHeaders(),
        body: body ? JSON.stringify(body) : undefined,
      });
      return this.handleResponse<T>(response);
    } catch (error) {
      return {
        error: {
          message: error instanceof Error ? error.message : 'Network error',
          type: 'network_error',
          statusCode: 0,
          retryable: true,
          source: 'api_client',
        },
      };
    }
  }

  async patch<T>(endpoint: string, body?: unknown): Promise<ApiResponse<T>> {
    try {
      const response = await fetch(`${this.baseUrl}${endpoint}`, {
        method: 'PATCH',
        headers: this.getHeaders(),
        body: body ? JSON.stringify(body) : undefined,
      });
      return this.handleResponse<T>(response);
    } catch (error) {
      return {
        error: {
          message: error instanceof Error ? error.message : 'Network error',
          type: 'network_error',
          statusCode: 0,
          retryable: true,
          source: 'api_client',
        },
      };
    }
  }

  async delete<T>(endpoint: string): Promise<ApiResponse<T>> {
    try {
      const response = await fetch(`${this.baseUrl}${endpoint}`, {
        method: 'DELETE',
        headers: this.getHeaders(),
      });
      return this.handleResponse<T>(response);
    } catch (error) {
      return {
        error: {
          message: error instanceof Error ? error.message : 'Network error',
          type: 'network_error',
          statusCode: 0,
          retryable: true,
          source: 'api_client',
        },
      };
    }
  }
}

// Singleton instance
export const apiClient = new ApiClient();

// Helper to update token from store
export function updateApiToken(token: string | null) {
  apiClient.setToken(token);
}
