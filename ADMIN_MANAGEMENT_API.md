# Admin Management API Documentation

API untuk mengelola admin users dan roles. **Semua endpoint memerlukan autentikasi dengan role superadmin**.

## Base URL

```
http://localhost:8000/api/admin
```

## Authentication

Semua endpoint memerlukan:

- Header: `Authorization: Bearer YOUR_TOKEN`
- Role: `superadmin`

Jika tidak memiliki role superadmin, akan mendapat response `403 Forbidden`.

---

## Endpoints

### 1. Get All Admins (List)

Mendapatkan daftar semua admin dengan pagination dan filtering.

**Endpoint:** `GET /api/admin/`

**Query Parameters:**

- `page` (optional, default: 1) - Nomor halaman
- `page_size` (optional, default: 10, max: 100) - Jumlah item per halaman
- `username` (optional) - Filter berdasarkan username (case-insensitive partial match)
- `role` (optional) - Filter berdasarkan role (`superadmin` atau `writer`)

**Request Example:**

```bash
# Get all admins (page 1, 10 items)
curl -X GET "http://localhost:8000/api/admin/" \
  -H "Authorization: Bearer YOUR_TOKEN"

# With filtering and pagination
curl -X GET "http://localhost:8000/api/admin/?page=1&page_size=20&role=superadmin" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Filter by username
curl -X GET "http://localhost:8000/api/admin/?username=john" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response Example (200 OK):**

```json
{
  "data": [
    {
      "id": 1,
      "username": "admin",
      "role": "superadmin",
      "created_at": "2024-01-15T10:30:00"
    },
    {
      "id": 2,
      "username": "writer1",
      "role": "writer",
      "created_at": "2024-01-16T14:20:00"
    }
  ],
  "meta": {
    "total": 2,
    "page": 1,
    "page_size": 10,
    "total_pages": 1
  }
}
```

---

### 2. Get Single Admin

Mendapatkan detail admin berdasarkan ID.

**Endpoint:** `GET /api/admin/{admin_id}`

**Path Parameters:**

- `admin_id` (required) - ID admin

**Request Example:**

```bash
curl -X GET "http://localhost:8000/api/admin/1" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response Example (200 OK):**

```json
{
  "id": 1,
  "username": "admin",
  "role": "superadmin",
  "created_at": "2024-01-15T10:30:00"
}
```

**Error Responses:**

- `404 Not Found` - Admin tidak ditemukan

```json
{
  "detail": "Admin not found"
}
```

---

### 3. Create Admin

Membuat admin baru. Alternative dari endpoint `/api/auth/register` yang bisa dimatikan.

**Endpoint:** `POST /api/admin/`

**Request Body:**

```json
{
  "username": "newadmin",
  "password": "secure_password",
  "role": "writer"
}
```

**Fields:**

- `username` (required) - Username (3-50 karakter)
- `password` (required) - Password (minimum 6 karakter)
- `role` (optional, default: "writer") - Role admin (`superadmin` atau `writer`)

**Request Example:**

```bash
# Create writer admin
curl -X POST "http://localhost:8000/api/admin/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "writer1",
    "password": "password123",
    "role": "writer"
  }'

# Create superadmin
curl -X POST "http://localhost:8000/api/admin/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin2",
    "password": "admin123456",
    "role": "superadmin"
  }'
```

**Response Example (201 Created):**

```json
{
  "id": 3,
  "username": "writer1",
  "role": "writer",
  "created_at": "2024-01-17T09:15:00"
}
```

**Error Responses:**

- `400 Bad Request` - Username sudah digunakan

```json
{
  "detail": "Username already registered"
}
```

---

### 4. Update Admin

Update informasi admin (username, password, atau role).

**Endpoint:** `PUT /api/admin/{admin_id}`

**Path Parameters:**

- `admin_id` (required) - ID admin yang akan diupdate

**Request Body:**

```json
{
  "username": "new_username",
  "password": "new_password",
  "role": "superadmin"
}
```

**Fields (semua optional):**

- `username` (optional) - Username baru (3-50 karakter)
- `password` (optional) - Password baru (minimum 6 karakter)
- `role` (optional) - Role baru (`superadmin` atau `writer`)

**Request Examples:**

```bash
# Update only role
curl -X PUT "http://localhost:8000/api/admin/2" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "role": "superadmin"
  }'

# Update username and password
curl -X PUT "http://localhost:8000/api/admin/3" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "new_username",
    "password": "newpassword123"
  }'

# Update all fields
curl -X PUT "http://localhost:8000/api/admin/4" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "updated_admin",
    "password": "newpass456",
    "role": "writer"
  }'
```

