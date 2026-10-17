import os
import json
import threading
from flask import Flask, render_template_string, request, redirect, url_for, session, jsonify

app = Flask(__name__)
app.secret_key = 'super_secret_car_showroom_key_2026'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024

# بيانات التسجيل (يفضل تغيير كلمة المرور)
ADMIN_USER = os.environ.get('ADMIN_USER', 'admin')
ADMIN_PASS = os.environ.get('ADMIN_PASS', 'admin')

# ملف حفظ البيانات على السيرفر (بيتعمل تلقائيًا جنب الملف ده)
STATE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data.json')
LOCK = threading.Lock()

FULL_HTML_SYSTEM = r"""
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>النظام المحاسبي البنكي المتكامل لإدارة معارض السيارات</title>
  <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
  <style>
    :root {
      --bg-main: #f8fafc; --bg-card: #ffffff; --border-color: #e2e8f0; --border-highlight: #cbd5e1;
      --text-main: #0f172a; --text-muted: #64748b; --primary: #2563eb; --primary-hover: #1d4ed8;
      --accent-green: #059669; --accent-red: #dc2626; --accent-amber: #d97706; --accent-cyan: #0891b2;
      --accent-purple: #7c3aed; --accent-vodafone: #e60000; --accent-instapay: #5b21b6;
    }
    * { box-sizing: border-box; font-family: 'Cairo', sans-serif; margin: 0; padding: 0; }
    body { background-color: var(--bg-main); color: var(--text-main); padding: 25px; }
    .login-wrapper { max-width: 420px; margin: 80px auto; background: var(--bg-card); border: 1px solid var(--border-color); padding: 35px; border-radius: 16px; box-shadow: 0 10px 25px rgba(0,0,0,0.08); text-align: center; }
    .login-wrapper h2 { font-size: 1.4rem; font-weight: 800; margin-bottom: 8px; }
    .login-wrapper p { font-size: 0.85rem; color: var(--text-muted); margin-bottom: 25px; }
    .bank-header { display: flex; justify-content: space-between; align-items: center; background: var(--bg-card); border: 1px solid var(--border-color); padding: 20px 25px; border-radius: 14px; margin-bottom: 25px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); flex-wrap: wrap; gap: 15px; }
    .bank-title h1 { font-size: 1.5rem; font-weight: 800; display: flex; align-items: center; gap: 12px; }
    .bank-title h1 i { color: var(--primary); }
    .bank-title p { font-size: 0.85rem; color: var(--text-muted); margin-top: 4px; }
    .alert-banner { background: #fef2f2; border: 1px solid #fecaca; color: var(--accent-red); padding: 12px 20px; border-radius: 10px; margin-bottom: 20px; align-items: center; gap: 10px; font-weight: 700; display: none; }
    .fin-dashboard { display: grid; grid-template-columns: repeat(auto-fit, minmax(210px, 1fr)); gap: 15px; margin-bottom: 30px; }
    .fin-box { color: #fff; border: none; border-radius: 14px; padding: 18px; position: relative; overflow: hidden; transition: 0.3s; cursor: pointer; box-shadow: 0 4px 14px rgba(0,0,0,0.18); }
    .fin-box:hover { transform: translateY(-4px); box-shadow: 0 10px 26px rgba(0,0,0,0.28); }
    .fin-box::after { content: ''; position: absolute; left: -22px; bottom: -22px; width: 95px; height: 95px; border-radius: 50%; background: rgba(255,255,255,0.14); }
    .fin-box .label { font-size: 0.85rem; color: rgba(255,255,255,0.95); display: flex; justify-content: space-between; align-items: center; font-weight: 700; }
    .fin-box .label i { font-size: 1.3rem; opacity: 0.95; }
    .fin-box .value { font-size: 1.4rem; font-weight: 800; margin-top: 10px; color: #fff; letter-spacing: 0.5px; }
    .c-capital { background: linear-gradient(135deg, #1e40af, #3b82f6); }
    .c-vault { background: linear-gradient(135deg, #0f766e, #14b8a6); }
    .c-vodafone { background: linear-gradient(135deg, #b91c1c, #ef4444); }
    .c-instapay { background: linear-gradient(135deg, #6d28d9, #8b5cf6); }
    .c-cars { background: linear-gradient(135deg, #0e7490, #06b6d4); }
    .c-sold { background: linear-gradient(135deg, #be185d, #ec4899); }
    .c-profit { background: linear-gradient(135deg, #15803d, #22c55e); }
    .c-exp { background: linear-gradient(135deg, #c2410c, #f97316); }
    .c-p1 { background: linear-gradient(135deg, #3730a3, #6366f1); }
    .c-p2 { background: linear-gradient(135deg, #4d7c0f, #84cc16); }
    .c-sh { background: linear-gradient(135deg, #334155, #64748b); }
    .c-ajel { background: linear-gradient(135deg, #854d0e, #ca8a04); }
    .bank-tabs { display: flex; gap: 10px; margin-bottom: 25px; border-bottom: 2px solid var(--border-color); padding-bottom: 12px; flex-wrap: wrap; }
    .tab-btn { background: var(--bg-card); border: 1px solid var(--border-color); color: var(--text-muted); padding: 9px 18px; border-radius: 8px; font-weight: 700; cursor: pointer; display: inline-flex; align-items: center; gap: 8px; font-size: 0.88rem; transition: 0.2s; }
    .tab-btn.active { background: var(--primary); color: #fff; border-color: var(--primary); box-shadow: 0 4px 12px rgba(37, 99, 235, 0.25); }
    .panel-card { background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 14px; padding: 25px; margin-bottom: 25px; box-shadow: 0 4px 15px rgba(0,0,0,0.03); }
    .panel-title { font-size: 1.1rem; font-weight: 700; margin-bottom: 20px; display: flex; align-items: center; gap: 10px; border-bottom: 1px solid var(--border-color); padding-bottom: 12px; }
    .form-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 15px; margin-bottom: 20px; }
    .field-group label { display: block; font-size: 0.8rem; color: var(--text-muted); margin-bottom: 6px; font-weight: 600; }
    .field-control { width: 100%; padding: 10px 14px; border-radius: 8px; border: 1px solid var(--border-color); background: #f1f5f9; color: var(--text-main); font-size: 0.95rem; }
    .field-control:focus { outline: none; border-color: var(--primary); background: #ffffff; }
    .btn { padding: 8px 16px; border-radius: 8px; border: none; font-weight: 700; cursor: pointer; display: inline-flex; align-items: center; gap: 8px; font-size: 0.85rem; transition: 0.2s; }
    .btn-main { background: var(--primary); color: #fff; }
    .btn-main:hover { background: var(--primary-hover); }
    .btn-success { background: var(--accent-green); color: #fff; }
    .btn-danger { background: var(--accent-red); color: #fff; }
    .btn-warning { background: var(--accent-amber); color: #fff; }
    .btn-sm { padding: 4px 10px; font-size: 0.75rem; }
    .table-wrap { overflow-x: auto; }
    table { width: 100%; border-collapse: collapse; margin-top: 15px; }
    th, td { padding: 12px; text-align: right; border-bottom: 1px solid var(--border-color); font-size: 0.88rem; vertical-align: top; }
    th { color: var(--text-muted); background: #f8fafc; font-weight: 700; white-space: nowrap; }
    .car-img-thumb { width: 55px; height: 55px; object-fit: cover; border-radius: 8px; border: 1px solid var(--border-color); }
    .plate { background: #eff6ff; padding: 3px 8px; border-radius: 4px; color: var(--primary); font-weight: 700; }
    .tot { margin-top: 4px; color: var(--accent-green); font-weight: 700; }
    .badge { display: inline-block; padding: 3px 10px; border-radius: 20px; font-size: 0.78rem; font-weight: 700; }
    .muted { color: var(--text-muted); font-size: 0.78rem; line-height: 1.6; }
    .modal-backdrop { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(15, 23, 42, 0.4); backdrop-filter: blur(4px); display: none; justify-content: center; align-items: center; z-index: 1000; }
    .modal-box { background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 16px; width: 92%; max-width: 750px; padding: 30px; max-height: 90vh; overflow-y: auto; box-shadow: 0 10px 30px rgba(0,0,0,0.15); }
    .workshop-row { background: #f1f5f9; padding: 10px; border-radius: 8px; margin-bottom: 8px; display: flex; gap: 10px; align-items: center; }
    .toast { position: fixed; bottom: 25px; left: 50%; transform: translateX(-50%); background: #0f172a; color: #fff; padding: 10px 22px; border-radius: 10px; font-weight: 700; display: none; z-index: 2000; box-shadow: 0 6px 20px rgba(0,0,0,0.25); }
    .p-sum { display: grid; grid-template-columns: repeat(auto-fit, minmax(230px, 1fr)); gap: 15px; margin-bottom: 25px; }
    .p-sum .c { background: #f8fafc; border: 1px solid var(--border-color); border-radius: 12px; padding: 15px; line-height: 1.9; }
    .alert-banner { position: sticky; top: 10px; z-index: 60; box-shadow: 0 6px 18px rgba(220,38,38,0.25); align-items: flex-start; line-height: 1.9; }
    .plate-row { display: flex; gap: 8px; }
    .plate-l { width: 56px; text-align: center; font-weight: 800; padding: 10px 4px; flex: none; }
  </style>
</head>
<body>

  {% if not logged_in %}
  <div class="login-wrapper">
    <h2><i class="fa-solid fa-lock"></i> تسجيل الدخول للنظام</h2>
    <p>النظام المحاسبي البنكي الخاص بمدير المعرض</p>
    {% if login_error %}
      <div style="color:var(--accent-red); font-weight:700; margin-bottom:15px;">{{ login_error }}</div>
    {% endif %}
    <form method="POST" action="/login">
      <div class="field-group" style="text-align:right; margin-bottom:12px;">
        <label>اسم المستخدم</label>
        <input type="text" name="username" class="field-control" placeholder="اسم المستخدم" required>
      </div>
      <div class="field-group" style="text-align:right; margin-bottom:20px;">
        <label>كلمة المرور</label>
        <input type="password" name="password" class="field-control" placeholder="كلمة المرور" required>
      </div>
      <button type="submit" class="btn btn-main" style="width:100%; justify-content:center;">دخول آمن <i class="fa-solid fa-right-to-bracket"></i></button>
    </form>
  </div>
  {% else %}

  <div class="bank-header">
    <div class="bank-title">
      <h1><i class="fa-solid fa-vault"></i> النظام المحاسبي البنكي لمعارض السيارات</h1>
      <p>إدارة رأس المال، الخزينة النقدية، المحافظ، الشركاء، والآجل</p>
    </div>
    <div style="display:flex; align-items:center; gap:15px;">
      <div id="liveDateDisplay" style="font-weight:700; color:var(--text-muted); font-size:0.9rem; background:#f1f5f9; padding:6px 12px; border-radius:8px;"></div>
      <a href="/logout" class="btn btn-danger btn-sm"><i class="fa-solid fa-power-off"></i> خروج</a>
    </div>
  </div>

  <div class="alert-banner" id="alertBanner">
    <i class="fa-solid fa-triangle-exclamation" style="font-size: 1.2rem;"></i>
    <span id="alertText"></span>
  </div>

  <div class="fin-dashboard">
    <div class="fin-box c-capital" onclick="openDetailModal('capital')">
      <div class="label"><span>رأس المال</span> <i class="fa-solid fa-building-columns"></i></div>
      <div class="value" id="f_capital">0 ج.م</div>
    </div>
    <div class="fin-box c-vault" onclick="openDetailModal('vault')">
      <div class="label"><span>الخزينة (السيولة الكاش)</span> <i class="fa-solid fa-wallet"></i></div>
      <div class="value" id="f_vault">0 ج.م</div>
    </div>
    <div class="fin-box c-vodafone" onclick="openDetailModal('vodafone')">
      <div class="label"><span>رصيد فودافون كاش</span> <i class="fa-solid fa-mobile-screen"></i></div>
      <div class="value" id="f_vodafone">0 ج.م</div>
    </div>
    <div class="fin-box c-instapay" onclick="openDetailModal('instapay')">
      <div class="label"><span>رصيد انستاباي</span> <i class="fa-solid fa-building-columns"></i></div>
      <div class="value" id="f_instapay">0 ج.م</div>
    </div>
    <div class="fin-box c-cars" onclick="openDetailModal('cars')">
      <div class="label"><span>عربيات متاحة</span> <i class="fa-solid fa-car"></i></div>
      <div class="value" id="f_cars">0 (0 ج.م)</div>
    </div>
    <div class="fin-box c-sold" onclick="openDetailModal('sold')">
      <div class="label"><span>عربيات تم بيعها</span> <i class="fa-solid fa-handshake"></i></div>
      <div class="value" id="f_sold">0 (0 ج.م)</div>
    </div>
    <div class="fin-box c-profit" onclick="openDetailModal('profit')">
      <div class="label"><span>أرباح</span> <i class="fa-solid fa-chart-line"></i></div>
      <div class="value" id="f_profit">0 ج.م</div>
    </div>
    <div class="fin-box c-exp" onclick="openDetailModal('showExp')">
      <div class="label"><span>مصروف معرض</span> <i class="fa-solid fa-receipt"></i></div>
      <div class="value" id="f_showExp">0 ج.م</div>
    </div>
    <div class="fin-box c-p1" onclick="openDetailModal('p1')">
      <div class="label"><span>محمد (صافي)</span> <i class="fa-solid fa-user-tie"></i></div>
      <div class="value" id="f_p1">0 ج.م</div>
    </div>
    <div class="fin-box c-p2" onclick="openDetailModal('p2')">
      <div class="label"><span>محمود (صافي)</span> <i class="fa-solid fa-user-tie"></i></div>
      <div class="value" id="f_p2">0 ج.م</div>
    </div>
    <div class="fin-box c-sh" onclick="openDetailModal('sh')">
      <div class="label"><span>ش (صافي)</span> <i class="fa-solid fa-id-card"></i></div>
      <div class="value" id="f_sh">0 ج.م</div>
    </div>
    <div class="fin-box c-ajel" onclick="openDetailModal('ajel')">
      <div class="label"><span>آجل (اللي بره)</span> <i class="fa-solid fa-file-invoice-dollar"></i></div>
      <div class="value" id="f_ajel">0 ج.م</div>
    </div>
  </div>

  <div class="bank-tabs">
    <button class="tab-btn active" onclick="switchTab('tab-inv', this)"><i class="fa-solid fa-car-side"></i> المخزون</button>
    <button class="tab-btn" onclick="switchTab('tab-archive', this)"><i class="fa-solid fa-box-archive"></i> الأرشيف</button>
    <button class="tab-btn" id="btn-tab-ajel" onclick="switchTab('tab-ajel', this)"><i class="fa-solid fa-file-invoice-dollar"></i> الآجل</button>
    <button class="tab-btn" onclick="switchTab('tab-returned', this)"><i class="fa-solid fa-rotate-left"></i> المرتجعات والاستبدال</button>
    <button class="tab-btn" onclick="switchTab('tab-wallets', this)"><i class="fa-solid fa-wallet"></i> المحافظ</button>
    <button class="tab-btn" onclick="switchTab('tab-partners', this)"><i class="fa-solid fa-users"></i> الشركاء</button>
    <button class="tab-btn" onclick="switchTab('tab-capital-sec', this)"><i class="fa-solid fa-building-columns"></i> رأس المال</button>
    <button class="tab-btn" onclick="switchTab('tab-vault-sec', this)"><i class="fa-solid fa-wallet"></i> الخزينة</button>
    <button class="tab-btn" onclick="switchTab('tab-expenses', this)"><i class="fa-solid fa-receipt"></i> المصروفات</button>
    <button class="tab-btn" onclick="switchTab('tab-trash', this)"><i class="fa-solid fa-trash-can"></i> سلة المحذوفات</button>
  </div>

  <!-- المخزون -->
  <div id="tab-inv">
    <div class="panel-card">
      <div class="panel-title"><i class="fa-solid fa-plus-circle"></i> إدراج سيارة جديدة وبنود الورشة (تخصم من الخزينة تلقائيًا)</div>
      <div class="form-grid">
        <div class="field-group"><label>نوع / اسم السيارة</label><input type="text" id="cName" class="field-control" placeholder="هيونداي توسان"></div>
        <div class="field-group"><label>موديل السيارة (سنة)</label><input type="text" id="cModel" class="field-control" placeholder="2020"></div>
        <div class="field-group"><label>رقم اللوحة (حروف ثم أرقام)</label>
          <div class="plate-row">
            <input type="text" id="pl1" class="field-control plate-l" maxlength="1" placeholder="أ">
            <input type="text" id="pl2" class="field-control plate-l" maxlength="1" placeholder="ب">
            <input type="text" id="pl3" class="field-control plate-l" maxlength="1" placeholder="ج">
            <input type="text" id="plNum" class="field-control" maxlength="4" inputmode="numeric" placeholder="1234" style="min-width:80px;">
          </div>
        </div>
        <div class="field-group"><label>رقم الشاسيه</label><input type="text" id="cChassis" class="field-control" placeholder="الشاسيه"></div>
        <div class="field-group"><label>العربية جاية منين (اسم البائع / المصدر)</label><input type="text" id="cFromName" class="field-control" placeholder="اسم البائع أو المعرض"></div>
        <div class="field-group"><label>عنوان البائع / المصدر</label><input type="text" id="cFromAddr" class="field-control" placeholder="العنوان"></div>
        <div class="field-group"><label>سعر الشراء الأساسي</label><input type="number" id="cBuy" class="field-control" value="0"></div>
        <div class="field-group"><label>تاريخ الإدخال</label><input type="date" id="cDate" class="field-control"></div>
        <div class="field-group"><label>صورة السيارة</label><input type="file" id="cImg" class="field-control" accept="image/*"></div>
      </div>
      <div style="background:#f8fafc; border:1px solid var(--border-color); padding:15px; border-radius:10px; margin-bottom:20px;">
        <label style="font-weight:700; color:var(--accent-cyan); margin-bottom:10px; display:block;"><i class="fa-solid fa-wrench"></i> بنود مصاريف الورشة (صيانة، دوكو...)</label>
        <div style="display:flex; gap:10px; margin-bottom:10px;">
          <input type="text" id="tempWkDesc" class="field-control" placeholder="اسم البند">
          <input type="number" id="tempWkPrice" class="field-control" placeholder="المبلغ" style="max-width:150px;">
          <button type="button" class="btn btn-main btn-sm" onclick="addTempWorkshopItem()"><i class="fa-solid fa-plus"></i> إضافة بند</button>
        </div>
        <div id="tempWorkshopList" style="margin-top:10px;"></div>
        <div style="margin-top:10px; font-weight:700; color:var(--accent-green);">إجمالي الورشة: <span id="tempWkTotal">0</span> ج.م</div>
      </div>
      <button class="btn btn-success" onclick="addNewCar()"><i class="fa-solid fa-floppy-disk"></i> حفظ وإدراج السيارة</button>
    </div>

    <div class="panel-card">
      <div class="panel-title"><i class="fa-solid fa-warehouse"></i> السيارات المتاحة بالمعرض</div>
      <div class="table-wrap">
      <table>
        <thead>
          <tr>
            <th>الصورة</th><th>السيارة</th><th>رقم اللوحة</th><th>الشاسيه</th><th>الموديل</th>
            <th>سعر الشراء</th><th>الورشة والتوتال</th><th>التكلفة الكلية</th><th>بيع</th>
          </tr>
        </thead>
        <tbody id="inventoryList"></tbody>
      </table>
      </div>
    </div>
  </div>

  <!-- الأرشيف -->
  <div id="tab-archive" style="display:none;">
    <div class="panel-card">
      <div class="panel-title"><i class="fa-solid fa-magnifying-glass"></i> بحث في أرشيف المبيعات</div>
      <input type="text" id="searchBox" class="field-control" placeholder="ابحث بالسيارة أو اللوحة أو المشتري..." onkeyup="renderArchive()">
    </div>
    <div class="panel-card">
      <div class="panel-title"><i class="fa-solid fa-file-lines"></i> سجل السيارات المباعة</div>
      <div class="table-wrap">
      <table>
        <thead>
          <tr>
            <th>السيارة واللوحة</th><th>المشتري</th><th>الماليات (البيع / المدفوع / المتبقي)</th>
            <th>الحالة</th><th>التوكيل</th><th>البيع النهائي</th><th>الشرط الجزائي</th><th>الربح</th><th>الإجراءات</th>
          </tr>
        </thead>
        <tbody id="archiveList"></tbody>
      </table>
      </div>
    </div>
  </div>

  <!-- الآجل -->
  <div id="tab-ajel" style="display:none;">
    <div class="panel-card">
      <div class="panel-title"><i class="fa-solid fa-magnifying-glass"></i> بحث في الآجل</div>
      <input type="text" id="ajelSearch" class="field-control" placeholder="ابحث باسم المشتري أو السيارة..." onkeyup="renderAjel()">
      <div id="ajelSummary" style="margin-top:12px; font-weight:700;"></div>
    </div>
    <div class="panel-card">
      <div class="panel-title"><i class="fa-solid fa-file-invoice-dollar"></i> متابعة الآجل والسداد</div>
      <div class="table-wrap">
      <table>
        <thead>
          <tr>
            <th>المشتري</th><th>السيارة</th><th>الإجمالي</th><th>المدفوع</th><th>المتبقي</th>
            <th>تاريخ الاستحقاق</th><th>الحالة</th><th>سجل السداد</th><th>سداد</th>
          </tr>
        </thead>
        <tbody id="ajelList"></tbody>
      </table>
      </div>
    </div>
  </div>

  <!-- المرتجعات والاستبدال -->
  <div id="tab-returned" style="display:none;">
    <div class="panel-card">
      <div class="panel-title"><i class="fa-solid fa-magnifying-glass"></i> بحث في المرتجعات والاستبدال</div>
      <input type="text" id="retSearch" class="field-control" placeholder="ابحث بالسيارة أو اللوحة أو المشتري..." onkeyup="renderReturned()">
    </div>
    <div class="panel-card">
      <div class="panel-title"><i class="fa-solid fa-rotate-left"></i> العربيات اللي تم إرجاعها أو استبدالها</div>
      <div class="table-wrap">
      <table>
        <thead>
          <tr><th>النوع</th><th>السيارة المُرجعة</th><th>المشتري</th><th>تاريخ العملية</th><th>المدفوع سابقًا</th><th>الغرامة</th><th>المرتد للمشتري</th><th>تفاصيل الاستبدال / ملاحظة</th></tr>
        </thead>
        <tbody id="returnedList"></tbody>
      </table>
      </div>
    </div>
  </div>

  <!-- المحافظ الإلكترونية -->
  <div id="tab-wallets" style="display:none;">
    <div class="panel-card">
      <div class="panel-title"><i class="fa-solid fa-wallet"></i> المحافظ (فودافون كاش / انستاباي)</div>
      <div class="form-grid">
        <div class="field-group">
          <label>نوع المحفظة</label>
          <select id="walletType" class="field-control">
            <option value="vodafone">فودافون كاش</option>
            <option value="instapay">انستاباي</option>
          </select>
        </div>
        <div class="field-group">
          <label>نوع الحركة</label>
          <select id="walletActionType" class="field-control">
            <option value="deposit">إيداع وارد (من شخص للمحفظة)</option>
            <option value="withdraw_cash">سحب نقدي (للكاش بالخزينة)</option>
            <option value="transfer">تحويل صادر (لجهة أو شخص)</option>
          </select>
        </div>
        <div class="field-group"><label>اسم الشخص / الجهة</label><input type="text" id="walletParty" class="field-control" placeholder="مثل: السيد"></div>
        <div class="field-group"><label>رقم الحساب / الموبايل</label><input type="text" id="walletAccount" class="field-control" placeholder="رقم الموبايل"></div>
        <div class="field-group"><label>المبلغ</label><input type="number" id="walletAmount" class="field-control" placeholder="المبلغ"></div>
        <div class="field-group"><label>السبب / البيان</label><input type="text" id="walletDesc" class="field-control" placeholder="السبب..."></div>
        <div class="field-group"><label>التاريخ</label><input type="date" id="walletDate" class="field-control"></div>
      </div>
      <button class="btn btn-success" onclick="addWalletTransaction()"><i class="fa-solid fa-plus-circle"></i> تنفيذ المعاملة</button>
    </div>
    <div class="panel-card">
      <div class="panel-title"><i class="fa-solid fa-magnifying-glass"></i> بحث في المحافظ</div>
      <input type="text" id="walletSearchBox" class="field-control" placeholder="ابحث بالاسم أو البيان أو الرقم..." onkeyup="renderWalletsTable()">
    </div>
    <div class="panel-card">
      <div class="panel-title"><i class="fa-solid fa-list-check"></i> سجل حركات المحافظ</div>
      <div class="table-wrap">
      <table>
        <thead><tr><th>المحفظة</th><th>الحركة</th><th>الشخص / الجهة</th><th>المبلغ</th><th>البيان</th><th>التاريخ</th></tr></thead>
        <tbody id="walletsListTable"></tbody>
      </table>
      </div>
    </div>
  </div>

  <!-- الشركاء -->
  <div id="tab-partners" style="display:none;">
    <div class="panel-card">
      <div class="panel-title"><i class="fa-solid fa-scale-balanced"></i> ملخص حسابات الشركاء</div>
      <div class="p-sum" id="partnerSummary"></div>
    </div>
    <div class="panel-card">
      <div class="panel-title"><i class="fa-solid fa-users"></i> الشركاء (محمد، محمود، ش)</div>
      <div class="form-grid">
        <div class="field-group">
          <label>الشريك</label>
          <select id="partnerSelect" class="field-control">
            <option value="p1">محمد</option>
            <option value="p2">محمود</option>
            <option value="sh">ش</option>
          </select>
        </div>
        <div class="field-group">
          <label>نوع الحركة</label>
          <select id="partnerActionType" class="field-control">
            <option value="withdraw">سحب</option>
            <option value="deposit">إيداع</option>
          </select>
        </div>
        <div class="field-group"><label>السبب / البيان</label><input type="text" id="partnerDesc" class="field-control" placeholder="السبب..."></div>
        <div class="field-group"><label>المبلغ</label><input type="number" id="partnerAmount" class="field-control" placeholder="المبلغ"></div>
        <div class="field-group"><label>التاريخ</label><input type="date" id="partnerDate" class="field-control"></div>
      </div>
      <button class="btn btn-main" onclick="addPartnerTransaction()"><i class="fa-solid fa-plus"></i> تسجيل الحركة</button>
    </div>
    <div class="panel-card">
      <div class="panel-title"><i class="fa-solid fa-magnifying-glass"></i> بحث في الشركاء</div>
      <input type="text" id="partnerSearchBox" class="field-control" placeholder="ابحث باسم الشريك أو البيان..." onkeyup="renderPartnersTable()">
    </div>
    <div class="panel-card">
      <div class="panel-title"><i class="fa-solid fa-list-check"></i> سجل حركات الشركاء</div>
      <div class="table-wrap">
      <table>
        <thead><tr><th>الشريك</th><th>الحركة</th><th>البيان</th><th>المبلغ</th><th>التاريخ</th></tr></thead>
        <tbody id="partnersListTable"></tbody>
      </table>
      </div>
    </div>
  </div>

  <!-- رأس المال -->
  <div id="tab-capital-sec" style="display:none;">
    <div class="panel-card">
      <div class="panel-title"><i class="fa-solid fa-building-columns"></i> رأس المال الثابت</div>
      <div class="form-grid">
        <div class="field-group">
          <label>نوع العملية</label>
          <select id="capitalAction" class="field-control">
            <option value="set">تعديل المبلغ الكلي إلى</option>
            <option value="add">إضافة لرأس المال</option>
            <option value="sub">سحب من رأس المال</option>
          </select>
        </div>
        <div class="field-group"><label>المبلغ</label><input type="number" id="inputCapital" class="field-control" placeholder="المبلغ"></div>
        <div class="field-group"><label>السبب (إجباري للتوثيق)</label><input type="text" id="capitalDesc" class="field-control" placeholder="سبب التعديل..."></div>
        <div class="field-group"><label>التاريخ</label><input type="date" id="capitalDate" class="field-control"></div>
      </div>
      <button class="btn btn-main" onclick="updateCapital()"><i class="fa-solid fa-check"></i> حفظ</button>
    </div>
    <div class="panel-card">
      <div class="panel-title"><i class="fa-solid fa-clock-rotate-left"></i> سجل تعديلات رأس المال</div>
      <div class="table-wrap">
      <table>
        <thead><tr><th>التاريخ</th><th>وقت التسجيل</th><th>العملية</th><th>من</th><th>إلى</th><th>البيان</th></tr></thead>
        <tbody id="capitalLogTable"></tbody>
      </table>
      </div>
    </div>
  </div>

  <!-- الخزينة -->
  <div id="tab-vault-sec" style="display:none;">
    <div class="panel-card">
      <div class="panel-title"><i class="fa-solid fa-wallet"></i> الخزينة النقدية (السيولة الفعلية)</div>
      <div class="form-grid">
        <div class="field-group">
          <label>نوع الحركة بالخزينة</label>
          <select id="vaultActionType" class="field-control" onchange="toggleVaultReason()">
            <option value="deposit">إيداع نقدي بالخزينة (+)</option>
            <option value="withdraw">سحب نقدي من الخزينة (-)</option>
          </select>
        </div>
        <div class="field-group"><label>المبلغ</label><input type="number" id="vaultAdjustAmt" class="field-control" placeholder="المبلغ"></div>
        <div class="field-group" id="vaultReasonGroup" style="display:none;"><label>السبب</label><input type="text" id="vaultAdjustDesc" class="field-control" placeholder="سبب السحب..."></div>
        <div class="field-group"><label>التاريخ</label><input type="date" id="vaultDate" class="field-control"></div>
      </div>
      <button class="btn btn-success" onclick="adjustVault()"><i class="fa-solid fa-wallet"></i> تنفيذ حركة الخزينة</button>
    </div>
    <div class="panel-card">
      <div class="panel-title"><i class="fa-solid fa-magnifying-glass"></i> بحث في حركات الخزينة</div>
      <input type="text" id="vaultSearch" class="field-control" placeholder="ابحث بالبيان (مثلاً: اسم سيارة)..." onkeyup="renderVaultLogs()">
    </div>
    <div class="panel-card">
      <div class="panel-title"><i class="fa-solid fa-list"></i> سجل حركة الخزينة المباشرة</div>
      <div class="table-wrap">
      <table>
        <thead><tr><th>الحركة</th><th>المبلغ</th><th>البيان</th><th>التاريخ</th></tr></thead>
        <tbody id="vaultLogsTable"></tbody>
      </table>
      </div>
    </div>
  </div>

  <!-- مصروفات المعرض -->
  <div id="tab-expenses" style="display:none;">
    <div class="panel-card">
      <div class="panel-title"><i class="fa-solid fa-receipt"></i> مصروفات المعرض (تخصم من الخزينة)</div>
      <div class="form-grid">
        <div class="field-group"><label>بيان المصروف</label><input type="text" id="expDesc" class="field-control" placeholder="إيجار، كهرباء..."></div>
        <div class="field-group"><label>المبلغ</label><input type="number" id="expAmount" class="field-control" placeholder="المبلغ"></div>
        <div class="field-group"><label>التاريخ</label><input type="date" id="expDate" class="field-control"></div>
      </div>
      <button class="btn btn-danger" onclick="addExpenseRecord()"><i class="fa-solid fa-plus"></i> تسجيل المصروف</button>
      <div class="table-wrap">
      <table style="margin-top:20px;">
        <thead><tr><th>البيان</th><th>المبلغ</th><th>التاريخ</th></tr></thead>
        <tbody id="expensesList"></tbody>
      </table>
      </div>
    </div>
  </div>

  <!-- سلة المحذوفات -->
  <div id="tab-trash" style="display:none;">
    <div class="panel-card">
      <div class="panel-title"><i class="fa-solid fa-trash-can"></i> سلة المحذوفات</div>
      <div class="table-wrap">
      <table>
        <thead><tr><th>نوع العنصر</th><th>التفاصيل والبيان</th><th>المبلغ / التكلفة</th><th>تاريخ الحذف</th></tr></thead>
        <tbody id="trashList"></tbody>
      </table>
      </div>
    </div>
  </div>

  <!-- نافذة البيع -->
  <div class="modal-backdrop" id="sellModal">
    <div class="modal-box">
      <div class="panel-title" style="color:var(--primary);"><i class="fa-solid fa-handshake"></i> إتمام بيع السيارة وتحديد طريقة الدفع</div>
      <div id="sellCarInfo" class="muted" style="margin-bottom:15px; font-size:0.9rem;"></div>
      <input type="hidden" id="modalTargetCarId">
      <div class="form-grid">
        <div class="field-group"><label>اسم المشتري الرباعي</label><input type="text" id="bName" class="field-control"></div>
        <div class="field-group"><label>تليفون المشتري</label><input type="text" id="bPhone" class="field-control"></div>
        <div class="field-group"><label>رقم بطاقة المشتري</label><input type="text" id="bNatId" class="field-control"></div>
        <div class="field-group"><label>عنوان المشتري</label><input type="text" id="bAddr" class="field-control" placeholder="العنوان"></div>
        <div class="field-group"><label>سعر البيع الإجمالي النهائي</label><input type="number" id="bSellPrice" class="field-control" oninput="calcRemainingSell()"></div>
        <div class="field-group">
          <label>طريقة استلام المدفوع</label>
          <select id="bPayMethod" class="field-control">
            <option value="cash">كاش (مباشرة للخزينة)</option>
            <option value="vodafone">فودافون كاش (للمحفظة)</option>
            <option value="instapay">انستاباي (للمحفظة)</option>
          </select>
        </div>
        <div class="field-group"><label>المبلغ المدفوع حاليًا</label><input type="number" id="bPaidPrice" class="field-control" value="0" oninput="calcRemainingSell()"></div>
        <div class="field-group"><label>المبلغ المتبقي (آجل)</label><input type="number" id="bRemPrice" class="field-control" readonly style="background:#e2e8f0; font-weight:bold;"></div>
        <div class="field-group"><label>تاريخ البيع</label><input type="date" id="bSellDate" class="field-control"></div>
        <div class="field-group">
          <label>هل تم عمل التوكيل؟</label>
          <select id="bPoa" class="field-control"><option value="no">لم يتم</option><option value="yes">تم</option></select>
        </div>
        <div class="field-group">
          <label>هل تم البيع بشكل نهائي؟</label>
          <select id="bFinal" class="field-control"><option value="no">لم يتم</option><option value="yes">تم</option></select>
        </div>
        <div class="field-group"><label>الشرط الجزائي (المبلغ)</label><input type="number" id="bPenalty" class="field-control" value="0"></div>
        <div class="field-group" style="grid-column: span 2;">
          <label>تاريخ استحقاق الآجل (التذكير) أو اختر بضغطة زر:</label>
          <div style="display:flex; gap:8px; margin-bottom:8px; flex-wrap:wrap;">
            <button type="button" class="btn btn-sm btn-main" onclick="setDueDateOffset(1)">بعد شهر</button>
            <button type="button" class="btn btn-sm btn-main" onclick="setDueDateOffset(2)">بعد شهرين</button>
            <button type="button" class="btn btn-sm btn-main" onclick="setDueDateOffset(3)">بعد 3 أشهر</button>
            <button type="button" class="btn btn-sm btn-main" onclick="setDueDateOffset(6)">بعد 6 أشهر</button>
          </div>
          <input type="date" id="bDueDate" class="field-control">
        </div>
      </div>
      <div style="display:flex; justify-content:flex-end; gap:12px; margin-top:20px;">
        <button class="btn" style="background:var(--border-highlight);" onclick="closeModal('sellModal')">إلغاء</button>
        <button class="btn btn-success" onclick="confirmSellAction()"><i class="fa-solid fa-check-circle"></i> تأكيد البيع</button>
      </div>
    </div>
  </div>

  <!-- نافذة سداد دفعة -->
  <div class="modal-backdrop" id="payModal">
    <div class="modal-box" style="max-width:480px;">
      <div class="panel-title" style="color:var(--accent-green);"><i class="fa-solid fa-money-bill-wave"></i> سداد دفعة من الآجل</div>
      <input type="hidden" id="payTargetId">
      <div id="payInfo" class="muted" style="margin-bottom:15px; font-size:0.9rem;"></div>
      <div class="form-grid">
        <div class="field-group"><label>مبلغ الدفعة</label><input type="number" id="pAmount" class="field-control"></div>
        <div class="field-group">
          <label>طريقة الاستلام</label>
          <select id="pMethod" class="field-control">
            <option value="cash">كاش (للخزينة)</option>
            <option value="vodafone">فودافون كاش</option>
            <option value="instapay">انستاباي</option>
          </select>
        </div>
        <div class="field-group"><label>تاريخ السداد</label><input type="date" id="pDate" class="field-control"></div>
      </div>
      <div style="display:flex; justify-content:flex-end; gap:12px; margin-top:10px;">
        <button class="btn" style="background:var(--border-highlight);" onclick="closeModal('payModal')">إلغاء</button>
        <button class="btn btn-success" onclick="confirmPay()"><i class="fa-solid fa-check"></i> تسجيل السداد</button>
      </div>
    </div>
  </div>

  <!-- نافذة الإرجاع / الاستبدال -->
  <div class="modal-backdrop" id="returnModal">
    <div class="modal-box" style="max-width:620px;">
      <div class="panel-title" style="color:var(--accent-amber);"><i class="fa-solid fa-rotate-left"></i> إرجاع أو استبدال السيارة</div>
      <input type="hidden" id="retTargetId">
      <div id="retInfo" class="muted" style="margin-bottom:15px; font-size:0.9rem;"></div>
      <div class="form-grid">
        <div class="field-group">
          <label>نوع العملية</label>
          <select id="rType" class="field-control" onchange="toggleRetType()">
            <option value="return">إرجاع للعربيات المتاحة</option>
            <option value="exchange">استبدال بسيارة أخرى</option>
          </select>
        </div>
        <div class="field-group"><label>تاريخ العملية</label><input type="date" id="rDate" class="field-control"></div>
        <div class="field-group"><label>غرامة مدفوعة من المشتري (تضاف للخزينة/المحفظة وللأرباح)</label><input type="number" id="rPenalty" class="field-control" value="0"></div>
        <div class="field-group">
          <label>طريقة استلام الغرامة / الدفعة</label>
          <select id="rPenMethod" class="field-control">
            <option value="cash">كاش (للخزينة)</option>
            <option value="vodafone">فودافون كاش</option>
            <option value="instapay">انستاباي</option>
          </select>
        </div>
      </div>
      <div id="rReturnBox" class="form-grid">
        <div class="field-group"><label>مبلغ مرتد للمشتري من اللي دفعه (يخصم من الخزينة)</label><input type="number" id="rRefund" class="field-control" value="0"></div>
      </div>
      <div id="rExchangeBox" class="form-grid" style="display:none;">
        <div class="field-group"><label>السيارة البديلة (من المتاحة)</label><select id="rNewCar" class="field-control"></select></div>
        <div class="field-group"><label>سعر بيع السيارة الجديدة</label><input type="number" id="rNewPrice" class="field-control" oninput="calcExchangeDiff()"></div>
        <div id="rDiffInfo" style="grid-column: span 2; font-weight:700; color:var(--accent-purple);"></div>
        <div class="field-group"><label>مبلغ يدفعه المشتري الآن (من الفرق)</label><input type="number" id="rPayNow" class="field-control" value="0"></div>
        <div class="field-group"><label>تاريخ استحقاق المتبقي</label><input type="date" id="rDue" class="field-control"></div>
      </div>
      <div class="field-group" style="margin-top:5px;"><label>ملاحظة / سبب</label><input type="text" id="rNote" class="field-control" placeholder="سبب الإرجاع أو الاستبدال..."></div>
      <div style="display:flex; justify-content:flex-end; gap:12px; margin-top:15px;">
        <button class="btn" style="background:var(--border-highlight);" onclick="closeModal('returnModal')">إلغاء</button>
        <button class="btn btn-warning" onclick="confirmReturn()"><i class="fa-solid fa-check"></i> تأكيد</button>
      </div>
    </div>
  </div>

  <!-- نافذة التفاصيل -->
  <div class="modal-backdrop" id="detailModal">
    <div class="modal-box" style="max-width:800px;">
      <div class="panel-title" id="detailModalTitle" style="color:var(--primary);"></div>
      <div id="detailModalBody" style="margin-bottom:20px; max-height:60vh; overflow-y:auto;"></div>
      <div style="display:flex; justify-content:flex-end;">
        <button class="btn btn-main" onclick="closeModal('detailModal')">إغلاق</button>
      </div>
    </div>
  </div>

  <div class="toast" id="toast"></div>

  <script>
    // ================= الحالة العامة (بتتحفظ على السيرفر تلقائيًا) =================
    let S = { capital: 0, capitalLog: [], inventory: [], archive: [], wallets: [], partners: [], vault: [], expenses: [], trash: [] };
    let tempWk = [];

    const $ = id => document.getElementById(id);
    const esc = s => String(s == null ? '' : s).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
    const fmt = n => (Number(n) || 0).toLocaleString('en-US');
    const money = n => fmt(n) + ' ج.م';
    const pad = n => String(n).padStart(2, '0');
    const ymd = d => d.getFullYear() + '-' + pad(d.getMonth() + 1) + '-' + pad(d.getDate());
    const today = () => ymd(new Date());
    const nowStr = () => { const d = new Date(); return ymd(d) + ' ' + pad(d.getHours()) + ':' + pad(d.getMinutes()); };
    const uid = () => Date.now() * 1000 + Math.floor(Math.random() * 1000);
    const num = id => parseFloat($(id).value) || 0;
    const WALLET_NAME = { vodafone: 'فودافون كاش', instapay: 'انستاباي', cash: 'كاش (الخزينة)', transfer: 'محوّل من الدفعات السابقة' };
    const PARTNER_NAME = { p1: 'محمد', p2: 'محمود', sh: 'ش' };

    // ===== التاريخ والوقت التلقائي =====
    const DATE_IDS = ['cDate', 'walletDate', 'partnerDate', 'capitalDate', 'vaultDate', 'expDate', 'bSellDate', 'pDate', 'rDate'];
    function refreshDateInputs(force) {
      DATE_IDS.forEach(id => { const el = $(id); if (el && (force || el.dataset.manual !== '1')) el.value = today(); });
    }
    function resetDateFlags() { DATE_IDS.forEach(id => { const el = $(id); if (el) delete el.dataset.manual; }); refreshDateInputs(true); }
    function getDate(id) { const el = $(id); return (el && el.dataset.manual === '1' && el.value) ? el.value : today(); }
    function tickClock() {
      $('liveDateDisplay').innerText = new Date().toLocaleString('ar-EG-u-nu-latn', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit', second: '2-digit' });
    }
    const diffText = d => d > 0 ? 'المشتري يدفع فرق ' + fmt(d) + ' ج.م' : (d < 0 ? 'المعرض يرد فرق ' + fmt(-d) + ' ج.م' : 'بدون فرق');

    function toast(msg) {
      const t = $('toast');
      t.innerText = msg; t.style.display = 'block';
      clearTimeout(window._tt);
      window._tt = setTimeout(() => { t.style.display = 'none'; }, 2500);
    }

    // ================= الحفظ على السيرفر =================
    let saveQ = Promise.resolve();
    function save() {
      saveQ = saveQ.then(() => fetch('/api/state', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(S) })
        .then(r => { if (r.status === 401) location.href = '/'; else if (!r.ok) toast('تعذر الحفظ على السيرفر'); }))
        .catch(() => toast('تعذر الحفظ على السيرفر'));
    }
    function commit() { renderAll(); save(); resetDateFlags(); }

    function openModal(id) { $(id).style.display = 'flex'; }
    function closeModal(id) { $(id).style.display = 'none'; }

    function switchTab(tabId, btn) {
      document.querySelectorAll('[id^="tab-"]').forEach(el => el.style.display = 'none');
      $(tabId).style.display = 'block';
      document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
      if (btn) btn.classList.add('active');
    }

    // ================= دوال مساعدة للماليات =================
    function vaultAdd(type, amount, desc, date, src) {
      S.vault.push({ id: uid(), type, amount, desc, date: date || today(), at: nowStr(), src: src || 'manual' });
    }
    const vaultBal = () => S.vault.reduce((s, v) => v.type === 'deposit' ? s + v.amount : s - v.amount, 0);
    const walletBal = t => S.wallets.filter(w => w.walletType === t).reduce((s, w) => w.actionType === 'deposit' ? s + w.amount : s - w.amount, 0);
    const partnerStat = p => {
      const dep = S.partners.filter(x => x.partner === p && x.type === 'deposit').reduce((s, x) => s + x.amount, 0);
      const wd = S.partners.filter(x => x.partner === p && x.type === 'withdraw').reduce((s, x) => s + x.amount, 0);
      return { dep, wd, net: wd - dep };
    };
    function receiveMoney(method, amount, party, phone, desc, date) {
      if (amount <= 0) return;
      if (method === 'cash') vaultAdd('deposit', amount, desc, date, 'sale');
      else S.wallets.push({ id: uid(), at: nowStr(), walletType: method, actionType: 'deposit', party, account: phone || '', amount, desc, date });
    }

    // ================= الداشبورد =================
    function refreshFinancials() {
      const carsCost = S.inventory.reduce((s, c) => s + c.totalCost, 0);
      const sold = S.archive.filter(r => r.status === 'sold');
      const profit = sold.reduce((s, r) => s + r.profit, 0) + S.archive.filter(r => r.status === 'returned').reduce((s, r) => s + (r.penaltyCollected || 0), 0);
      const ajel = sold.reduce((s, r) => s + r.rem, 0);
      const exp = S.expenses.reduce((s, e) => s + e.amount, 0);
      $('f_capital').innerText = money(S.capital);
      $('f_vault').innerText = money(vaultBal());
      $('f_vodafone').innerText = money(walletBal('vodafone'));
      $('f_instapay').innerText = money(walletBal('instapay'));
      $('f_cars').innerText = S.inventory.length + ' (' + money(carsCost) + ')';
      $('f_profit').innerText = money(profit);
      $('f_showExp').innerText = money(exp);
      $('f_p1').innerText = money(partnerStat('p1').net);
      $('f_p2').innerText = money(partnerStat('p2').net);
      $('f_sh').innerText = money(partnerStat('sh').net);
      $('f_ajel').innerText = money(ajel);
      $('f_sold').innerText = sold.length + ' (' + money(sold.reduce((x, r) => x + r.sellPrice, 0)) + ')';
      const od = sold.filter(r => r.rem > 0 && r.dueDate && r.dueDate <= today());
      const b = $('alertBanner');
      if (od.length > 0) {
        const items = od.map(r => {
          const days = Math.round((new Date(today() + 'T00:00:00') - new Date(r.dueDate + 'T00:00:00')) / 86400000);
          const when = days > 0 ? 'متأخر ' + days + ' يوم' : 'مستحق اليوم';
          return `<div>• <b>${esc(r.bName)}</b> (${esc(r.carName)}) — المطلوب تحصيله: <b>${money(r.rem)}</b> — الاستحقاق: ${esc(r.dueDate)} — <b>${when}</b></div>`;
        }).join('');
        b.style.display = 'flex';
        $('alertText').innerHTML = `<div style="font-size:1.05rem">تنبيه: فلوس آجلة جه ميعادها وفاضل تتحصل (${od.length}):</div>${items}<button class="btn btn-danger btn-sm" style="margin-top:8px" onclick="switchTab('tab-ajel', $('btn-tab-ajel'))">فتح الآجل</button>`;
      } else b.style.display = 'none';
    }

    // ================= رأس المال =================
    function updateCapital() {
      const type = $('capitalAction').value, raw = $('inputCapital').value;
      const amt = parseFloat(raw), desc = $('capitalDesc').value.trim(), date = getDate('capitalDate');
      if (raw === '' || isNaN(amt) || amt < 0) return toast('اكتب المبلغ');
      if (!desc) return toast('اكتب سبب التعديل');
      const old = S.capital;
      let nw;
      if (type === 'set') nw = amt;
      else if (type === 'add') nw = old + amt;
      else { if (amt > old) return toast('المبلغ أكبر من رأس المال الحالي'); nw = old - amt; }
      S.capital = nw;
      S.capitalLog.push({ id: uid(), at: nowStr(), date, action: type, amount: amt, oldVal: old, newVal: nw, desc });
      $('inputCapital').value = ''; $('capitalDesc').value = '';
      commit();
    }
    function capitalLogRows() {
      const lbl = { set: 'تعديل المبلغ', add: 'إضافة', sub: 'سحب', opening: 'رصيد افتتاحي' };
      return S.capitalLog.slice().reverse().map(l => {
        const op = (lbl[l.action] || l.action) + ((l.action === 'add' || l.action === 'sub') ? ' ' + fmt(l.amount) : '');
        return `<tr><td>${esc(l.date)}</td><td><small>${esc(l.at)}</small></td><td><b>${op}</b></td><td>${fmt(l.oldVal)}</td><td><b>${fmt(l.newVal)}</b></td><td>${esc(l.desc)}</td></tr>`;
      }).join('');
    }
    function renderCapitalLog() { $('capitalLogTable').innerHTML = capitalLogRows() || '<tr><td colspan="6" class="muted">لا توجد تعديلات</td></tr>'; }

    // ================= الخزينة =================
    function toggleVaultReason() { $('vaultReasonGroup').style.display = $('vaultActionType').value === 'withdraw' ? 'block' : 'none'; }
    function adjustVault() {
      const type = $('vaultActionType').value, amt = num('vaultAdjustAmt'), desc = $('vaultAdjustDesc').value.trim(), date = getDate('vaultDate');
      if (amt <= 0) return toast('اكتب المبلغ');
      if (type === 'withdraw' && !desc) return toast('اكتب سبب السحب');
      vaultAdd(type, amt, type === 'deposit' ? 'إيداع نقدي' : desc, date, 'manual');
      $('vaultAdjustAmt').value = ''; $('vaultAdjustDesc').value = '';
      commit();
    }
    function renderVaultLogs() {
      const q = $('vaultSearch').value.trim().toLowerCase();
      const rows = S.vault.slice().reverse().filter(v => !q || (v.desc + ' ' + v.date + ' ' + (v.type === 'deposit' ? 'إيداع' : 'سحب')).toLowerCase().includes(q));
      $('vaultLogsTable').innerHTML = rows.map(v => {
        const badge = v.type === 'deposit' ? '<span style="color:var(--accent-green);font-weight:bold;">إيداع</span>' : '<span style="color:var(--accent-red);font-weight:bold;">سحب</span>';
        return `<tr><td>${badge}</td><td><b>${money(v.amount)}</b></td><td>${esc(v.desc)}</td><td>${esc(v.date)}<br><small class="muted">${esc(v.at)}</small></td></tr>`;
      }).join('') || '<tr><td colspan="4" class="muted">لا توجد حركات</td></tr>';
    }

    // ================= المصروفات =================
    function addExpenseRecord() {
      const desc = $('expDesc').value.trim(), amount = num('expAmount'), date = getDate('expDate');
      if (!desc || amount <= 0) return toast('اكتب البيان والمبلغ');
      S.expenses.push({ id: uid(), at: nowStr(), desc, amount, date });
      vaultAdd('withdraw', amount, 'مصروف معرض: ' + desc, date, 'expense');
      $('expDesc').value = ''; $('expAmount').value = '';
      commit();
    }
    function renderExpenses() {
      $('expensesList').innerHTML = S.expenses.slice().reverse().map(e =>
        `<tr><td>${esc(e.desc)}</td><td><b style="color:var(--accent-red)">${money(e.amount)}</b></td><td>${esc(e.date)}<br><small class="muted">${esc(e.at)}</small></td></tr>`).join('') || '<tr><td colspan="3" class="muted">لا توجد مصروفات</td></tr>';
    }

    // ================= المحافظ =================
    function addWalletTransaction() {
      const walletType = $('walletType').value, actionType = $('walletActionType').value;
      const party = $('walletParty').value.trim(), account = $('walletAccount').value.trim();
      const amount = num('walletAmount'), desc = $('walletDesc').value.trim(), date = getDate('walletDate');
      if (!party || amount <= 0) return toast('اكتب اسم الشخص/الجهة والمبلغ');
      if (actionType !== 'deposit' && amount > walletBal(walletType)) return toast('رصيد المحفظة غير كافٍ');
      S.wallets.push({ id: uid(), at: nowStr(), walletType, actionType, party, account, amount, desc, date });
      if (actionType === 'withdraw_cash') vaultAdd('deposit', amount, 'سحب نقدي من ' + WALLET_NAME[walletType] + ' - ' + party + (desc ? ': ' + desc : ''), date, 'wallet');
      ['walletParty', 'walletAccount', 'walletAmount', 'walletDesc'].forEach(i => $(i).value = '');
      commit();
    }
    function renderWalletsTable() {
      const q = $('walletSearchBox').value.trim().toLowerCase();
      const rows = S.wallets.slice().reverse().filter(w => !q || [w.party, w.desc, w.account, WALLET_NAME[w.walletType]].join(' ').toLowerCase().includes(q));
      $('walletsListTable').innerHTML = rows.map(w => {
        let badge;
        if (w.actionType === 'deposit') badge = '<span style="color:var(--accent-green);font-weight:bold;">إيداع وارد</span>';
        else if (w.actionType === 'withdraw_cash') badge = '<span style="color:var(--primary);font-weight:bold;">سحب كاش</span>';
        else badge = '<span style="color:var(--accent-amber);font-weight:bold;">تحويل صادر</span>';
        return `<tr><td><b>${WALLET_NAME[w.walletType]}</b></td><td>${badge}</td><td><b>${esc(w.party)}</b><br><small class="muted">${esc(w.account)}</small></td><td><b style="color:var(--accent-purple)">${money(w.amount)}</b></td><td>${esc(w.desc)}</td><td>${esc(w.date)}<br><small class="muted">${esc(w.at)}</small></td></tr>`;
      }).join('') || '<tr><td colspan="6" class="muted">لا توجد حركات</td></tr>';
    }

    // ================= الشركاء =================
    function addPartnerTransaction() {
      const partner = $('partnerSelect').value, type = $('partnerActionType').value;
      const desc = $('partnerDesc').value.trim(), amount = num('partnerAmount'), date = getDate('partnerDate');
      if (amount <= 0) return toast('اكتب المبلغ');
      if (type === 'withdraw' && !desc) return toast('اكتب سبب السحب');
      S.partners.push({ id: uid(), at: nowStr(), partner, type, desc: desc || 'إيداع', amount, date });
      vaultAdd(type, amount, (type === 'withdraw' ? 'سحب' : 'إيداع') + ' الشريك ' + PARTNER_NAME[partner] + (desc ? ': ' + desc : ''), date, 'partner');
      $('partnerDesc').value = ''; $('partnerAmount').value = '';
      commit();
    }
    function renderPartnerSummary() {
      $('partnerSummary').innerHTML = ['p1', 'p2', 'sh'].map(p => {
        const s = partnerStat(p);
        return `<div class="c"><b style="font-size:1.05rem">${PARTNER_NAME[p]}</b><br>إجمالي الإيداع: <b style="color:var(--accent-green)">${money(s.dep)}</b><br>إجمالي السحب: <b style="color:var(--accent-red)">${money(s.wd)}</b><br>الصافي (المسحوب − المودع): <b>${money(s.net)}</b></div>`;
      }).join('');
    }
    function renderPartnersTable() {
      const q = $('partnerSearchBox').value.trim().toLowerCase();
      const rows = S.partners.slice().reverse().filter(p => !q || (PARTNER_NAME[p.partner] + ' ' + p.desc + ' ' + p.date).toLowerCase().includes(q));
      $('partnersListTable').innerHTML = rows.map(p => {
        const badge = p.type === 'withdraw' ? '<span style="color:var(--accent-red);font-weight:bold;">سحب</span>' : '<span style="color:var(--accent-green);font-weight:bold;">إيداع</span>';
        return `<tr><td><b>${PARTNER_NAME[p.partner]}</b></td><td>${badge}</td><td>${esc(p.desc)}</td><td><b style="color:var(--accent-amber)">${money(p.amount)}</b></td><td>${esc(p.date)}<br><small class="muted">${esc(p.at)}</small></td></tr>`;
      }).join('') || '<tr><td colspan="5" class="muted">لا توجد حركات</td></tr>';
    }

    // ================= المخزون =================
    function addTempWorkshopItem() {
      const desc = $('tempWkDesc').value.trim(), price = num('tempWkPrice');
      if (!desc || price <= 0) return toast('اكتب اسم البند والمبلغ');
      tempWk.push({ desc, price });
      $('tempWkDesc').value = ''; $('tempWkPrice').value = '';
      renderTempWorkshopList();
    }
    function removeTempItem(i) { tempWk.splice(i, 1); renderTempWorkshopList(); }
    function renderTempWorkshopList() {
      let total = 0;
      $('tempWorkshopList').innerHTML = tempWk.map((it, i) => {
        total += it.price;
        return `<div class="workshop-row"><span><b>${esc(it.desc)}</b>: ${money(it.price)}</span><button type="button" class="btn btn-warning btn-sm" style="margin-right:auto;" onclick="removeTempItem(${i})">إلغاء البند</button></div>`;
      }).join('');
      $('tempWkTotal').innerText = fmt(total);
    }
    function readImg(file) {
      return new Promise(res => {
        if (!file) return res('');
        const fr = new FileReader();
        fr.onload = e => {
          const im = new Image();
          im.onload = () => {
            const k = Math.min(1, 500 / Math.max(im.width, im.height));
            const c = document.createElement('canvas');
            c.width = im.width * k; c.height = im.height * k;
            c.getContext('2d').drawImage(im, 0, 0, c.width, c.height);
            res(c.toDataURL('image/jpeg', 0.7));
          };
          im.onerror = () => res('');
          im.src = e.target.result;
        };
        fr.onerror = () => res('');
        fr.readAsDataURL(file);
      });
    }
    async function addNewCar() {
      const name = $('cName').value.trim();
      const letters = ['pl1', 'pl2', 'pl3'].map(i => $(i).value.trim()).filter(Boolean);
      const digits = $('plNum').value.trim();
      if (!name || (!digits && !letters.length)) return toast('اكتب اسم السيارة ورقم اللوحة');
      const plate = (letters.join(' ') + ' ' + digits).trim();
      const buyPrice = num('cBuy'), cDate = getDate('cDate');
      const wkItems = tempWk.slice(), wkTotal = wkItems.reduce((s, i) => s + i.price, 0);
      const img = await readImg($('cImg').files[0]);
      const car = {
        id: uid(), at: nowStr(), name, plate, plateLetters: letters.join(' '), plateNum: digits,
        chassis: $('cChassis').value.trim(), model: $('cModel').value.trim(),
        fromName: $('cFromName').value.trim(), fromAddr: $('cFromAddr').value.trim(),
        buyPrice, cDate, wkItems, wkTotal, totalCost: buyPrice + wkTotal, img, notes: []
      };
      S.inventory.push(car);
      if (buyPrice > 0) vaultAdd('withdraw', buyPrice, 'شراء سيارة ' + name + ' - لوحة ' + plate + (car.fromName ? ' من ' + car.fromName : ''), cDate, 'car');
      if (wkTotal > 0) vaultAdd('withdraw', wkTotal, 'مصاريف ورشة سيارة ' + name + ' - لوحة ' + plate + ' (' + wkItems.map(i => i.desc).join('، ') + ')', cDate, 'car');
      ['cName', 'cModel', 'pl1', 'pl2', 'pl3', 'plNum', 'cChassis', 'cFromName', 'cFromAddr', 'cImg'].forEach(i => $(i).value = '');
      $('cBuy').value = '0';
      tempWk = []; renderTempWorkshopList();
      commit();
    }
    function renderInventory() {
      $('inventoryList').innerHTML = S.inventory.map(c => {
        const thumb = c.img ? `<img src="${c.img}" class="car-img-thumb">` : '<small class="muted">بدون صورة</small>';
        const wk = c.wkItems.length ? c.wkItems.map(i => `• ${esc(i.desc)}: <b>${fmt(i.price)}</b>`).join('<br>') : 'بدون مصاريف ورشة';
        const from = (c.fromName || c.fromAddr) ? `<div class="muted">جاية من: <b>${esc(c.fromName) || '-'}</b>${c.fromAddr ? ' — ' + esc(c.fromAddr) : ''}</div>` : '';
        const notes = (c.notes || []).map(n => `<div class="muted" style="color:var(--accent-amber);font-weight:700">⚠ ${esc(n)}</div>`).join('');
        return `<tr>
          <td>${thumb}</td>
          <td><b>${esc(c.name)}</b><br><small class="muted">إدخال: ${esc(c.cDate)}</small>${from}${notes}</td>
          <td><span class="plate">${esc(c.plate)}</span></td>
          <td><small>${esc(c.chassis) || 'غير مدون'}</small></td>
          <td>${esc(c.model) || '-'}</td>
          <td>${money(c.buyPrice)}</td>
          <td><div style="font-size:0.85rem;line-height:1.4">${wk}</div><div class="tot">التوتال: ${money(c.wkTotal)}</div></td>
          <td><b>${money(c.totalCost)}</b></td>
          <td><button class="btn btn-success btn-sm" onclick="openSellModal(${c.id})"><i class="fa-solid fa-handshake"></i> بيع</button></td>
        </tr>`;
      }).join('') || '<tr><td colspan="9" class="muted" style="text-align:center">لا توجد سيارات متاحة</td></tr>';
    }

    // ================= البيع =================
    function openSellModal(id) {
      const car = S.inventory.find(c => c.id === id);
      if (!car) return;
      $('modalTargetCarId').value = id;
      $('sellCarInfo').innerHTML = `السيارة: <b>${esc(car.name)}</b> | لوحة: <b>${esc(car.plate)}</b> | التكلفة الكلية: <b>${money(car.totalCost)}</b>`;
      ['bName', 'bPhone', 'bNatId', 'bAddr', 'bSellPrice', 'bRemPrice'].forEach(i => $(i).value = '');
      $('bPaidPrice').value = '0'; $('bPenalty').value = '0';
      $('bPayMethod').value = 'cash'; $('bPoa').value = 'no'; $('bFinal').value = 'no';
      $('bSellDate').value = today(); delete $('bSellDate').dataset.manual; $('bDueDate').value = today();
      openModal('sellModal');
    }
    function calcRemainingSell() {
      const rem = num('bSellPrice') - num('bPaidPrice');
      $('bRemPrice').value = rem >= 0 ? rem : 0;
    }
    function setDueDateOffset(m) { const d = new Date(); d.setMonth(d.getMonth() + m); $('bDueDate').value = ymd(d); }
    function confirmSellAction() {
      const car = S.inventory.find(c => c.id === parseInt($('modalTargetCarId').value));
      if (!car) return toast('السيارة غير موجودة');
      const bName = $('bName').value.trim();
      if (!bName) return toast('اكتب اسم المشتري');
      const sellPrice = num('bSellPrice'), paid = num('bPaidPrice');
      if (sellPrice <= 0) return toast('اكتب سعر البيع');
      if (paid > sellPrice) return toast('المدفوع أكبر من سعر البيع');
      const bPhone = $('bPhone').value.trim(), payMethod = $('bPayMethod').value, sellDate = getDate('bSellDate');
      const rem = sellPrice - paid;
      const rec = {
        id: uid(), at: nowStr(), status: 'sold', carId: car.id, carSnap: car,
        carName: car.name, plate: car.plate, chassis: car.chassis, model: car.model, totalCost: car.totalCost,
        bName, bPhone, bNatId: $('bNatId').value.trim(), bAddr: $('bAddr').value.trim(),
        sellPrice, paidPrice: paid, rem, ajelOriginal: rem, payMethod, sellDate,
        dueDate: rem > 0 ? ($('bDueDate').value || today()) : '',
        profit: sellPrice - car.totalCost,
        poa: $('bPoa').value, final: $('bFinal').value, penalty: num('bPenalty'),
        payments: [], log: []
      };
      rec.log.push({ at: nowStr(), text: 'تم البيع بتاريخ ' + sellDate + ' بسعر ' + fmt(sellPrice) + ' ج.م' });
      if (paid > 0) {
        rec.payments.push({ amount: paid, date: sellDate, method: payMethod, first: true, at: nowStr() });
        receiveMoney(payMethod, paid, bName, bPhone, 'دفعة بيع سيارة ' + car.name + ' - ' + bName, sellDate);
      }
      S.archive.push(rec);
      S.inventory = S.inventory.filter(c => c.id !== car.id);
      closeModal('sellModal');
      commit();
    }

    // ================= الأرشيف =================
    const methodLabel = m => WALLET_NAME[m] || m;
    function payStatus(r) {
      if (r.status === 'returned') return ['مرتجعة', '#475569', '#f1f5f9'];
      if (r.rem <= 0) return ['تم السداد بالكامل', '#059669', '#ecfdf5'];
      if (r.payments.some(p => !p.first)) return ['سداد جزء من المبلغ', '#d97706', '#fffbeb'];
      return ['آجل - لم يُسدد', '#dc2626', '#fef2f2'];
    }
    const statusBadge = r => { const s = payStatus(r); return `<span class="badge" style="color:${s[1]};background:${s[2]}">${s[0]}</span>`; };
    const payHistory = r => r.payments.map(p => `${fmt(p.amount)} ج.م — ${esc(p.date)} — ${methodLabel(p.method)}${p.first ? ' (دفعة أولى)' : ''}`).join('<br>');

    function setSaleStatus(id, field, val) {
      const r = S.archive.find(x => x.id === id); if (!r) return;
      r[field] = val;
      r.log.push({ at: nowStr(), text: (field === 'poa' ? 'التوكيل' : 'البيع النهائي') + ': ' + (val === 'yes' ? 'تم' : 'لم يتم') });
      commit();
    }
    function setPenalty(id, v) {
      const r = S.archive.find(x => x.id === id); if (!r) return;
      r.penalty = parseFloat(v) || 0;
      r.log.push({ at: nowStr(), text: 'تعديل الشرط الجزائي إلى ' + fmt(r.penalty) + ' ج.م' });
      commit();
    }
    function renderArchive() {
      const q = $('searchBox').value.trim().toLowerCase();
      const rows = S.archive.filter(r => r.status === 'sold').slice().reverse().filter(r => !q || [r.carName, r.plate, r.bName, r.bPhone, r.bAddr, r.chassis].join(' ').toLowerCase().includes(q));
      $('archiveList').innerHTML = rows.map(r => {
        const sel = (f, v) => `<select class="field-control" style="padding:4px 8px;font-size:0.8rem;min-width:80px" onchange="setSaleStatus(${r.id},'${f}',this.value)"><option value="no" ${v === 'no' ? 'selected' : ''}>لم يتم</option><option value="yes" ${v === 'yes' ? 'selected' : ''}>تم</option></select>`;
        const logs = r.log.map(l => esc(l.at) + ': ' + esc(l.text)).join('<br>');
        const actions = `${r.rem > 0 ? `<button class="btn btn-success btn-sm" onclick="openPayModal(${r.id})">سداد</button> ` : ''}<button class="btn btn-warning btn-sm" onclick="openReturnModal(${r.id})">إرجاع / استبدال</button>`;
        return `<tr>
          <td><b>${esc(r.carName)}</b><br><span class="plate">${esc(r.plate)}</span><br><small class="muted">${esc(r.model)} ${esc(r.chassis)}</small></td>
          <td><b>${esc(r.bName)}</b><br><small class="muted">${esc(r.bPhone)}</small>${r.bAddr ? `<div class="muted">${esc(r.bAddr)}</div>` : ''}</td>
          <td>إجمالي: <b>${fmt(r.sellPrice)}</b><br>مدفوع: <span style="color:var(--accent-green)">${fmt(r.paidPrice)}</span><br>متبقي: <span style="color:var(--accent-red)">${fmt(r.rem)}</span>${r.dueDate && r.rem > 0 ? `<br><small class="muted">استحقاق: ${esc(r.dueDate)}</small>` : ''}<div class="muted">${payHistory(r)}</div></td>
          <td>${statusBadge(r)}<div class="muted">${logs}</div></td>
          <td>${sel('poa', r.poa)}</td>
          <td>${sel('final', r.final)}</td>
          <td><input type="number" class="field-control" style="padding:4px 8px;font-size:0.8rem;width:100px" value="${r.penalty || 0}" onchange="setPenalty(${r.id},this.value)"></td>
          <td><b style="color:var(--accent-green)">${money(r.profit)}</b></td>
          <td>${actions}</td>
        </tr>`;
      }).join('') || '<tr><td colspan="9" class="muted" style="text-align:center">لا توجد مبيعات</td></tr>';
    }

    // ================= الآجل =================
    function renderAjel() {
      const q = $('ajelSearch').value.trim().toLowerCase();
      const list = S.archive.filter(r => r.status === 'sold' && r.ajelOriginal > 0);
      const rows = list.slice().reverse().filter(r => !q || [r.bName, r.bPhone, r.carName, r.plate].join(' ').toLowerCase().includes(q));
      const totalRem = list.reduce((s, r) => s + r.rem, 0);
      $('ajelSummary').innerHTML = `إجمالي المتبقي بره: <span style="color:var(--accent-red)">${money(totalRem)}</span> | عدد العمليات: ${list.length}`;
      $('ajelList').innerHTML = rows.map(r => {
        const late = r.rem > 0 && r.dueDate && r.dueDate <= today();
        return `<tr>
          <td><b>${esc(r.bName)}</b><br><small class="muted">${esc(r.bPhone)}</small>${r.bAddr ? `<div class="muted">${esc(r.bAddr)}</div>` : ''}</td>
          <td>${esc(r.carName)}<br><span class="plate">${esc(r.plate)}</span></td>
          <td>${money(r.sellPrice)}</td>
          <td style="color:var(--accent-green)"><b>${money(r.paidPrice)}</b></td>
          <td style="color:var(--accent-red)"><b>${money(r.rem)}</b></td>
          <td>${r.rem > 0 ? `<b ${late ? 'style="color:var(--accent-red)"' : ''}>${esc(r.dueDate)}</b>${late ? '<br><small style="color:var(--accent-red)">متأخر / مستحق</small>' : ''}` : '-'}</td>
          <td>${statusBadge(r)}</td>
          <td><div class="muted">${payHistory(r)}</div></td>
          <td>${r.rem > 0 ? `<button class="btn btn-success btn-sm" onclick="openPayModal(${r.id})">سداد</button>` : '-'}</td>
        </tr>`;
      }).join('') || '<tr><td colspan="9" class="muted" style="text-align:center">لا توجد مبالغ آجلة</td></tr>';
    }
    function openPayModal(id) {
      const r = S.archive.find(x => x.id === id); if (!r) return;
      $('payTargetId').value = id;
      $('payInfo').innerHTML = `المشتري: <b>${esc(r.bName)}</b> | السيارة: <b>${esc(r.carName)}</b><br>المتبقي: <b style="color:var(--accent-red)">${money(r.rem)}</b>`;
      $('pAmount').value = ''; $('pMethod').value = 'cash'; $('pDate').value = today(); delete $('pDate').dataset.manual;
      openModal('payModal');
    }
    function confirmPay() {
      const r = S.archive.find(x => x.id === parseInt($('payTargetId').value));
      if (!r || r.status !== 'sold') return;
      const amt = num('pAmount'), method = $('pMethod').value, date = getDate('pDate');
      if (amt <= 0) return toast('اكتب مبلغ الدفعة');
      if (amt > r.rem) return toast('المبلغ أكبر من المتبقي');
      r.paidPrice += amt; r.rem -= amt;
      r.payments.push({ amount: amt, date, method, first: false, at: nowStr() });
      r.log.push({ at: nowStr(), text: 'سداد ' + fmt(amt) + ' ج.م بتاريخ ' + date + ' (' + methodLabel(method) + ')' + (r.rem <= 0 ? ' - تم السداد بالكامل' : ' - المتبقي ' + fmt(r.rem)) });
      receiveMoney(method, amt, r.bName, r.bPhone, 'سداد آجل سيارة ' + r.carName + ' - ' + r.bName, date);
      closeModal('payModal');
      commit();
    }

    // ================= الإرجاع / الاستبدال =================
    function openReturnModal(id) {
      const r = S.archive.find(x => x.id === id); if (!r || r.status !== 'sold') return;
      $('retTargetId').value = id;
      $('retInfo').innerHTML = `السيارة: <b>${esc(r.carName)}</b> (${esc(r.plate)}) | المشتري: <b>${esc(r.bName)}</b><br>سعر البيع: <b>${money(r.sellPrice)}</b> | المشتري دفع قبل كده: <b>${money(r.paidPrice)}</b> | الشرط الجزائي: <b>${money(r.penalty)}</b>`;
      $('rType').value = 'return';
      $('rPenalty').value = r.penalty || 0; $('rRefund').value = '0';
      $('rNewPrice').value = ''; $('rPayNow').value = '0'; $('rDue').value = today(); $('rDiffInfo').innerHTML = '';
      $('rPenMethod').value = 'cash'; $('rDate').value = today(); delete $('rDate').dataset.manual; $('rNote').value = '';
      toggleRetType();
      openModal('returnModal');
    }
    function toggleRetType() {
      const ex = $('rType').value === 'exchange';
      $('rReturnBox').style.display = ex ? 'none' : 'grid';
      $('rExchangeBox').style.display = ex ? 'grid' : 'none';
      if (ex) {
        $('rNewCar').innerHTML = S.inventory.length
          ? S.inventory.map(c => `<option value="${c.id}">${esc(c.name)} - ${esc(c.plate)} (تكلفة ${fmt(c.totalCost)})</option>`).join('')
          : '<option value="">لا توجد سيارات متاحة</option>';
      }
    }
    function calcExchangeDiff() {
      const r = S.archive.find(x => x.id === parseInt($('retTargetId').value)); if (!r) return;
      const np = num('rNewPrice');
      $('rDiffInfo').innerHTML = np > 0 ? 'الفرق عن سعر البيعة القديمة (' + fmt(r.sellPrice) + '): <b>' + diffText(np - r.sellPrice) + '</b>' : '';
    }
    function confirmReturn() {
      const r = S.archive.find(x => x.id === parseInt($('retTargetId').value));
      if (!r || r.status !== 'sold') return;
      const type = $('rType').value, pen = num('rPenalty'), pm = $('rPenMethod').value, date = getDate('rDate'), note = $('rNote').value.trim();
      const oldCar = JSON.parse(JSON.stringify(r.carSnap));
      oldCar.notes = oldCar.notes || [];
      const info = { type, date, penalty: pen, refund: 0, note, at: nowStr(), paidBefore: r.paidPrice };

      if (type === 'return') {
        const ref = num('rRefund');
        if (ref > r.paidPrice) return toast('المبلغ المرتد أكبر من المدفوع');
        info.refund = ref;
        oldCar.notes.push('مرتجعة من المشتري ' + r.bName + ' بتاريخ ' + date + (note ? ' (' + note + ')' : ''));
        r.log.push({ at: nowStr(), text: 'إرجاع السيارة للمتاحة - غرامة ' + fmt(pen) + ' - مرتد ' + fmt(ref) });
        if (ref > 0) vaultAdd('withdraw', ref, 'مبلغ مرتد للمشتري ' + r.bName + ' عن سيارة ' + r.carName, date, 'return');
      } else {
        const newCar = S.inventory.find(c => c.id === parseInt($('rNewCar').value));
        const newPrice = num('rNewPrice'), payNow = num('rPayNow');
        if (!newCar) return toast('اختر السيارة البديلة');
        if (newPrice <= 0) return toast('اكتب سعر بيع السيارة الجديدة');
        const carried = Math.min(r.paidPrice, newPrice), excess = r.paidPrice - carried;
        if (payNow > newPrice - carried) return toast('الدفعة أكبر من المتبقي على السيارة الجديدة');
        const diff = newPrice - r.sellPrice;
        const rem = newPrice - carried - payNow;
        const rec = {
          id: uid(), at: nowStr(), status: 'sold', carId: newCar.id, carSnap: newCar,
          carName: newCar.name, plate: newCar.plate, chassis: newCar.chassis, model: newCar.model, totalCost: newCar.totalCost,
          bName: r.bName, bPhone: r.bPhone, bNatId: r.bNatId, bAddr: r.bAddr || '',
          sellPrice: newPrice, paidPrice: carried + payNow, rem, ajelOriginal: rem,
          payMethod: payNow > 0 ? pm : 'transfer', sellDate: date,
          dueDate: rem > 0 ? ($('rDue').value || today()) : '',
          profit: newPrice - newCar.totalCost, poa: 'no', final: 'no', penalty: r.penalty || 0,
          payments: [], log: [], exchangedFrom: r.id
        };
        if (carried > 0) rec.payments.push({ amount: carried, date, method: 'transfer', first: true, at: nowStr() });
        if (payNow > 0) {
          rec.payments.push({ amount: payNow, date, method: pm, first: true, at: nowStr() });
          receiveMoney(pm, payNow, r.bName, r.bPhone, 'دفعة فرق استبدال سيارة ' + newCar.name + ' - ' + r.bName, date);
        }
        rec.log.push({ at: nowStr(), text: 'سيارة بديلة عن ' + r.carName + ' (' + r.plate + ') - ' + diffText(diff) });
        S.archive.push(rec);
        S.inventory = S.inventory.filter(c => c.id !== newCar.id);
        if (excess > 0) vaultAdd('withdraw', excess, 'مبلغ زيادة مرتد للمشتري ' + r.bName + ' بعد الاستبدال', date, 'return');
        oldCar.notes.push('استُبدلت بسيارة ' + newCar.name + ' (' + newCar.plate + ') للمشتري ' + r.bName + ' بتاريخ ' + date + ' — ' + diffText(diff) + (note ? ' (' + note + ')' : ''));
        r.log.push({ at: nowStr(), text: 'استبدال بسيارة ' + newCar.name + ' (' + newCar.plate + ') - ' + diffText(diff) });
        Object.assign(info, { newCarName: newCar.name, newPlate: newCar.plate, newPrice, diff, newRecId: rec.id });
      }

      r.status = 'returned';
      r.penaltyCollected = pen;
      r.returnInfo = info;
      S.inventory.push(oldCar);
      if (pen > 0) receiveMoney(pm, pen, r.bName, r.bPhone, 'غرامة ' + (type === 'exchange' ? 'استبدال' : 'إرجاع') + ' سيارة ' + r.carName + ' - ' + r.bName, date);
      closeModal('returnModal');
      commit();
    }
    function renderReturned() {
      const q = $('retSearch').value.trim().toLowerCase();
      const list = S.archive.filter(r => r.status === 'returned').slice().reverse().filter(r => !q || [r.carName, r.plate, r.bName, r.bPhone].join(' ').toLowerCase().includes(q));
      $('returnedList').innerHTML = list.map(r => {
        const i = r.returnInfo || {}, ex = i.type === 'exchange';
        const details = ex
          ? `استُبدلت بـ <b>${esc(i.newCarName)}</b> (${esc(i.newPlate)})<br>سعر البيع الجديد: ${fmt(i.newPrice)} ج.م<br><b style="color:var(--accent-purple)">${diffText(i.diff)}</b>`
          : '-';
        return `<tr>
          <td><span class="badge" style="color:${ex ? '#7c3aed' : '#d97706'};background:${ex ? '#f5f3ff' : '#fffbeb'}">${ex ? 'استبدال' : 'إرجاع'}</span></td>
          <td><b>${esc(r.carName)}</b><br><span class="plate">${esc(r.plate)}</span></td>
          <td><b>${esc(r.bName)}</b><br><small class="muted">${esc(r.bPhone)}</small></td>
          <td>${esc(i.date)}<br><small class="muted">${esc(i.at)}</small></td>
          <td>${money(i.paidBefore)}</td>
          <td>${money(i.penalty)}</td>
          <td>${money(i.refund)}</td>
          <td>${details}${i.note ? `<div class="muted">ملاحظة: ${esc(i.note)}</div>` : ''}</td>
        </tr>`;
      }).join('') || '<tr><td colspan="8" class="muted" style="text-align:center">لا توجد مرتجعات أو استبدالات</td></tr>';
    }

    // ================= سلة المحذوفات (الحذف معطل - للعرض فقط) =================
    function renderTrash() {
      $('trashList').innerHTML = S.trash.map(t => `<tr><td>${esc(t.type)}</td><td>${esc(t.desc)}</td><td>${fmt(t.amount)} ج.م</td><td>${esc(t.deletedAt)}</td></tr>`).join('') || '<tr><td colspan="4" class="muted" style="text-align:center">لا توجد عناصر محذوفة</td></tr>';
    }

    // ================= تفاصيل الكروت =================
    function openDetailModal(type) {
      let title = '', body = '';
      const list = rows => rows.length ? '<ul style="line-height:2;padding-right:20px">' + rows.map(x => '<li>' + x + '</li>').join('') + '</ul>' : '<p class="muted">لا توجد بيانات</p>';
      const sold = S.archive.filter(r => r.status === 'sold');
      if (type === 'capital') {
        title = 'تفاصيل رأس المال: ' + money(S.capital);
        body = `<div class="table-wrap"><table><thead><tr><th>التاريخ</th><th>وقت التسجيل</th><th>العملية</th><th>من</th><th>إلى</th><th>البيان</th></tr></thead><tbody>${capitalLogRows()}</tbody></table></div>`;
      } else if (type === 'vault') {
        title = 'الخزينة النقدية: ' + money(vaultBal());
        body = list(S.vault.slice().reverse().slice(0, 25).map(v => `${v.type === 'deposit' ? '➕' : '➖'} ${fmt(v.amount)} ج.م | ${esc(v.desc)} | ${esc(v.date)}`));
      } else if (type === 'vodafone' || type === 'instapay') {
        title = 'تفاصيل ' + WALLET_NAME[type] + ': ' + money(walletBal(type));
        body = list(S.wallets.filter(w => w.walletType === type).reverse().map(w => `${w.actionType === 'deposit' ? '➕' : '➖'} ${fmt(w.amount)} ج.م | ${esc(w.party)} | ${esc(w.desc)} | ${esc(w.date)}`));
      } else if (type === 'cars') {
        title = 'السيارات المتاحة';
        body = list(S.inventory.map(c => `<b>${esc(c.name)}</b> (${esc(c.plate)}) - التكلفة ${money(c.totalCost)}`));
      } else if (type === 'profit') {
        title = 'تفاصيل الأرباح';
        body = list(sold.map(r => `${esc(r.carName)} → ${esc(r.bName)} | ربح ${money(r.profit)}`).concat(S.archive.filter(r => r.status === 'returned' && r.penaltyCollected > 0).map(r => `غرامة إرجاع ${esc(r.carName)} (${esc(r.bName)}) | ${money(r.penaltyCollected)}`)));
      } else if (type === 'showExp') {
        title = 'مصروفات المعرض';
        body = list(S.expenses.slice().reverse().map(e => `${esc(e.desc)} | ${money(e.amount)} | ${esc(e.date)}`));
      } else if (type === 'p1' || type === 'p2' || type === 'sh') {
        const s = partnerStat(type);
        title = 'حساب الشريك ' + PARTNER_NAME[type];
        body = `<p style="margin-bottom:10px">إيداع: <b>${money(s.dep)}</b> | سحب: <b>${money(s.wd)}</b> | الصافي: <b>${money(s.net)}</b></p>` + list(S.partners.filter(p => p.partner === type).reverse().map(p => `${p.type === 'withdraw' ? '➖ سحب' : '➕ إيداع'} ${fmt(p.amount)} ج.م | ${esc(p.desc)} | ${esc(p.date)}`));
      } else if (type === 'sold') {
        title = 'العربيات اللي تم بيعها (' + sold.length + ')';
        body = list(sold.slice().reverse().map(r => `<b>${esc(r.carName)}</b> (${esc(r.plate)}) → ${esc(r.bName)} | ${money(r.sellPrice)} | ${esc(r.sellDate)}`));
      } else if (type === 'ajel') {
        title = 'الآجل (اللي بره)';
        body = list(sold.filter(r => r.rem > 0).map(r => `<b>${esc(r.bName)}</b> - ${esc(r.carName)} | متبقي ${money(r.rem)} | استحقاق ${esc(r.dueDate)}`));
      }
      $('detailModalTitle').innerHTML = '<i class="fa-solid fa-circle-info"></i> ' + title;
      $('detailModalBody').innerHTML = body;
      openModal('detailModal');
    }

    // ================= تشغيل =================
    function renderAll() {
      renderInventory(); renderArchive(); renderAjel(); renderReturned(); renderWalletsTable();
      renderPartnerSummary(); renderPartnersTable(); renderCapitalLog();
      renderVaultLogs(); renderExpenses(); renderTrash(); refreshFinancials();
    }
    async function init() {
      DATE_IDS.forEach(i => { $(i).addEventListener('change', () => { $(i).dataset.manual = '1'; }); });
      refreshDateInputs(true);
      tickClock(); setInterval(tickClock, 1000);
      setInterval(() => { refreshDateInputs(); refreshFinancials(); }, 60000);
      try {
        const r = await fetch('/api/state');
        if (r.status === 401) { location.href = '/'; return; }
        const d = await r.json();
        if (d && d.capitalLog) S = Object.assign(S, d);
      } catch (e) { toast('تعذر تحميل البيانات من السيرفر'); }
      if (!S.capitalLog.length) {
        S.capitalLog.push({ id: uid(), at: nowStr(), date: today(), action: 'opening', amount: S.capital, oldVal: 0, newVal: S.capital, desc: 'رصيد افتتاحي' });
        save();
      }
      renderTempWorkshopList();
      renderAll();
    }
    init();
  </script>
  {% endif %}
</body>
</html>
"""


@app.route('/')
def index():
    if not session.get('logged_in'):
        return render_template_string(FULL_HTML_SYSTEM, logged_in=False)
    return render_template_string(FULL_HTML_SYSTEM, logged_in=True)


@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    if username == ADMIN_USER and password == ADMIN_PASS:
        session['logged_in'] = True
        return redirect(url_for('index'))
    return render_template_string(FULL_HTML_SYSTEM, logged_in=False,
                                  login_error="اسم المستخدم أو كلمة المرور غير صحيحة!")


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('index'))


@app.route('/api/state', methods=['GET', 'POST'])
def api_state():
    if not session.get('logged_in'):
        return jsonify({'error': 'unauthorized'}), 401
    if request.method == 'POST':
        data = request.get_json(force=True, silent=True)
        if not isinstance(data, dict):
            return jsonify({'error': 'bad data'}), 400
        with LOCK:
            tmp = STATE_FILE + '.tmp'
            with open(tmp, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False)
            os.replace(tmp, STATE_FILE)
        return jsonify({'ok': True})
    with LOCK:
        if os.path.exists(STATE_FILE):
            with open(STATE_FILE, encoding='utf-8') as f:
                return jsonify(json.load(f))
    return jsonify({})


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
