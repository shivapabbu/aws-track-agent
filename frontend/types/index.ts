export interface Agent {
  name: string
  running: boolean
  last_check_time?: string
  status: Record<string, any>
}

export interface AgentStatus {
  orchestrator: {
    name: string
    running: boolean
    agents_count: number
  }
  agents: {
    cloudtrail: Agent
    cost: Agent
  }
}

export interface DashboardStats {
  cloudtrail: {
    suspicious_events: number
    running: boolean
    last_check: string | null
  }
  cost: {
    anomalies: number
    running: boolean
    last_check: string | null
  }
  timestamp: string
}

export interface CloudTrailEvent {
  event_id?: string
  event_time?: string
  event_name?: string
  event_source?: string
  aws_region?: string
  source_ip?: string
  user_agent?: string
  user_identity?: {
    type?: string
    principal_id?: string
    arn?: string
    account_id?: string
    user_name?: string
  }
  resources?: any[]
  request_parameters?: Record<string, any>
  response_elements?: Record<string, any>
  error_code?: string
  error_message?: string
  read_only?: boolean
  management_event?: boolean
}

export interface CostAnomaly {
  anomaly_id?: string
  anomaly_score?: any
  impact?: {
    TotalImpact?: {
      Amount?: string
    }
  }
  root_cause?: string[]
  monitor_arn?: string
  dimension_value?: string
  feedback?: string
  status?: string
}
