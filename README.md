# Library Management System API

This repository contains a Flask-based API for a "Library Management System" that allows CRUD operations for books and users (members). It includes additional features like search functionality, pagination, and token-based authentication.

## Features

1. **CRUD Operations**:

   - Create, Read, Update, and Delete books.
   - Register and authenticate users.

2. **Search Functionality**:

   - Search books by title or author.

3. **Pagination**:

   - Manage large datasets with paginated results.

4. **Token-Based Authentication**:
   - Protect endpoints using JSON Web Tokens (JWT).

---

## How to Run the Project

### Prerequisites

- Python 3.8 or later
- A PostgreSQL database instance

### Steps

1. **Clone the Repository**:

   ```bash
   git clone https://github.com/<your-username>/library-management-system.git
   cd library-management-system
   ```

2. **Set Up a Virtual Environment**:

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**:
   Install required Python libraries.

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure the Database**:
   Update the `SQLALCHEMY_DATABASE_URI` in the code with your PostgreSQL connection string.

5. **Run the Application**:

   ```bash
   python app.py
   ```

6. **Access the API**:
   The application will run on `http://127.0.0.1:5000/` by default.

---

## Design Choices

1. **Flask Framework**:
   - Chosen for its simplicity and scalability, making it ideal for lightweight APIs.
2. **SQLAlchemy ORM**:
   - Enables object-relational mapping, simplifying database operations.
3. **Token-Based Authentication**:
   - JSON Web Tokens (JWT) are used to secure endpoints. This ensures that only authorized users can access protected resources.
4. **Search Functionality**:

   - Implemented using SQLAlchemy's `TSVectorType` for efficient text search in PostgreSQL.

5. **Pagination**:
   - Flask-SQLAlchemy’s `paginate()` method is used to efficiently handle large datasets.

---

## Assumptions and Limitations

### Assumptions

- Users will be authenticated using their username and password.
- JWT expiration is set to 1 hour by default.

### Limitations

- No third-party libraries like `Flask-JWT-Extended` were used as per the constraints.
- Limited error handling in search functionality (e.g., malformed queries).
- Currently, passwords are stored in plain text (not hashed). For production, implement hashing using libraries like `bcrypt`.

---

## API Endpoints

### Public Endpoints

1. **Register User**:
   - `POST /register`
2. **Login User**:
   - `POST /login`

### Protected Endpoints

1. **Add a Book**:
   - `POST /add_book`
2. **Get Books (Paginated)**:
   - `GET /get_books`
3. **Search Books**:
   - `POST /search_book`
4. **Update a Book**:
   - `PUT /update_book/<id>`
5. **Delete a Book**:
   - `DELETE /delete_book/<id>`

---

## Future Improvements

1. Add password hashing and salting.
2. Implement rate-limiting for enhanced security.
3. Improve error handling and validation.
4. Deploy the application using Docker for portability.

---

## License

This project is licensed under the MIT License.

---

Feel free to fork or contribute! 🎉