**Response Example (200 OK):**

```json
{
  "id": 2,
  "username": "updated_admin",
  "role": "superadmin",
  "created_at": "2024-01-16T14:20:00"
}
```

**Error Responses:**

- `404 Not Found` - Admin tidak ditemukan
- `400 Bad Request` - Username sudah digunakan

```json
{
  "detail": "Username already taken"
}
```

- `400 Bad Request` - Tidak bisa demote superadmin terakhir

```json
{
  "detail": "Cannot demote the last superadmin. Promote another admin first."
}
```

---

### 5. Update Admin Role (PATCH)

Update hanya role admin saja (endpoint khusus untuk update role).

**Endpoint:** `PATCH /api/admin/{admin_id}/role`

**Path Parameters:**

- `admin_id` (required) - ID admin yang akan diupdate

**Request Body:**

```json
{
  "role": "superadmin"
}
```

**Fields:**

- `role` (required) - Role baru (`superadmin` atau `writer`)

**Request Examples:**

```bash
# Promote writer to superadmin
curl -X PATCH "http://localhost:8000/api/admin/2/role" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "role": "superadmin"
  }'

# Demote superadmin to writer
curl -X PATCH "http://localhost:8000/api/admin/3/role" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "role": "writer"
  }'
```

**Response Example (200 OK):**

```json
{
  "id": 2,
  "username": "writer1",
  "role": "superadmin",
  "created_at": "2024-01-16T14:20:00"
}
```

**Error Responses:**

- `404 Not Found` - Admin tidak ditemukan
- `400 Bad Request` - Tidak bisa demote superadmin terakhir

```json
{
  "detail": "Cannot demote the last superadmin. Promote another admin first."
}
```

---

### 6. Delete Admin

Menghapus admin berdasarkan ID.

**Endpoint:** `DELETE /api/admin/{admin_id}`

**Path Parameters:**

- `admin_id` (required) - ID admin yang akan dihapus

**Request Example:**

```bash
curl -X DELETE "http://localhost:8000/api/admin/3" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response:** `204 No Content` (no response body)

**Error Responses:**

- `404 Not Found` - Admin tidak ditemukan

```json
{
  "detail": "Admin not found"
}
```

- `400 Bad Request` - Tidak bisa menghapus akun sendiri

```json
{
  "detail": "Cannot delete your own admin account"
}
```

- `400 Bad Request` - Tidak bisa menghapus superadmin terakhir

```json
{
  "detail": "Cannot delete the last superadmin"
}
```

---

## Security Features

### 1. Protection Against Self-Demotion

Superadmin tidak bisa menurunkan role dirinya sendiri jika dia adalah satu-satunya superadmin dalam sistem.

### 2. Protection Against Self-Deletion

Admin tidak bisa menghapus akun mereka sendiri.

### 3. Last Superadmin Protection

Sistem mencegah penghapusan atau demotion dari superadmin terakhir untuk menghindari lockout.

### 4. Username Uniqueness

Username harus unik dalam sistem. Tidak bisa membuat atau update admin dengan username yang sudah ada.

---

## Complete Workflow Example

### Scenario: Membuat dan mengelola admin users

```bash
# 1. Login sebagai superadmin
TOKEN=$(curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' \
  | jq -r '.access_token')

# 2. List semua admin
curl -X GET "http://localhost:8000/api/admin/" \
  -H "Authorization: Bearer $TOKEN"

# 3. Create admin writer baru
curl -X POST "http://localhost:8000/api/admin/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "content_writer",
    "password": "writer123",
    "role": "writer"
  }'

# 4. Create admin superadmin baru
curl -X POST "http://localhost:8000/api/admin/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "super_admin2",
    "password": "super123",
    "role": "superadmin"
  }'

# 5. Get detail admin dengan ID 2
curl -X GET "http://localhost:8000/api/admin/2" \
  -H "Authorization: Bearer $TOKEN"

# 6. Promote writer to superadmin
curl -X PATCH "http://localhost:8000/api/admin/2/role" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"role": "superadmin"}'

# 7. Update password admin
curl -X PUT "http://localhost:8000/api/admin/2" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"password": "new_secure_password"}'

# 8. Filter admins berdasarkan role
curl -X GET "http://localhost:8000/api/admin/?role=superadmin" \
  -H "Authorization: Bearer $TOKEN"

