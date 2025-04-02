
[![codecov](https://codecov.io/gh/CSCI-GA-2820-SP25-003/customers/graph/badge.svg?token=92SBP8I9EC)](https://codecov.io/gh/CSCI-GA-2820-SP25-003/customers)
![Build Status](https://github.com/CSCI-GA-2820-SP25-003/customers/actions/workflows/workflow.yml/badge.svg)


# Customer REST API Service

A Flask-based REST API that allows you to create, read, update, and delete customer records. This service uses SQLAlchemy as the ORM to interact with the database.

## Overview

The Customer REST API Service provides endpoints to manage customer data with the following features:

- **Create a Customer:** `POST /customers`
- **Retrieve Customers:** `GET /customers`
- **Retrieve a Single Customer:** `GET /customers/<customer_id>`
- **Update a Customer:** `PUT /customers/<customer_id>`
- **Delete a Customer:** `DELETE /customers/<customer_id>`

## API Endpoints

### Root Endpoint

- **URL:** `/`
- **Method:** `GET`
- **Description:** Returns basic information about the API, including the service name, version, and a link to the customer list endpoint.

### Create a Customer

- **URL:** `/customers`
- **Method:** `POST`
- **Headers:** `Content-Type: application/json`
- **Body Example:**

  ```json
  {
    "name": "John Doe",
    "address": "123 Main St, Springfield",
    "email": "johndoe@example.com",
    "phonenumber": "1234567890"
  }
  ```

- **Description:** Creates a new customer record and returns the created customer object along with a `Location` header pointing to the new resource.
- **Response Status:** `201 Created`

### Retrieve Customers

- **URL:** `/customers`
- **Method:** `GET`
- **Query Parameters (optional):**
  - `id` – Filter by customer ID
  - `name` – Filter by customer name
  - `address` – Filter by customer address
  - `email` – Filter by customer email
  - `phonenumber` – Filter by customer phone number

- **Description:** Retrieves all customers or a subset based on the provided query parameters.
- **Response Status:** `200 OK`
- **Response Example:**

  ```json
  [
    {
      "id": 1,
      "name": "John Doe",
      "address": "123 Main St, Springfield",
      "email": "johndoe@example.com",
      "phonenumber": "1234567890"
    },
    {
      "id": 2,
      "name": "Jane Doe",
      "address": "456 Elm St, Springfield",
      "email": "janedoe@example.com",
      "phonenumber": "0987654321"
    }
  ]
  ```

### Retrieve a Single Customer

- **URL:** `/customers/<customer_id>`
- **Method:** `GET`
- **Description:** Retrieves a single customer record by its ID.
- **Response Status:** `200 OK`
- **Response Example:**

  ```json
  {
    "id": 1,
    "name": "John Doe",
    "address": "123 Main St, Springfield",
    "email": "johndoe@example.com",
    "phonenumber": "1234567890"
  }
  ```

### Update a Customer

- **URL:** `/customers/<customer_id>`
- **Method:** `PUT`
- **Headers:** `Content-Type: application/json`
- **Body Example:**

  ```json
  {
    "name": "Jane Doe",
    "address": "456 Elm St, Springfield",
    "email": "janedoe@example.com",
    "phonenumber": "0987654321"
  }
  ```

- **Description:** Updates an existing customer record using the provided data.
- **Response Status:** `200 OK`
- **Response Example:** Returns the updated customer object.

### Delete a Customer

- **URL:** `/customers/<customer_id>`
- **Method:** `DELETE`
- **Description:** Deletes the customer record with the specified ID.
- **Response Status:** `204 No Content`
- **Response Example:** An empty body is returned.
