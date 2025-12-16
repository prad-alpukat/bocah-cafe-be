# Bocah Cafe API

API untuk menampilkan data cafe hasil scraping dari Google Maps menggunakan FastAPI dan SQLite.

## Fitur

- 📋 **List Data Cafe** - Menampilkan semua data cafe dengan filtering
- 🔐 **Authentication Admin** - Login dan register untuk admin
- ✏️ **CRUD Operations** - Admin dapat Create, Read, Update, Delete data cafe
- 🗄️ **SQLite Database** - Database lokal yang ringan

## Data Cafe

Setiap cafe memiliki informasi:

- Nama cafe
- Gambar thumbnail
- Nomor HP
- Link website
- Rating (0-5)
- Range harga
- Jumlah review Google
- Jam buka
- Alamat lengkap

## Instalasi

1. Copy file environment example:

```bash
cp .env.example .env
```

2. Edit file `.env` dan sesuaikan konfigurasi:

```env
SECRET_KEY=your-super-secret-key-change-this-in-production-min-32-characters
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
ALLOW_ADMIN_REGISTRATION=true  # Set to false to disable admin registration
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Jalankan aplikasi:

```bash
python main.py
```

Server akan berjalan di `http://localhost:8000`

## Dokumentasi API

Setelah menjalankan server, buka:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Endpoint API

### Authentication

#### Register Admin

```
POST /api/auth/register
Body: {
  "username": "admin",
  "password": "password123"
}
```

#### Login Admin

```
POST /api/auth/login
Body: {
  "username": "admin",
  "password": "password123"
}
Response: {
  "access_token": "...",
  "token_type": "bearer"
}
```

#### Get Current Admin Info

```
GET /api/auth/me
Headers: Authorization: Bearer <token>
```

### Cafe (Public Endpoints)

#### Get All Cafes

```
GET /api/cafe/
Query params:
  - page: int (default: 1, min: 1) - Page number
  - page_size: int (default: 10, min: 1, max: 100) - Items per page
  - nama: string (optional - filter by name)
  - min_rating: float (optional - minimum rating filter)

Response:
{
  "data": [
    {
      "id": 1,
      "nama": "Cafe Example",
      "gambar_thumbnail": "https://example.com/image.jpg",
      "no_hp": "081234567890",
      "link_website": "https://example.com",
      "rating": 4.5,
      "range_price": "Rp 15.000 - Rp 50.000",
      "count_google_review": 150,
      "jam_buka": "08:00 - 22:00",
      "alamat_lengkap": "Jl. Example No. 123, Jakarta",
      "created_at": "2025-12-16T10:00:00",
      "updated_at": null
    }
  ],
  "meta": {
    "total": 50,
    "page": 1,
    "page_size": 10,
    "total_pages": 5
  }
}
```

#### Get Single Cafe

```
GET /api/cafe/{cafe_id}
```

### Cafe (Admin Only - Requires Authentication)

#### Create Cafe

```
POST /api/cafe/
Headers: Authorization: Bearer <token>
Body: {
  "nama": "Cafe Example",
  "gambar_thumbnail": "https://example.com/image.jpg",
  "no_hp": "081234567890",
  "link_website": "https://example.com",
  "rating": 4.5,
  "range_price": "Rp 15.000 - Rp 50.000",
  "count_google_review": 150,
  "jam_buka": "08:00 - 22:00",
  "alamat_lengkap": "Jl. Example No. 123, Jakarta"
}
```

#### Update Cafe

```
PUT /api/cafe/{cafe_id}
Headers: Authorization: Bearer <token>
Body: {
  "nama": "Updated Cafe Name",
  "rating": 4.8
}
```

#### Delete Cafe

```
DELETE /api/cafe/{cafe_id}
Headers: Authorization: Bearer <token>
```

## Cara Menggunakan

1. **Register Admin** - Buat akun admin pertama kali
2. **Login** - Dapatkan access token
3. **Tambah Data Cafe** - Gunakan token untuk menambah data cafe
4. **Public Access** - Endpoint list cafe dapat diakses tanpa authentication

## Struktur Database

### Table: cafes

- id (Primary Key)
- nama
- gambar_thumbnail
- no_hp
- link_website
- rating
- range_price
- count_google_review
- jam_buka
- alamat_lengkap
- created_at
- updated_at

### Table: admins

- id (Primary Key)
- username (Unique)
- hashed_password
- created_at

## Teknologi

- FastAPI - Modern web framework
- SQLAlchemy - ORM untuk database
- SQLite - Database
- JWT - Authentication
- Pydantic - Data validation
- Bcrypt - Password hashing

## Security

- Password di-hash menggunakan bcrypt
- JWT token untuk authentication
- Token expires dalam 24 jam
- Admin-only endpoints dilindungi dengan Bearer token
- Admin registration dapat dinonaktifkan via environment variable `ALLOW_ADMIN_REGISTRATION`

## Environment Variables

| Variable                      | Description                       | Default       |
| ----------------------------- | --------------------------------- | ------------- |
| `SECRET_KEY`                  | Secret key untuk JWT token        | -             |
| `ALGORITHM`                   | Algorithm untuk JWT               | HS256         |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Durasi token dalam menit          | 1440 (24 jam) |
| `ALLOW_ADMIN_REGISTRATION`    | Enable/disable admin registration | true          |

**Catatan Keamanan:** Setelah membuat admin pertama, disarankan untuk set `ALLOW_ADMIN_REGISTRATION=false` di file `.env` untuk mencegah registrasi admin yang tidak diinginkan.

## File Database

Database SQLite akan dibuat otomatis dengan nama `bocah_cafe.db` di root directory project saat pertama kali menjalankan aplikasi.
