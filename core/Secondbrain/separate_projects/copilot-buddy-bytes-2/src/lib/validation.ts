import { z } from "zod";

// =====================================================
// COMPREHENSIVE INPUT VALIDATION SCHEMAS
// =====================================================

// Common validation patterns
const emailSchema = z
  .string()
  .trim()
  .email({ message: "Invalid email address" })
  .max(255, { message: "Email must be less than 255 characters" });

const phoneSchema = z
  .string()
  .trim()
  .regex(/^[+]?[(]?[0-9]{1,4}[)]?[-\s\.]?[(]?[0-9]{1,4}[)]?[-\s\.]?[0-9]{1,9}$/, {
    message: "Invalid phone number format",
  })
  .optional();

const urlSchema = z
  .string()
  .trim()
  .url({ message: "Invalid URL format" })
  .max(2048, { message: "URL must be less than 2048 characters" })
  .optional();

const uuidSchema = z
  .string()
  .uuid({ message: "Invalid UUID format" });

// Text field validation with length limits
const createTextSchema = (fieldName: string, maxLength: number = 1000, required: boolean = true) => {
  const base = z.string().trim().max(maxLength, { 
    message: `${fieldName} must be less than ${maxLength} characters` 
  });
  return required 
    ? base.min(1, { message: `${fieldName} is required` })
    : base.optional();
};

// =====================================================
// USER & AUTHENTICATION SCHEMAS
// =====================================================

export const userProfileSchema = z.object({
  full_name: createTextSchema("Full name", 100),
  email: emailSchema,
  department: createTextSchema("Department", 50, false),
  job_title: createTextSchema("Job title", 100, false),
  phone: phoneSchema,
});

export const changePasswordSchema = z.object({
  current_password: z.string().min(8, { message: "Password must be at least 8 characters" }),
  new_password: z
    .string()
    .min(8, { message: "Password must be at least 8 characters" })
    .regex(/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]/, {
      message: "Password must contain uppercase, lowercase, number, and special character",
    }),
  confirm_password: z.string(),
}).refine((data) => data.new_password === data.confirm_password, {
  message: "Passwords don't match",
  path: ["confirm_password"],
});

// =====================================================
// COMPLIANCE SCHEMAS
// =====================================================

export const complianceEvidenceSchema = z.object({
  control_id: uuidSchema,
  evidence_type: z.enum(["document", "screenshot", "log", "attestation", "automated"]),
  evidence_data: z.record(z.any()),
  description: createTextSchema("Description", 2000),
  collected_by: uuidSchema,
  status: z.enum(["draft", "pending_review", "approved", "rejected"]),
});

export const complianceFrameworkSchema = z.object({
  framework_code: createTextSchema("Framework code", 50),
  framework_name: createTextSchema("Framework name", 200),
  version: createTextSchema("Version", 20, false),
  industry: createTextSchema("Industry", 100),
  description: createTextSchema("Description", 2000, false),
});

// =====================================================
// CMDB & CHANGE MANAGEMENT SCHEMAS
// =====================================================

export const configurationItemSchema = z.object({
  ci_name: createTextSchema("CI name", 200),
  ci_type: z.enum(["server", "workstation", "network_device", "application", "database", "service", "other"]),
  ci_subtype: createTextSchema("CI subtype", 100, false),
  serial_number: createTextSchema("Serial number", 100, false),
  asset_tag: createTextSchema("Asset tag", 50, false),
  ip_address: z.string().ip({ version: "v4", message: "Invalid IPv4 address" }).optional(),
  mac_address: z.string().regex(/^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$/, {
    message: "Invalid MAC address format",
  }).optional(),
  hostname: createTextSchema("Hostname", 255, false),
  location: createTextSchema("Location", 200, false),
  department: createTextSchema("Department", 100, false),
  criticality: z.enum(["low", "medium", "high", "critical"]).optional(),
});

export const changeRequestSchema = z.object({
  title: createTextSchema("Title", 200),
  description: createTextSchema("Description", 5000),
  change_type: z.enum(["normal", "standard", "emergency"]),
  priority: z.enum(["low", "medium", "high", "critical"]),
  risk_level: z.enum(["low", "medium", "high"]),
  justification: createTextSchema("Justification", 2000),
  implementation_plan: createTextSchema("Implementation plan", 5000),
  rollback_plan: createTextSchema("Rollback plan", 5000),
  testing_plan: createTextSchema("Testing plan", 5000, false),
  affected_ci_ids: z.array(uuidSchema).optional(),
  estimated_downtime_minutes: z.number().int().min(0).max(10080).optional(), // Max 1 week
  affected_users: z.number().int().min(0).optional(),
  requested_start_time: z.string().datetime().optional(),
  requested_end_time: z.string().datetime().optional(),
});

