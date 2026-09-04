LOGIN_SUCCESS = "User authenticated successfully."
LOGOUT_SUCCESS = "User logged out successfully."
INVALID_CREDENTIALS = "Invalid username/email or password."
UNAUTHORIZED_ACCESS = "Authentication credentials were not provided or invalid."
PERMISSION_DENIED = "You do not have administrative permission to perform this action."

TRIGGER_CREATED_SUCCESS = "Notification trigger created successfully."
TRIGGER_UPDATED_SUCCESS = "Notification trigger updated successfully."
TRIGGER_NOT_FOUND = "Notification trigger not found."
TRIGGER_CODE_EXISTS = "A trigger with this code already exists."

TEMPLATE_CREATED_SUCCESS = "Notification template created successfully."
TEMPLATE_UPDATED_SUCCESS = "Notification template updated successfully."
TEMPLATE_DELETED_SUCCESS = "Notification template deleted successfully."
TEMPLATE_TOGGLED_SUCCESS = "Notification template toggle status updated successfully."
TEMPLATE_NOT_FOUND = "Notification template not found."
TEMPLATE_UNIQUE_CONSTRAINT_ERROR = "A template for this trigger and channel already exists."
INVALID_CHANNEL_CHOICE = "Invalid notification channel specified."
INVALID_TEMPLATE_STATUS = "Invalid template status specified."

TEST_SEND_INITIATED = "Test notification dispatch initiated successfully."
TEST_SEND_FAILED = "Test notification dispatch failed."
TEST_RECIPIENT_REQUIRED = "Recipient address/phone/player_id is required for test send."

WEBPUSH_SUBSCRIPTION_SUCCESS = "Web push subscription saved successfully."
WEBPUSH_SUBSCRIPTION_REQUIRED = "Subscription endpoint or player ID is required."

MISSING_REQUIRED_VARIABLES = "Missing required template variable(s): "
INVALID_VARIABLE_SYNTAX = "Template body contains malformed variable tags."

PROVIDER_DELIVERY_SUCCESS = "Notification delivered successfully via provider."
PROVIDER_DELIVERY_FAILED = "Notification delivery failed via provider."
PROVIDER_DISABLED_SKIPPED = "Notification channel is disabled for this trigger. Skipping delivery."
