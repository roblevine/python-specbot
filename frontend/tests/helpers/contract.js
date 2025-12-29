import { writeFileSync, readFileSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';
import yaml from 'js-yaml';

// Load OpenAPI specification
const __dirname = dirname(fileURLToPath(import.meta.url));
const openapiPath = join(__dirname, '../../../specs/003-backend-api-loopback/contracts/message-api.yaml');
const openapiSpec = yaml.load(readFileSync(openapiPath, 'utf8'));

/**
 * Normalize dynamic data in request body for stable snapshots
 * Replaces UUIDs and timestamps with stable placeholders
 *
 * @param {object} data - The request body data
 * @returns {object} - Normalized data with stable values
 */
export function normalizeRequest(data) {
  if (!data) return data;

  // Convert to string for regex replacements
  let str = JSON.stringify(data);

  // Normalize conversation IDs (conv-UUID format)
  str = str.replace(
    /conv-[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}/gi,
    'conv-00000000-0000-0000-0000-000000000000'
  );

  // Normalize ISO-8601 timestamps
  str = str.replace(
    /\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z/g,
    '2025-01-01T00:00:00.000Z'
  );

  return JSON.parse(str);
}

/**
 * Validate request against OpenAPI specification
 *
 * @param {string} operationId - The OpenAPI operation ID (e.g., 'sendMessage')
 * @param {object} request - The HTTP request object {method, path, headers, body}
 * @returns {object} - Validation result {valid: boolean, errors: string[]}
 */
export function validateRequest(operationId, request) {
  const errors = [];

  // Find the operation in OpenAPI spec
  const operation = findOperation(operationId);
  if (!operation) {
    errors.push(`Operation '${operationId}' not found in OpenAPI specification`);
    return { valid: false, errors };
  }

  // Validate HTTP method
  if (request.method.toUpperCase() !== operation.method.toUpperCase()) {
    errors.push(`Expected method ${operation.method}, got ${request.method}`);
  }

  // Validate path
  if (request.path !== operation.path) {
    errors.push(`Expected path ${operation.path}, got ${request.path}`);
  }

  // Validate request body if operation requires it
  if (operation.requestBody && operation.requestBody.required) {
    if (!request.body) {
      errors.push('Request body is required but not provided');
    } else {
      // Validate request body against schema
      const schema = operation.requestBody.content['application/json']?.schema;
      if (schema) {
        const bodyErrors = validateSchema(request.body, schema);
        errors.push(...bodyErrors);
      }
    }
  }

  return {
    valid: errors.length === 0,
    errors
  };
}

/**
 * Find operation in OpenAPI spec by operationId
 *
 * @param {string} operationId - The operation ID to find
 * @returns {object|null} - Operation object with {method, path, requestBody, responses}
 */
function findOperation(operationId) {
  for (const [path, pathItem] of Object.entries(openapiSpec.paths)) {
    for (const [method, operation] of Object.entries(pathItem)) {
      if (operation.operationId === operationId) {
        return {
          method: method.toUpperCase(),
          path,
          requestBody: operation.requestBody,
          responses: operation.responses
        };
      }
    }
  }
  return null;
}

/**
 * Validate data against JSON schema
 * Simple validation for required fields and types
 *
 * @param {object} data - The data to validate
 * @param {object} schema - The JSON schema
 * @returns {string[]} - Array of validation errors (empty if valid)
 */
function validateSchema(data, schema) {
  const errors = [];

  // Resolve $ref if present
  if (schema.$ref) {
    const refPath = schema.$ref.replace('#/components/schemas/', '');
    schema = openapiSpec.components.schemas[refPath];
  }

  // Check required fields
  if (schema.required) {
    for (const field of schema.required) {
      if (!(field in data)) {
        errors.push(`Required field '${field}' is missing`);
      }
    }
  }

  // Validate field types and constraints
  if (schema.properties) {
    for (const [field, fieldSchema] of Object.entries(schema.properties)) {
      if (field in data) {
        const value = data[field];

        // Type validation
        if (fieldSchema.type === 'string' && typeof value !== 'string') {
          errors.push(`Field '${field}' must be a string`);
        }

        // String constraints
        if (fieldSchema.type === 'string' && typeof value === 'string') {
          if (fieldSchema.minLength && value.length < fieldSchema.minLength) {
            errors.push(`Field '${field}' must have at least ${fieldSchema.minLength} characters`);
          }
          if (fieldSchema.maxLength && value.length > fieldSchema.maxLength) {
            errors.push(`Field '${field}' must have at most ${fieldSchema.maxLength} characters`);
          }
          if (fieldSchema.pattern && !new RegExp(fieldSchema.pattern).test(value)) {
            errors.push(`Field '${field}' does not match pattern: ${fieldSchema.pattern}`);
          }
        }
      }
    }
  }

  return errors;
}

/**
 * Capture contract snapshot for a request
 * Validates request against OpenAPI spec and writes snapshot file
 *
 * @param {string} operationId - The OpenAPI operation ID
 * @param {object} request - The HTTP request object {method, path, headers, body}
 * @throws {Error} - If validation fails
 */
export async function captureSnapshot(operationId, request) {
  // Validate request against OpenAPI spec
  const validation = validateRequest(operationId, request);
  if (!validation.valid) {
    throw new Error(
      `Request validation failed for operation '${operationId}':\n` +
      validation.errors.map(e => `  - ${e}`).join('\n')
    );
  }

  // Normalize dynamic data in request body
  const normalizedRequest = {
    ...request,
    body: normalizeRequest(request.body)
  };

  // Build snapshot object
  const snapshot = {
    metadata: {
      operationId,
      capturedAt: new Date().toISOString(),
      frontendVersion: '1.0.0'
    },
    request: normalizedRequest
  };

  // Write snapshot to file
  const snapshotDir = join(__dirname, '../../../tests/contract-snapshots');
  const snapshotPath = join(snapshotDir, `${operationId}.json`);

  writeFileSync(snapshotPath, JSON.stringify(snapshot, null, 2));

  console.log(`✓ Contract snapshot captured: ${operationId}.json`);
}
