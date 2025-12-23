# Role Management API Documentation

Complete API documentation for the new flexible role management system in Bocah Cafe API.

## Overview

The new role system allows you to:
- Create custom roles with descriptions
- Assign roles to users (admins)
- System roles (superadmin, writer) are protected from deletion/modification
- Role-based access control (RBAC) for all endpoints

## Base URL

```
http://localhost:8000/api/roles
```

## Authentication

All endpoints require:
- Header: `Authorization: Bearer YOUR_TOKEN`
- Role: `superadmin` (only superadmins can manage roles)

---

## Role Model

```json
{
  "id": 1,
  "name": "Super Admin",
  "slug": "superadmin",
  "description": "Full system access with all permissions",
  "is_system_role": true,
  "created_at": "2024-01-15T10:30:00",
  "updated_at": null
}
```

**Fields:**
- `id` - Unique role identifier
- `name` - Human-readable role name
- `slug` - URL-friendly identifier (lowercase, alphanumeric with hyphens)
- `description` - Role description/purpose
- `is_system_role` - Boolean indicating if this is a protected system role
- `created_at` - Creation timestamp
- `updated_at` - Last update timestamp

---

## Endpoints

### 1. List All Roles

Get paginated list of all roles with optional filtering.

**Endpoint:** `GET /api/roles/`

**Query Parameters:**
- `page` (optional, default: 1) - Page number
- `page_size` (optional, default: 10, max: 100) - Items per page
- `name` (optional) - Filter by role name (case-insensitive partial match)
- `slug` (optional) - Filter by slug (case-insensitive partial match)
- `include_system` (optional, default: true) - Include system roles in results

**Example Request:**

```bash
# Get all roles
curl -X GET "http://localhost:8000/api/roles/" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Filter by name
curl -X GET "http://localhost:8000/api/roles/?name=admin" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Exclude system roles
curl -X GET "http://localhost:8000/api/roles/?include_system=false" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response (200 OK):**

```json
{
  "data": [
    {
      "id": 1,
      "name": "Super Admin",
      "slug": "superadmin",
      "description": "Full system access with all permissions",
      "is_system_role": true,
      "created_at": "2024-01-15T10:30:00",
      "updated_at": null
    },
    {
      "id": 2,
      "name": "Writer",
      "slug": "writer",
      "description": "Can create and manage content",
      "is_system_role": true,
      "created_at": "2024-01-15T10:30:05",
      "updated_at": null
    },
    {
      "id": 3,
      "name": "Content Moderator",
      "slug": "content-moderator",
      "description": "Can moderate and approve content",
      "is_system_role": false,
      "created_at": "2024-01-16T14:20:00",
      "updated_at": null
    }
  ],
  "meta": {
    "total": 3,
    "page": 1,
    "page_size": 10,
    "total_pages": 1
  }
}
```

---

### 2. Get Single Role

Get role details by ID.

**Endpoint:** `GET /api/roles/{role_id}`

**Example Request:**

```bash
curl -X GET "http://localhost:8000/api/roles/1" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response (200 OK):**

```json
{
  "id": 1,
  "name": "Super Admin",
  "slug": "superadmin",
  "description": "Full system access with all permissions",
  "is_system_role": true,
  "created_at": "2024-01-15T10:30:00",
  "updated_at": null
}
```

**Error Response (404 Not Found):**

```json
{
  "detail": "Role not found"
}
```

---

### 3. Get Role by Slug

Get role details by slug (alternative to ID-based lookup).

**Endpoint:** `GET /api/roles/slug/{slug}`

**Example Request:**

```bash
curl -X GET "http://localhost:8000/api/roles/slug/superadmin" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response:** Same as "Get Single Role"

---

### 4. Create Role

Create a new custom role.

**Endpoint:** `POST /api/roles/`

**Request Body:**

```json
{
  "name": "Content Moderator",
  "slug": "content-moderator",
  "description": "Can moderate and approve user-submitted content"
}
```

**Field Requirements:**
- `name` (required) - 2-50 characters
- `slug` (required) - 2-50 characters, lowercase alphanumeric with hyphens only
- `description` (optional) - Max 500 characters

**Example Request:**

```bash
curl -X POST "http://localhost:8000/api/roles/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Content Moderator",
    "slug": "content-moderator",
    "description": "Can moderate and approve content"
  }'
