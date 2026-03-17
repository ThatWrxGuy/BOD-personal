import { apiClient } from './client';

// Types
export interface User {
  id: string;
  email: string;
  username: string;
  status: string;
  created_at: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  username: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
}

export interface OnboardingRequest {
  email: string;
  username: string;
  password: string;
  life_stage?: string;
  top_goals?: string[];
  major_stressors?: string[];
  finance_rating?: number;
  health_rating?: number;
  career_rating?: number;
  relationships_rating?: number;
  intelligence_rating?: number;
  life_architecture_rating?: number;
  operating_style?: string;
  planning_horizon_days?: number;
}

// API Functions
export const authApi = {
  login: async (data: LoginRequest): Promise<{ access_token: string } | null> => {
    const formData = new URLSearchParams();
    formData.append('username', data.email);
    formData.append('password', data.password);
    
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'}/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: formData,
    });
    
    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Login failed' }));
      throw new Error(error.detail || 'Login failed');
    }
    
    return response.json();
  },
  
  register: async (data: RegisterRequest): Promise<User> => {
    const result = await apiClient.post<User>('/auth/register', data);
    if (result.error) {
      throw new Error(result.error.message);
    }
    return result.data!;
  },
  
  onboard: async (data: OnboardingRequest): Promise<{ user: User; token: TokenResponse }> => {
    const result = await apiClient.post<{ user: User; token: TokenResponse }>('/auth/onboard', data);
    if (result.error) {
      throw new Error(result.error.message);
    }
    return result.data!;
  },
  
  me: async (): Promise<User> => {
    const result = await apiClient.get<User>('/auth/me');
    if (result.error) {
      throw new Error(result.error.message);
    }
    return result.data!;
  },
  
  logout: async (): Promise<void> => {
    await apiClient.post('/auth/logout');
  },
};
