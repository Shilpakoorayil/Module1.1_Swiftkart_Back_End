# SwiftKart Backend API Documentation

Base URL path for these APIs is assumed to be `/api/` (based on typical Django rest framework setups, verify in your main `urls.py`).

## Authentication Endpoints

### 1. User Login
- **URL**: `/auth/login/user/`
- **Method**: `POST`
- **Permissions**: AllowAny
- **Description**: Authenticate or register a standard User via 10-digit phone number and OTP.
- **Payload**:
  ```json
  {
    "phone_number": "1234567890",
    "otp": "1234"
  }
  ```
- **Response** (200 OK):
  ```json
  {
    "tokens": {
      "refresh": "<refresh_token>",
      "access": "<access_token>"
    },
    "user": {
      "id": 1,
      "username": "1234567890",
      "mobile_number": "1234567890",
      "role": "USER"
    }
  }
  ```

### 2. Admin Login
- **URL**: `/auth/login/admin/`
- **Method**: `POST`
- **Permissions**: AllowAny
- **Description**: Authenticate an Admin user via username and password.
- **Payload**:
  ```json
  {
    "username": "admin_username",
    "password": "admin_password"
  }
  ```
- **Response** (200 OK): Returns JWT tokens and admin user details (similar to User Login).

### 3. Guest Login
- **URL**: `/auth/login/guest/`
- **Method**: `POST`
- **Permissions**: AllowAny
- **Description**: Generate temporary authentication tokens for a guest session.
- **Payload**: None required.
- **Response** (200 OK): Returns JWT tokens and a temporary guest user account.


## Location

### 4. Closest Store
- **URL**: `/location/closest-store/`
- **Method**: `POST`
- **Permissions**: AllowAny
- **Description**: Submit a user's latitude and longitude to find the nearest operational darkstore.
- **Payload**:
  ```json
  {
    "latitude": "12.9716",
    "longitude": "77.5946"
  }
  ```
- **Response** (200 OK):
  ```json
  {
    "id": 1,
    "name": "Koramangala Darkstore",
    "latitude": "12.9352",
    "longitude": "77.6245"
    // ...other store fields
  }
  ```

## Products

### 5. Products List & Retrieve
- **URL**: `/products/` and `/products/<id>/`
- **Methods**: `GET`
- **Permissions**: AllowAny
- **Description**: Fetch a list of all products or retrieve details of a specific product.
- **Response** (200 OK): Array of product objects (or single object for retrieve).

### 6. Product Management
- **URL**: `/products/`, `/products/<id>/`
- **Methods**: `POST`, `PUT`, `PATCH`, `DELETE`
- **Permissions**: IsAuthenticated (must be ADMIN role)
- **Description**: Create, modify, or delete products.


## User Addresses

### 7. Address Management (CRUD)
- **URL**: `/addresses/`, `/addresses/<id>/`
- **Methods**: `GET`, `POST`, `PUT`, `PATCH`, `DELETE`
- **Permissions**: IsAuthenticated (Any logged-in user)
- **Description**: Manage delivery addresses. Users can only see and modify their own addresses.
- **Note**: The `user` field is injected automatically on creation from the authenticated token.


## Checkout & Orders

### 8. Submit Checkout
- **URL**: `/checkout/`
- **Method**: `POST`
- **Permissions**: IsAuthenticated
- **Description**: Convert cart items into a finalized order, deducting product stock in the process.
- **Payload**:
  ```json
  {
    "address_id": 1,
    "store_id": 1,
    "items": [
      {
        "product_id": 10,
        "quantity": 2
      },
      {
        "product_id": 15,
        "quantity": 1
      }
    ]
  }
  ```
- **Response** (201 Created):
  ```json
  {
    "id": 101,
    "user": 1,
    "store": { /* store details */ },
    "address": { /* address details */ },
    "total_amount": "338.00",
    "status": "COMPLETED",
    "created_at": "2026-03-18T10:00:00Z",
    "items": [
        // array of order items
    ]
  }
  ```
- **Error Responses**:
  - `400 Bad Request`: "Missing checkout details." or "Insufficient stock for <Product Name>".
