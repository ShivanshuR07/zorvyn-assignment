export type Role = "viewer" | "analyst" | "admin";
export type UserState = "active" | "inactive" | "suspended";
export type RecordType = "income" | "expense";
export type TrendPeriod = "weekly" | "monthly";
export type TrendTypeFilter = "all" | "income" | "expense";

export interface AuthUser {
  id: string;
  full_name: string;
  email: string;
  role: Role;
  state: UserState;
  is_active: boolean;
  created_at?: string;
  updated_at?: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: "bearer";
  user: AuthUser;
}

export interface ErrorPayload {
  detail: {
    code: string;
    message: string;
    errors?: Array<Record<string, unknown>>;
  };
}

export interface PagedResponse<T> {
  items: T[];
  total: number;
  limit: number;
  offset: number;
}

export interface FinancialRecord {
  id: string;
  amount: string;
  type: RecordType;
  category: string;
  record_date: string;
  notes: string | null;
  created_by: string;
  created_at: string;
  updated_at: string;
}

export interface SummaryReport {
  total_income: string;
  total_expense: string;
  net_balance: string;
}

export interface CategoryBreakdownItem {
  category: string;
  type: RecordType;
  total: string;
}

export interface CategoryBreakdownResponse {
  items: CategoryBreakdownItem[];
}

export interface TrendPoint {
  period: TrendPeriod;
  period_start: string;
  total_income: string;
  total_expense: string;
  net_balance: string;
}

export interface TrendResponse {
  items: TrendPoint[];
}

export interface RecentActivityResponse {
  items: FinancialRecord[];
}

export interface RoleDefinition {
  name: Role;
  permissions: string[];
}

export interface UserCreatePayload {
  full_name: string;
  email: string;
  password: string;
  role: Role;
  state: UserState;
}

export interface UserUpdatePayload {
  full_name?: string;
  password?: string;
  role?: Role;
  state?: UserState;
}

export interface RecordCreatePayload {
  amount: string;
  type: RecordType;
  category: string;
  record_date: string;
  notes: string;
}

export interface RecordUpdatePayload {
  amount?: string;
  type?: RecordType;
  category?: string;
  record_date?: string;
  notes?: string;
}
