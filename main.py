import base64
import hashlib
import hmac
import time
from flask import Flask, jsonify, request, abort
from functools import wraps
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.inspection import inspect
from flask_sqlalchemy.query import Query
from sqlalchemy_utils.types import TSVectorType
from sqlalchemy_searchable import SearchQueryMixin, make_searchable


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://vbhxdyww:XoKieKKoQC-TjF9ffr9v7YqvLqMXMq79@tiny.db.elephantsql.com/vbhxdyww"
# Secret key for encoding and decoding the JWT tokens
SECRET_KEY = "mysecretkey"  # Change this to a more secure key in production


db = SQLAlchemy(app)
make_searchable(db.metadata)


# Utility class to handle serialization of database models
class Serializer(object):
    def serialize(self):
        return {c:getattr(self,c) for c in inspect(self).attrs.keys()}
    
    @staticmethod
    def serialize_list(l):
        return [x.serialize() for x in l]


# User model for authentication
class User(db.Model):
    username = db.Column(db.String(100), primary_key=True)
    password = db.Column(db.String(100))

# Custom query class for Book model to enable search functionality
class BookQuery(Query, SearchQueryMixin):
    pass

# Book model with search capabilities
class Book(db.Model, Serializer):
    query_class = BookQuery

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(100))
    author = db.Column(db.String(100))
    
    search_vector = db.Column(TSVectorType("title", "author"))


# Function to encode a JWT token
def encode_jwt(payload):
    # JWT Header (indicating the algorithm used)
    header = {
        "alg": "HS256",
        "typ": "JWT"
    }

    # Base64 URL encoding function (removes trailing '=' for URL-safe encoding)
    def base64_url_encode(data):
        return base64.urlsafe_b64encode(data.encode('utf-8')).decode('utf-8').rstrip("=")

    # Encode header and payload to base64
    encoded_header = base64_url_encode(str(header))
    encoded_payload = base64_url_encode(str(payload))

    # Combine header and payload into a message
    message = f"{encoded_header}.{encoded_payload}"

    # Create the HMAC signature using the secret key
    signature = hmac.new(SECRET_KEY.encode('utf-8'),
                         message.encode('utf-8'), hashlib.sha256).digest()
    encoded_signature = base64.urlsafe_b64encode(
        signature).decode('utf-8').rstrip("=")

    # Return the JWT (header + payload + signature)
    return f"{message}.{encoded_signature}"


# Function to decode and verify a JWT token
def decode_jwt(token):
    try:
        # Split the token into its parts (header, payload, signature)
        header_b64, payload_b64, signature_b64 = token.split(".")
        message = f"{header_b64}.{payload_b64}"

        # Recalculate the signature with the secret key
        expected_signature = hmac.new(SECRET_KEY.encode(
            'utf-8'), message.encode('utf-8'), hashlib.sha256).digest()
        expected_signature_b64 = base64.urlsafe_b64encode(
            expected_signature).decode('utf-8').rstrip("=")

        # Compare the calculated signature with the provided signature
        if expected_signature_b64 != signature_b64:
            return None  # Signature does not match, token is invalid

        # Decode the payload (base64)
        payload = base64.urlsafe_b64decode(payload_b64 + "==").decode('utf-8')
        return payload

    except Exception as e:
        return None  # If any error occurs, return None


# Decorator to require JWT authentication for protected routes
def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(
                " ")[1]  # "Bearer <Token>"

        if not token:
            return jsonify({'message': 'Token is missing!'}), 403

        payload = decode_jwt(token)
        if not payload:
            return jsonify({'message': 'Token is invalid!'}), 403

        return f(eval(payload),*args, **kwargs)

    return decorated_function


# Route to add a book (protected)
@app.route('/add_book', methods=['POST'])
@token_required
def addBook(payload):
    title = request.json.get('title')
    author = request.json.get('author')

    if title is None or author is None:
        return {"message":"All fields are required."}, 404
    
    book = Book(title = title, author = author)

    db.session.add(book)
    db.session.commit()

    return {"message": "Book entered successfully!"}, 201


# Route to get all books (protected)
@app.route('/get_books', methods=['GET'])
@token_required
def getBooks(payload):
    books = Book.query.paginate()

    return {"result": Book.serialize_list(books)}, 200


# Route to search for books (protected)
@app.route('/search_book', methods=['POST'])
@token_required
def searchBook(payload):
    query = request.json.get("query")

    if query is None: return {"message":"query is required."}, 404

    query = " or ".join(query.split())

    books = Book.query.search(query).paginate()

    return {"result": Book.serialize_list(books)}, 200


# Route to update a book (protected)
@app.route('/update_book/<int:id>', methods=['PUT'])
@token_required
def updateBook(payload, id):
    title = request.json.get('title')
    author = request.json.get('author')

    if title is None or author is None:
        return {"message":"All fields are required."}, 404
    
    book = db.get_or_404(Book, id)

    book.title = title
    book.author = author

    db.session.commit()

    return {"book": book.serialize()}, 200


# Route to delete a book (protected)
@app.route('/delete_book/<int:id>', methods=['DELETE'])
@token_required
def deleteBook(payload, id):    
    book = db.get_or_404(Book, id)

    db.session.delete(book)
    db.session.commit()

    return {}, 204


# Route to register a user
@app.route('/register', methods=['POST'])
def register():
    username = request.json.get('username')
    password = request.json.get('password')

    user = User(username = username, password = password)
    db.session.add(user)

    db.session.commit()

    return {"message": "User created successfully!"}, 201


# Route to login and obtain a JWT token
@app.route('/login', methods=['POST'])
def login():
    username = request.json.get('username')
    password = request.json.get('password')

    user = db.session.query(User).filter_by(username = username).first()
    

    # Validate username and password
    if user is not None and user.password == password:
        # Define the payload, which typically includes user data
        payload = {
            # 'sub' is a standard claim for the subject (user)
            'sub': username,
            'exp': time.time() + 3600  # Expiry time: 1 hour from now
        }

        # Create JWT token
        token = encode_jwt(payload)
        return jsonify({'token': token}), 200
    else:
        return jsonify({'message': 'Invalid credentials'}), 401


if __name__ == '__main__':
    with app.app_context():
        db.configure_mappers()
        db.create_all()
    app.run(debug=True)
