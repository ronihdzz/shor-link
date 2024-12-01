# Basic API Users

| CI Status | Coverage |
|-----------|----------|
| ![CI](https://github.com/ronihdzz/basic-api-feelings/actions/workflows/ci.yml/badge.svg) | ![Coverage Badge](https://github.com/ronihdzz/basic-api-feelings/raw/artifacts/main/latest/coverage.svg) |

## Overview

This API provides functionality to manage users, including creating accounts, authentication, retrieving user information, and deleting accounts. It uses JWT for secure authentication.


### Endpoints


#### 1. Create User

* Method: `POST`
* Path: `/v1/users/`
* Description: Registers a new user.
* Request Body
    ```
    {
    "username": "string",
    "email": "string",
    "password": "string"
    }
    ```
* Response 
    ```
    {
    "id": "integer",
    "username": "string",
    "email": "string"
    }
    ```
* Erros:
    * `400 Bad Request`: Username or email already registered.


#### 2. Obtain Token

* Method: `POST`
* Path: `/v1/token/`
* Description: Authenticates a user and returns a JWT token.
* Request Body
    ```
    {
    "username": "string",
    "password": "string"
    }
    ```
* Response 
    ```
    {
    "access_token": "string",
    "token_type": "bearer"
    }
    ```
* Erros:
    * `401 Unauthorized`: Incorrect username or password.


#### 3. Get Current User

* Method: `GET`
* Path: `/v1/users/me/`
* Description: Retrieves information of the authenticated user.
* Headers:
    ```
    Authorization: Bearer <access_token>
    ```
* Response 
    ```
    {
    "id": "integer",
    "username": "string",
    "email": "string"
    }
    ```
* Erros:
    * `401 Unauthorized`: Invalid or expired token.
    * `401 Unauthorized`: User not found or deleted.


#### 4. Create User


* Method: `DELETE`
* Path: `/v1/users/me/`
* Description: Deletes the account of the authenticated user.
* Headers:
    ```
    Authorization: Bearer <access_token>
    ```
* Response 
    ```
    {
    "detail": "User deleted"
    }
    ```
* Erros:
    * `401 Unauthorized`: Invalid or expired token.
    * `401 Unauthorized`: User not found or deleted.

## Configuration and Execution

### Local Environment

#### 1) Run the Project

Navigate to the `src` folder and execute the following command:

```
uvicorn main:app --reload
```

#### 2) Run Project Tests


Navigate to the `src` folder and execute the following command:

```
pytest tests
```

#### 3) Run Test Coverage

Navigate to the src folder and execute the following command:

```
coverage run -m pytest tests -s -v --lf && coverage report
```

### Using Docker Compose

#### 1) Run the Project

```
docker-compose up app
```

#### 2) Run the Tests

```
docker-compose run test
```

## Environment Variables Required

* `ENVIRONMENT`: Indicates the environment in which the application is running (e.g., development, production, test).
* `DATABASE_NAME`: Name of the SQLite database (e.g., prod.db, test.db).
* `PRIVATE_KEY`: RSA private key for signing JWT tokens.
* `PUBLIC_KEY`: RSA public key for verifying JWT tokens.
* `JWT_ALGORITHM`: Algorithm used for signing JWT tokens (e.g., RS256).
* `JWT_EXPIRATION_MINUTES`: Token expiration time in minutes.

## Generate keys public and private:

```
openssl genpkey -algorithm RSA -out private_key.pem && openssl rsa -pubout -in private_key.pem -out public_key.pem
```
