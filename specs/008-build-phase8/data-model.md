# build-phase8: Data Model

## Advanced Analytics Entities

### AnalyticsEvent
- `event_id`: UUID (primary key)
- `event_type`: string (e.g., "page_view", "button_click", "api_call")
- `user_id`: UUID (optional, anonymous user identifier)
- `service`: string (service generating the event)
- `endpoint`: string (API endpoint path)
- `timestamp`: datetime (auto-now)
- `metadata`: JSONB (arbitrary key-value pairs)

### AIModelMetrics
- `model_id`: UUID (primary key)
- `model_name`: string (e.g., "anomaly_detection_v1")
- `accuracy`: float (validation accuracy percentage)
- `precision`: float (precision score)
- `recall`: float (recall score)
- `training_timestamp`: datetime (when model was trained)
- `validity_until`: datetime (when model becomes stale)
- `features_used`: JSONB (list of feature names used for prediction)

### PartnerIntegration
- `integration_id`: UUID (primary key)
- `partner_name`: string (e.g., "partner_abc")
- `api_endpoint`: string (partner API endpoint URL)
- `auth_method`: string (e.g., "OAuth2.0", "API Key")
- `status`: string (e.g., "active", "inactive", "pending")
- `last_contact`: datetime (when partner system last communicated)
- `metadata`: JSONB (partner-specific configuration details)

### ComplianceReport
- `report_id`: UUID (primary key)
- `report_type`: string (e.g., "SOC2", "GDPR", "CCPA")
- `period_start`: datetime (reporting period start)
- `period_end`: datetime (reporting period end)
- `generated_at`: datetime (when report was generated)
- `summary`: text (high-level compliance summary)
- `details`: JSONB (detailed compliance data)

### FeatureFlag
- `flag_id`: UUID (primary key)
- `flag_name`: string (e.g., "new_checkout_flow")
- `is_active`: boolean (whether the feature is currently enabled)
- `rollout_percentage`: integer (0–100, rollout progress)
- `created_at`: datetime (when flag was created)
- `updated_at`: datetime (when flag was last updated)
- `rollback_token`: string (token for instant rollback)

## Relationships
- **AnalyticsEvent → PartnerIntegration**: Many-to-Many (partner events can be associated with partner integrations; a partner can receive events from multiple services)
- **AnalyticsEvent → ComplianceReport**: Many-to-Many (events can be included in compliance reports; reports can include events from various time ranges)
- **PartnerIntegration → ComplianceReport**: Many-to-Many (partner data can be included in compliance reports; reports can include partner data)
- **FeatureFlag → AnalyticsEvent**: Many-to-Many (feature flags can affect which events are tracked; events can be associated with feature flags)

## Indexes
- `UNIQUE` on `AnalyticsEvent.event_id`
- `UNIQUE` on `AIModelMetrics.model_id`
- `UNIQUE` on `PartnerIntegration.integration_id`
- `UNIQUE` on `ComplianceReport.report_id`
- `UNIQUE` on `FeatureFlag.flag_id`
- Index on `AnalyticsEvent.service`
- Index on `AnalyticsEvent.timestamp`
- Index on `AIModelMetrics.model_name`
- Index on `PartnerIntegration.partner_name`
- Index on `ComplianceReport.period_start`
- Index on `FeatureFlag.is_active`

## JSON Schemas (for API integration)

```json
{
  "AnalyticsEvent": {
    "type": "object",
    "required": ["event_type", "service", "timestamp"],
    "properties": {
      "event_id": {"type": "string", "format": "uuid"},
      "event_type": {"type": "string"},
      "user_id": {"type": "string", "format": "uuid"},
      "service": {"type": "string"},
      "endpoint": {"type": "string"},
      "timestamp": {"type": "string", "format": "date-time"},
      "metadata": {"type": "object"}
    }
  },
  "AIModelMetrics": {
    "type": "object",
    "required": ["model_name", "accuracy", "precision", "recall", "training_timestamp"],
    "properties": {
      "model_id": {"type": "string", "format": "uuid"},
      "model_name": {"type": "string"},
      "accuracy": {"type": "float"},
      "precision": {"type": "float"},
      "recall": {"type": "float"},
      "training_timestamp": {"type": "string", "format": "date-time"},
      "validity_until": {"type": "string", "format": "date-time"},
      "features_used": {"type": "array", "items": {"type": "string"}}
    }
  },
  "PartnerIntegration": {
    "type": "object",
    "required": ["partner_name", "api_endpoint", "auth_method", "status"],
    "properties": {
      "integration_id": {"type": "string", "format": "uuid"},
      "partner_name": {"type": "string"},
      "api_endpoint": {"type": "string"},
      "auth_method": {"type": "string"},
      "status": {"type": "string"},
      "last_contact": {"type": "string", "format": "date-time"},
      "metadata": {"type": "object"}
    }
  },
  "ComplianceReport": {
    "type": "object",
    "required": ["report_type", "period_start", "period_end", "generated_at", "summary"],
    "properties": {
      "report_id": {"type": "string", "format": "uuid"},
      "report_type": {"type": "string"},
      "period_start": {"type": "string", "format": "date-time"},
      "period_end": {"type": "string", "format": "date-time"},
      "generated_at": {"type": "string", "format": "date-time"},
      "summary": {"type": "string"},
      "details": {"type": "object"}
    }
  },
  "FeatureFlag": {
    "type": "object",
    "required": ["flag_name", "is_active", "rollout_percentage"],
    "properties": {
      "flag_id": {"type": "string", "format": "uuid"},
      "flag_name": {"type": "string"},
      "is_active": {"type": "boolean"},
      "rollout_percentage": {"type": "integer"},
      "created_at": {"type": "string", "format": "date-time"},
      "updated_at": {"type": "string", "format": "date-time"},
      "rollback_token": {"type": "string"}
    }
  }
}
```