# 9. Delete admin (not self)
curl -X DELETE "http://localhost:8000/api/admin/3" \
  -H "Authorization: Bearer $TOKEN"

# 10. Verify deletion
curl -X GET "http://localhost:8000/api/admin/" \
  -H "Authorization: Bearer $TOKEN"
```

---

## Error Codes Summary

| Status Code      | Description                                |
| ---------------- | ------------------------------------------ |
| 200 OK           | Request berhasil                           |
| 201 Created      | Admin berhasil dibuat                      |
| 204 No Content   | Admin berhasil dihapus                     |
| 400 Bad Request  | Validation error atau business logic error |
| 401 Unauthorized | Token tidak valid atau expired             |
| 403 Forbidden    | Tidak memiliki akses (bukan superadmin)    |
| 404 Not Found    | Admin tidak ditemukan                      |

---

## Testing dengan Postman/Insomnia

### Setup Environment Variables:

```
BASE_URL = http://localhost:8000
TOKEN = <your_superadmin_token>
```

### Collection Structure:

```
Admin Management/
├── Login (to get token)
├── List All Admins
├── Get Single Admin
├── Create Admin (Writer)
├── Create Admin (Superadmin)
├── Update Admin
├── Update Admin Role Only
└── Delete Admin
```

---

## Frontend Integration Example

```typescript
// lib/api.ts - Add these functions

export interface AdminListResponse {
  id: number;
  username: string;
  role: AdminRole;
  created_at?: string | null;
}

export interface AdminUpdate {
  username?: string;
  password?: string;
  role?: AdminRole;
}

export interface AdminCreate {
  username: string;
  password: string;
  role?: AdminRole;
}

// Get all admins
export async function getAdmins(params?: {
  page?: number;
  page_size?: number;
  username?: string;
  role?: string;
}): Promise<PaginatedResponse<AdminListResponse>> {
  const token = getAuthToken();
  const searchParams = new URLSearchParams();
  if (params?.page) searchParams.set("page", params.page.toString());
  if (params?.page_size)
    searchParams.set("page_size", params.page_size.toString());
  if (params?.username) searchParams.set("username", params.username);
  if (params?.role) searchParams.set("role", params.role);

  const url = `${API_BASE}/api/admin/?${searchParams}`;
  const response = await fetch(url, {
    headers: { Authorization: `Bearer ${token}` },
  });
  return handleResponse<PaginatedResponse<AdminListResponse>>(response);
}

// Get single admin
export async function getAdmin(id: number): Promise<AdminResponse> {
  const token = getAuthToken();
  const response = await fetch(`${API_BASE}/api/admin/${id}`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  return handleResponse<AdminResponse>(response);
}

// Create admin
export async function createAdmin(admin: AdminCreate): Promise<AdminResponse> {
  const token = getAuthToken();
  const response = await fetch(`${API_BASE}/api/admin/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(admin),
  });
  return handleResponse<AdminResponse>(response);
}

// Update admin
export async function updateAdmin(
  id: number,
  admin: AdminUpdate
): Promise<AdminResponse> {
  const token = getAuthToken();
  const response = await fetch(`${API_BASE}/api/admin/${id}`, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(admin),
  });
  return handleResponse<AdminResponse>(response);
}

// Update admin role
export async function updateAdminRole(
  id: number,
  role: AdminRole
): Promise<AdminResponse> {
  const token = getAuthToken();
  const response = await fetch(`${API_BASE}/api/admin/${id}/role`, {
    method: "PATCH",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({ role }),
  });
  return handleResponse<AdminResponse>(response);
}

// Delete admin
export async function deleteAdmin(id: number): Promise<void> {
  const token = getAuthToken();
  const response = await fetch(`${API_BASE}/api/admin/${id}`, {
    method: "DELETE",
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!response.ok) {
    const error = await response
      .json()
      .catch(() => ({ detail: "An error occurred" }));
    throw new Error(error.detail || `HTTP error! status: ${response.status}`);
  }
}
```

---

## Notes

1. Semua endpoint ini **hanya bisa diakses oleh superadmin**
2. Password akan di-hash menggunakan bcrypt sebelum disimpan
3. Token JWT akan expired setelah 24 jam (sesuai konfigurasi)
4. Gunakan HTTPS di production untuk keamanan
5. Pertimbangkan implementasi rate limiting untuk mencegah brute force
