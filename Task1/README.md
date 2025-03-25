This is a **Flask project** with **Two-Factor Authentication (2FA)** using **Google Authenticator**.  
It also has **Product Management** (CRUD) with **JWT token security**.

How to Run the Project:
**Install the required packages:**  
```bash
pip install flask flask-mysqldb werkzeug pyotp qrcode pillow jwt
```
Creat database from DB.txt file then
Run the server:
python task1.py
In File Commands.txt you will find how to run the project.

Features
 User Registration (POST /register)
 Generate 2FA QR Code (GET /generate-2fa/<username>)
 User Login (POST /login)
 Verify 2FA Code (POST /verify-2fa/<username>)
 Manage Products (Add, View, Update, Delete) with JWT


Notes
 You must use a JWT token to manage products.
 The token expires in 10 minutes.
 Scan the QR code using Google Authenticator to get the 2FA code. 