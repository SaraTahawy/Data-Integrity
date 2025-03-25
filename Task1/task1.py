from flask import Flask, request, jsonify, send_file
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
import pyotp
import qrcode
import io
import jwt  # ✅ استخدام PyJWT الصحيح
import datetime
from functools import wraps

app = Flask(__name__)

# إعداد قاعدة البيانات MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'DI_Task1_2FA'
app.config['SECRET_KEY'] = 'supersecretkey'

mysql = MySQL(app)

# ✅ تسجيل مستخدم جديد
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({'error': 'Missing username or password'}), 400

    username = data['username']
    password = generate_password_hash(data['password'])
    secret = pyotp.random_base32()

    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO users (username, password, twofa_secret) VALUES (%s, %s, %s)", 
                (username, password, secret))
    mysql.connection.commit()
    cur.close()

    return jsonify({'message': 'User registered successfully', '2FA_secret': secret})

# ✅ توليد QR Code لـ Google Authenticator
@app.route('/generate-2fa/<username>', methods=['GET'])
def generate_2fa(username):
    cur = mysql.connection.cursor()
    cur.execute("SELECT twofa_secret FROM users WHERE username=%s", (username,))
    user = cur.fetchone()
    cur.close()

    if not user:
        return jsonify({'message': 'User not found'}), 404

    secret = user[0]
    uri = pyotp.totp.TOTP(secret).provisioning_uri(name=username, issuer_name='Data_Integrity_2FA')

    qr = qrcode.make(uri)
    img = io.BytesIO()
    qr.save(img)
    img.seek(0)

    return send_file(img, mimetype='image/png')

# ✅ تسجيل الدخول
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({'error': 'Missing username or password'}), 400

    username = data['username']
    password = data['password']

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM users WHERE username=%s", (username,))
    user = cur.fetchone()
    cur.close()

    if user and check_password_hash(user[2], password):
        return jsonify({'message': 'Enter 2FA Code', 'username': username})
    return jsonify({'message': 'Invalid credentials'}), 401

# ✅ التحقق من 2FA وإصدار JWT
@app.route('/verify-2fa/<username>', methods=['POST'])
def verify_2fa(username):
    data = request.json
    if not data or 'code' not in data:
        return jsonify({'error': 'Missing 2FA code'}), 400

    user_code = data['code'].replace(" ", "")  # ✅ إزالة أي مسافات زائدة في الكود

    cur = mysql.connection.cursor()
    cur.execute("SELECT twofa_secret FROM users WHERE username=%s", (username,))
    user = cur.fetchone()
    cur.close()

    if not user:
        return jsonify({'message': 'User not found or 2FA not set up'}), 404

    secret = user[0]
    totp = pyotp.TOTP(secret)
    current_code = totp.now()

    print(f"DEBUG: Expected Code: {current_code}, User Entered: {user_code}")

    if totp.verify(user_code):
        token = jwt.encode(
            {'username': username, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=10)},
            app.config['SECRET_KEY'],
            algorithm='HS256'
        )
        return jsonify({'token': token})

    return jsonify({'message': 'Invalid or expired 2FA code'}), 401

# ✅ ديكوريتر لحماية العمليات بـ JWT
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            print("DEBUG: No token received!")  # ✅ طباعة رسالة في حالة عدم إرسال التوكن
            return jsonify({'message': 'Token is missing!'}), 401

        try:
            print(f"DEBUG: Received Token -> {token}")  # ✅ طباعة التوكن لفحصه
            token = token.split(" ")[1]  # ✅ استخراج التوكن بدون `Bearer`
            decoded_token = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            print(f"DEBUG: Decoded Token -> {decoded_token}")  # ✅ طباعة محتوى التوكن بعد فك تشفيره
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token expired!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token!'}), 401

        return f(*args, **kwargs)

    return decorated


# ✅ إضافة منتج جديد
@app.route('/products', methods=['POST'])
@token_required
def create_product():
    data = request.json
    if not data or 'name' not in data or 'price' not in data or 'quantity' not in data:
        return jsonify({'error': 'Missing product details'}), 400

    try:
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO products (name, description, price, quantity) VALUES (%s, %s, %s, %s)",
                    (data['name'], data.get('description', ''), data['price'], data['quantity']))
        mysql.connection.commit()
        cur.close()
    except Exception as e:
        return jsonify({'error': 'Database error', 'details': str(e)}), 500

    return jsonify({'message': 'Product created successfully'})

# ✅ عرض المنتجات
@app.route('/products', methods=['GET'])
@token_required
def get_products():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM products")
    products = cur.fetchall()
    cur.close()

    products_list = [{'id': p[0], 'name': p[1], 'description': p[2], 'price': p[3], 'quantity': p[4]} for p in products]
    return jsonify(products_list)

# ✅ تحديث منتج
@app.route('/products/<int:product_id>', methods=['PUT'])
@token_required
def update_product(product_id):
    data = request.json
    if not data or 'name' not in data or 'price' not in data or 'quantity' not in data:
        return jsonify({'error': 'Missing product details'}), 400

    cur = mysql.connection.cursor()
    cur.execute("UPDATE products SET name=%s, description=%s, price=%s, quantity=%s WHERE id=%s",
                (data['name'], data.get('description', ''), data['price'], data['quantity'], product_id))
    mysql.connection.commit()
    cur.close()

    return jsonify({'message': 'Product updated successfully'})

# ✅ حذف منتج
@app.route('/products/<int:product_id>', methods=['DELETE'])
@token_required
def delete_product(product_id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM products WHERE id=%s", (product_id,))
    mysql.connection.commit()
    cur.close()

    return jsonify({'message': 'Product deleted successfully'})

# ✅ تشغيل التطبيق
if __name__ == '__main__':
    app.run(debug=True)