// =====================================================
// NETWORK & SECURITY SCHEMAS
// =====================================================

export const networkDeviceSchema = z.object({
  device_name: createTextSchema("Device name", 200),
  device_type: z.enum(["router", "switch", "firewall", "access_point", "load_balancer", "other"]),
  ip_address: z.string().ip({ version: "v4", message: "Invalid IPv4 address" }),
  location: createTextSchema("Location", 200, false),
  snmp_community: createTextSchema("SNMP community", 100, false),
  snmp_version: z.enum(["v1", "v2c", "v3"]).optional(),
  polling_interval: z.number().int().min(30).max(3600).optional(), // 30s to 1hr
});

export const networkAlertRuleSchema = z.object({
  rule_name: createTextSchema("Rule name", 200),
  metric_type: z.enum(["cpu", "memory", "disk", "network", "temperature", "custom"]),
  operator: z.enum(["greater_than", "less_than", "equals", "not_equals"]),
  threshold: z.number().min(0).max(100),
  severity: z.enum(["info", "warning", "critical"]),
  notification_channels: z.array(z.string()).optional(),
  enabled: z.boolean(),
});

// =====================================================
// CLIENT PORTAL & TICKETS SCHEMAS
// =====================================================

export const clientTicketSchema = z.object({
  subject: createTextSchema("Subject", 200),
  description: createTextSchema("Description", 5000),
  category: z.enum(["technical_support", "billing", "feature_request", "incident", "other"]),
  priority: z.enum(["low", "medium", "high", "urgent"]),
});

export const ticketResponseSchema = z.object({
  ticket_id: uuidSchema,
  response_text: createTextSchema("Response", 5000),
  is_internal_note: z.boolean().optional(),
});

// =====================================================
// WORKFLOW & AUTOMATION SCHEMAS
// =====================================================

export const workflowSchema = z.object({
  workflow_name: createTextSchema("Workflow name", 200),
  description: createTextSchema("Description", 1000, false),
  workflow_type: z.enum(["compliance", "change_management", "incident_response", "onboarding", "custom"]),
  trigger_type: z.enum(["manual", "scheduled", "event", "webhook"]),
  workflow_definition: z.record(z.any()),
  is_active: z.boolean(),
});

// =====================================================
// SANITIZATION UTILITIES
// =====================================================

/**
 * Sanitize user input to prevent XSS attacks
 * Use this before rendering user-provided content
 */
export const sanitizeText = (input: string): string => {
  return input
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#x27;")
    .replace(/\//g, "&#x2F;");
};

/**
 * Encode data for use in URL parameters
 */
export const encodeForUrl = (data: Record<string, any>): string => {
  return Object.entries(data)
    .map(([key, value]) => `${encodeURIComponent(key)}=${encodeURIComponent(String(value))}`)
    .join("&");
};

/**
 * Validate and sanitize file uploads
 */
export const validateFile = (file: File, maxSizeMB: number = 10, allowedTypes: string[] = []) => {
  const errors: string[] = [];
  
  // Check file size
  const maxBytes = maxSizeMB * 1024 * 1024;
  if (file.size > maxBytes) {
    errors.push(`File size must be less than ${maxSizeMB}MB`);
  }
  
  // Check file type
  if (allowedTypes.length > 0 && !allowedTypes.includes(file.type)) {
    errors.push(`File type must be one of: ${allowedTypes.join(", ")}`);
  }
  
  // Check file name for malicious patterns
  const dangerousPatterns = /[<>:"|?*\x00-\x1f]/g;
  if (dangerousPatterns.test(file.name)) {
    errors.push("File name contains invalid characters");
  }
  
  return {
    isValid: errors.length === 0,
    errors,
  };
};

/**
 * Rate limiting helper for API calls
 */
export class RateLimiter {
  private timestamps: number[] = [];
  
  constructor(
    private maxRequests: number,
    private windowMs: number
  ) {}
  
  isAllowed(): boolean {
    const now = Date.now();
    this.timestamps = this.timestamps.filter(t => now - t < this.windowMs);
    
    if (this.timestamps.length < this.maxRequests) {
      this.timestamps.push(now);
      return true;
    }
    
    return false;
  }
  
  getResetTime(): number {
    if (this.timestamps.length === 0) return 0;
    return this.timestamps[0] + this.windowMs;
  }
}
