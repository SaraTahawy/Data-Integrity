### **Flask Project with Two-Factor Authentication (2FA) & JWT Security**  

#### **Overview**  
This is a **Flask project** that implements **Two-Factor Authentication (2FA)** using **Google Authenticator**.  
It also includes **Product Management (CRUD)** with **JWT token security**.

---

### **How to Run the Project**  
#### **1. Install Required Packages**  
Run the following command to install dependencies:  
```bash
pip install flask flask-mysqldb werkzeug pyotp qrcode pillow jwt
```

#### **2. Create Database**  
- Import the **DB.txt** file to create the database.  

#### **3. Run the Server**  
```bash
python task1.py
```
For detailed commands, check the **Commands.txt** file.

---

### **Features**  
✅ **User Registration** → `POST /register`  
✅ **Generate 2FA QR Code** → `GET /generate-2fa/<username>`  
✅ **User Login** → `POST /login`  
✅ **Verify 2FA Code** → `POST /verify-2fa/<username>`  
✅ **Manage Products (CRUD) with JWT**  
  - Add, View, Update, Delete  

---

### **Important Notes**  
⚡ **JWT Token Required** → You must use a JWT token to manage products.  
⏳ **Token Expiry** → The JWT token expires in **10 minutes**.  
📱 **2FA Authentication** → Scan the **QR code** using **Google Authenticator** to get the **2FA code**.  

🚀 **Now you're ready to run the project!**