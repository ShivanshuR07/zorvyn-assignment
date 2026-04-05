import type {
  AuthUser,
  CategoryBreakdownResponse,
  ErrorPayload,
  FinancialRecord,
  LoginResponse,
  PagedResponse,
  RecentActivityResponse,
  RecordCreatePayload,
  RecordUpdatePayload,
  RoleDefinition,
  SummaryReport,
  TrendPeriod,
  TrendResponse,
  TrendTypeFilter,
  UserCreatePayload,
  UserUpdatePayload,
} from "../types/api";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init.headers ?? {}),
    },
  });

  if (!response.ok) {
    const fallback = {
      detail: {
        code: "unknown_error",
        message: "Something went wrong while contacting the API.",
      },
    } satisfies ErrorPayload;

    const error = (await response.json().catch(() => fallback)) as ErrorPayload;
    throw new Error(error.detail.message);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return (await response.json()) as T;
}

function authHeaders(token: string) {
  return {
    Authorization: `Bearer ${token}`,
  };
}

export const api = {
  baseUrl: API_BASE_URL,
  login(email: string, password: string) {
    return request<LoginResponse>("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    });
  },
  me(token: string) {
    return request<AuthUser>("/auth/me", {
      headers: authHeaders(token),
    });
  },
  summary(token: string) {
    return request<SummaryReport>("/dashboard/summary", {
      headers: authHeaders(token),
    });
  },
  categoryBreakdown(token: string) {
    return request<CategoryBreakdownResponse>("/dashboard/category-breakdown", {
      headers: authHeaders(token),
    });
  },
  trends(token: string, period: TrendPeriod, type: TrendTypeFilter) {
    return request<TrendResponse>(`/dashboard/trends?period=${period}&type=${type}`, {
      headers: authHeaders(token),
    });
  },
  recentActivity(token: string) {
    return request<RecentActivityResponse>("/reports/recent-activity?limit=8", {
      headers: authHeaders(token),
    });
  },
  users(token: string) {
    return request<PagedResponse<AuthUser>>("/users?limit=50&offset=0", {
      headers: authHeaders(token),
    });
  },
  createUser(token: string, payload: UserCreatePayload) {
    return request<AuthUser>("/users", {
      method: "POST",
      headers: authHeaders(token),
      body: JSON.stringify(payload),
    });
  },
  updateUser(token: string, userId: string, payload: UserUpdatePayload) {
    return request<AuthUser>(`/users/${userId}`, {
      method: "PATCH",
      headers: authHeaders(token),
      body: JSON.stringify(payload),
    });
  },
  updateUserState(token: string, userId: string, state: string) {
    return request<AuthUser>(`/users/${userId}/state`, {
      method: "PATCH",
      headers: authHeaders(token),
      body: JSON.stringify({ state }),
    });
  },
  deleteUser(token: string, userId: string) {
    return request<void>(`/users/${userId}`, {
      method: "DELETE",
      headers: authHeaders(token),
    });
  },
  roles(token: string) {
    return request<RoleDefinition[]>("/roles", {
      headers: authHeaders(token),
    });
  },
  records(token: string, queryString = "") {
    return request<PagedResponse<FinancialRecord>>(`/financial-records${queryString}`, {
      headers: authHeaders(token),
    });
  },
  createRecord(token: string, payload: RecordCreatePayload) {
    return request<FinancialRecord>("/financial-records", {
      method: "POST",
      headers: authHeaders(token),
      body: JSON.stringify(payload),
    });
  },
  updateRecord(token: string, recordId: string, payload: RecordUpdatePayload) {
    return request<FinancialRecord>(`/financial-records/${recordId}`, {
      method: "PATCH",
      headers: authHeaders(token),
      body: JSON.stringify(payload),
    });
  },
  deleteRecord(token: string, recordId: string) {
    return request<void>(`/financial-records/${recordId}`, {
      method: "DELETE",
      headers: authHeaders(token),
    });
  },
};