```

**Response (201 Created):**

```json
{
  "id": 3,
  "name": "Content Moderator",
  "slug": "content-moderator",
  "description": "Can moderate and approve content",
  "is_system_role": false,
  "created_at": "2024-01-16T14:20:00",
  "updated_at": null
}
```

**Error Responses:**

- `400 Bad Request` - Validation error

```json
{
  "detail": "Role name already exists"
}
```

```json
{
  "detail": "Role slug already exists"
}
```

```json
{
  "detail": "Slug must be lowercase alphanumeric with hyphens only"
}
```

---

### 5. Update Role

Update an existing role (name, slug, or description).

**Endpoint:** `PUT /api/roles/{role_id}`

**Request Body:**

```json
{
  "name": "Senior Content Moderator",
  "description": "Senior moderator with extended permissions"
}
```

**Fields (all optional):**
- `name` - New role name
- `slug` - New slug
- `description` - New description

**Example Request:**

```bash
curl -X PUT "http://localhost:8000/api/roles/3" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Senior Content Moderator",
    "description": "Senior moderator with extended permissions"
  }'
```

**Response (200 OK):**

```json
{
  "id": 3,
  "name": "Senior Content Moderator",
  "slug": "content-moderator",
  "description": "Senior moderator with extended permissions",
  "is_system_role": false,
  "created_at": "2024-01-16T14:20:00",
  "updated_at": "2024-01-17T09:15:00"
}
```

**Error Responses:**

- `404 Not Found` - Role not found
- `400 Bad Request` - Cannot update system roles

```json
{
  "detail": "Cannot update system roles"
}
```

---

### 6. Delete Role

Delete a role by ID.

**Endpoint:** `DELETE /api/roles/{role_id}`

**Example Request:**

```bash
curl -X DELETE "http://localhost:8000/api/roles/3" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response:** `204 No Content`

**Error Responses:**

- `404 Not Found` - Role not found
- `400 Bad Request` - Cannot delete system roles

```json
{
  "detail": "Cannot delete system roles"
}
```

- `400 Bad Request` - Role is in use

```json
{
  "detail": "Cannot delete role. 5 admin(s) are currently assigned to this role"
}
```

---

## System Roles

Two system roles are created automatically during migration:

### 1. Super Admin
- **Slug:** `superadmin`
- **Description:** Full system access with all permissions
- **Protected:** Cannot be deleted or modified
- **Default assignment:** First admin account

### 2. Writer
- **Slug:** `writer`
- **Description:** Can create and manage content
- **Protected:** Cannot be deleted or modified
- **Default assignment:** New admins (if not specified)

---

## Usage with Admin Management

When creating or updating admins, you now use `role_id` instead of hardcoded role strings:

### Create Admin with Role

```bash
# First, get available roles
curl -X GET "http://localhost:8000/api/roles/" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Then create admin with specific role_id
curl -X POST "http://localhost:8000/api/admin/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "moderator1",
    "password": "password123",
    "role_id": 3
  }'
```

### Update Admin Role

```bash
curl -X PATCH "http://localhost:8000/api/admin/5/role" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "role_id": 3
  }'
```

---

## Complete Workflow Example

### Scenario: Creating a custom "Content Moderator" role and assigning it

```bash
# 1. Login as superadmin
TOKEN=$(curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' \
  | jq -r '.access_token')

# 2. List existing roles
curl -X GET "http://localhost:8000/api/roles/" \
  -H "Authorization: Bearer $TOKEN"

# 3. Create new "Content Moderator" role
ROLE_RESPONSE=$(curl -X POST "http://localhost:8000/api/roles/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Content Moderator",
    "slug": "content-moderator",
    "description": "Can moderate and approve user content"
  }')

ROLE_ID=$(echo $ROLE_RESPONSE | jq -r '.id')
echo "Created role with ID: $ROLE_ID"

# 4. Create new admin with moderator role
curl -X POST "http://localhost:8000/api/admin/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"username\": \"moderator1\",
    \"password\": \"mod123\",
    \"role_id\": $ROLE_ID
  }"

# 5. Verify the new admin
curl -X GET "http://localhost:8000/api/admin/" \
  -H "Authorization: Bearer $TOKEN"

# 6. Update role description
curl -X PUT "http://localhost:8000/api/roles/$ROLE_ID" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Senior moderator with content approval permissions"
  }'

# 7. Get role by slug
curl -X GET "http://localhost:8000/api/roles/slug/content-moderator" \
  -H "Authorization: Bearer $TOKEN"
```

