# Role-Based Access Control (RBAC) Usage Guide

This document explains how to use the role system in the Bocah Cafe API.

## Available Roles

The system supports two admin roles:

- **superadmin**: Full access to all endpoints and administrative functions
- **writer**: Standard access for content management

## Database Migration

Before using the role system, you need to migrate the existing database:

```bash
cd bocah-cafe-be
python migrate_add_role.py
```

This will:
- Add the `role` column to the `admins` table
- Set the first admin as `superadmin`
- Set all other existing admins as `writer`

## Creating Admins with Roles

### Register a new admin (POST /api/auth/register)

```json
{
  "username": "john_writer",
  "password": "secure_password",
  "role": "writer"
}
```

If `role` is not provided, it defaults to `writer`.

To create a superadmin:

```json
{
  "username": "admin_user",
  "password": "secure_password",
  "role": "superadmin"
}
```

## Using Role-Based Protection in Routes

### Method 1: Using `get_superadmin` dependency

Require superadmin role for an endpoint:

```python
from auth_utils import get_superadmin

@router.delete("/{cafe_id}")
async def delete_cafe(
    cafe_id: int,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_superadmin)  # Only superadmins can access
):
    """Delete cafe - superadmin only"""
    # Your code here
    pass
```

### Method 2: Using `require_role` factory

For custom role requirements:

```python
from auth_utils import require_role

@router.post("/special-action")
async def special_action(
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(require_role("superadmin"))
):
    """Special action - requires specific role"""
    # Your code here
    pass
```

### Method 3: Manual role checking inside the function

For more complex logic:

```python
from auth_utils import get_current_admin, is_superadmin, has_role

@router.put("/{cafe_id}")
async def update_cafe(
    cafe_id: int,
    cafe_update: CafeUpdate,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """Update cafe - with role-based logic"""

    # Check if user is superadmin
    if is_superadmin(current_admin):
        # Superadmins can update all fields
        pass
    elif has_role(current_admin, "writer"):
        # Writers have limited update permissions
        # Example: prevent changing certain fields
        if cafe_update.rating is not None:
            raise HTTPException(
                status_code=403,
                detail="Writers cannot modify ratings"
            )

    # Your update logic here
    pass
```

## Helper Functions

### Available in `auth_utils.py`:

1. **`require_role(required_role: str)`**
   - Dependency factory for requiring a specific role
   - Returns 403 if role doesn't match

2. **`get_superadmin()`**
   - Async dependency that requires superadmin role
   - Returns 403 if user is not superadmin

3. **`has_role(admin: Admin, role: str) -> bool`**
   - Check if admin has a specific role
   - Returns True/False

4. **`is_superadmin(admin: Admin) -> bool`**
   - Check if admin is a superadmin
   - Returns True/False

5. **`is_writer(admin: Admin) -> bool`**
   - Check if admin is a writer
   - Returns True/False

## Example: Protecting Delete Endpoint

Here's how to make the delete endpoint superadmin-only:

```python
# routers/cafe.py
from auth_utils import get_current_admin, get_superadmin

@router.delete("/{cafe_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_cafe(
    cafe_id: int,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_superadmin)  # Changed from get_current_admin
):
    """
    Delete cafe by ID
    Superadmin only - requires superadmin role
    """
    cafe = db.query(Cafe).filter(Cafe.id == cafe_id).first()
    if cafe is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cafe not found"
        )

    db.delete(cafe)
    db.commit()
    return None
```

## Frontend Integration

The frontend types have been updated to include the role field:

```typescript
// lib/api.ts
export type AdminRole = 'superadmin' | 'writer';

export interface AdminResponse {
  id: number;
  username: string;
  role: AdminRole;
  created_at?: string | null;
}
```

You can use the role in your frontend to show/hide features:

```typescript
import { authStore } from '$lib/stores/auth.svelte';

// Check role in your components
if (authStore.user?.role === 'superadmin') {
  // Show superadmin-only features
}
```

## JWT Token

The role is now included in the JWT token payload:

```json
{
  "sub": "username",
  "role": "superadmin",
  "exp": 1234567890
}
```

This allows the backend to quickly check permissions without database queries for every request.

## Testing

### Test with curl:

1. **Register a superadmin:**
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123","role":"superadmin"}'
```

2. **Register a writer:**
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"writer","password":"writer123","role":"writer"}'
```

3. **Login and get token:**
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

4. **Test protected endpoint:**
```bash
curl -X DELETE http://localhost:8000/api/cafe/1 \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

## Security Notes

- Always use HTTPS in production
- Keep `SECRET_KEY` secure and never commit it to version control
- Consider implementing rate limiting for authentication endpoints
- Regularly audit admin accounts and their roles
- Consider adding an audit log for superadmin actions