---

## Migration from Old System

Run the migration script to upgrade from the old string-based role system:

```bash
cd bocah-cafe-be
python migrate_to_role_system.py
```

This will:
1. Create the `roles` table
2. Create default system roles (superadmin, writer)
3. Migrate all existing admins to use `role_id`
4. Remove the old `role` column from admins table

---

## Frontend Integration

Update your frontend API client:

```typescript
// lib/api.ts

export interface Role {
  id: number;
  name: string;
  slug: string;
  description?: string;
  is_system_role: boolean;
  created_at?: string;
  updated_at?: string;
}

export interface AdminResponse {
  id: number;
  username: string;
  role: Role;  // Now a full role object, not just a string
  created_at?: string;
}

// Get all roles
export async function getRoles(params?: {
  page?: number;
  page_size?: number;
  name?: string;
  slug?: string;
  include_system?: boolean;
}): Promise<PaginatedResponse<Role>> {
  const token = getAuthToken();
  const searchParams = new URLSearchParams();
  if (params?.page) searchParams.set('page', params.page.toString());
  if (params?.page_size) searchParams.set('page_size', params.page_size.toString());
  if (params?.name) searchParams.set('name', params.name);
  if (params?.slug) searchParams.set('slug', params.slug);
  if (params?.include_system !== undefined) {
    searchParams.set('include_system', params.include_system.toString());
  }

  const url = `${API_BASE}/api/roles/?${searchParams}`;
  const response = await fetch(url, {
    headers: { Authorization: `Bearer ${token}` }
  });
  return handleResponse<PaginatedResponse<Role>>(response);
}

// Create role
export async function createRole(role: {
  name: string;
  slug: string;
  description?: string;
}): Promise<Role> {
  const token = getAuthToken();
  const response = await fetch(`${API_BASE}/api/roles/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`
    },
    body: JSON.stringify(role)
  });
  return handleResponse<Role>(response);
}

// Update role
export async function updateRole(id: number, updates: {
  name?: string;
  slug?: string;
  description?: string;
}): Promise<Role> {
  const token = getAuthToken();
  const response = await fetch(`${API_BASE}/api/roles/${id}`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`
    },
    body: JSON.stringify(updates)
  });
  return handleResponse<Role>(response);
}

// Delete role
export async function deleteRole(id: number): Promise<void> {
  const token = getAuthToken();
  const response = await fetch(`${API_BASE}/api/roles/${id}`, {
    method: 'DELETE',
    headers: { Authorization: `Bearer ${token}` }
  });
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'An error occurred' }));
    throw new Error(error.detail || `HTTP error! status: ${response.status}`);
  }
}
```

---

## Security Considerations

1. **System Role Protection:** System roles (superadmin, writer) cannot be deleted or modified
2. **Role In-Use Protection:** Roles assigned to admins cannot be deleted
3. **Superadmin Required:** All role management endpoints require superadmin access
4. **Slug Validation:** Role slugs must be lowercase alphanumeric with hyphens
5. **Unique Constraints:** Both role names and slugs must be unique

---

## Error Codes Summary

| Status Code | Description |
|-------------|-------------|
| 200 OK | Request successful |
| 201 Created | Role created successfully |
| 204 No Content | Role deleted successfully |
| 400 Bad Request | Validation error or business logic error |
| 401 Unauthorized | Invalid or expired token |
| 403 Forbidden | Not a superadmin |
| 404 Not Found | Role not found |

---

## Testing with Swagger UI

Access the interactive API documentation at:
```
http://localhost:8000/docs
```

All role management endpoints are under the **"Role Management"** section.
