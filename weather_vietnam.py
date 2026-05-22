"""
Thời Tiết Các Tỉnh Thành Việt Nam
Sử dụng Open-Meteo API (miễn phí, không cần API key)
"""

import json
import urllib.request
import urllib.parse
from datetime import datetime

# Danh sách 34 tỉnh thành + tọa độ
PROVINCES = [
    {"name": "An Giang",    "lat": 10.3861, "lon": 105.4350},
    {"name": "Bắc Ninh",   "lat": 21.1861, "lon": 106.0763},
    {"name": "Cà Mau",     "lat": 9.1769,  "lon": 105.1524},
    {"name": "Cần Thơ",    "lat": 10.0452, "lon": 105.7469},
    {"name": "Cao Bằng",   "lat": 22.6667, "lon": 106.2500},
    {"name": "Đà Nẵng",    "lat": 16.0544, "lon": 108.2022},
    {"name": "Đắk Lắk",   "lat": 12.6667, "lon": 108.0500},
    {"name": "Điện Biên",  "lat": 21.3861, "lon": 103.0230},
    {"name": "Đồng Nai",   "lat": 10.9452, "lon": 106.8243},
    {"name": "Đồng Tháp",  "lat": 10.4942, "lon": 105.6880},
    {"name": "Gia Lai",    "lat": 13.9833, "lon": 108.0000},
    {"name": "Hà Nội",     "lat": 21.0285, "lon": 105.8542},
    {"name": "Hà Tĩnh",    "lat": 18.3429, "lon": 105.9057},
    {"name": "Hải Phòng",  "lat": 20.8449, "lon": 106.6881},
    {"name": "Hồ Chí Minh","lat": 10.8231, "lon": 106.6297},
    {"name": "Huế",        "lat": 16.4637, "lon": 107.5909},
    {"name": "Khánh Hòa",  "lat": 12.2388, "lon": 109.1967},
    {"name": "Kiên Giang", "lat": 10.0125, "lon": 105.0809},
    {"name": "Kon Tum",    "lat": 14.3497, "lon": 108.0005},
    {"name": "Lào Cai",    "lat": 22.4809, "lon": 103.9750},
    {"name": "Long An",    "lat": 10.5354, "lon": 106.4070},
    {"name": "Nam Định",   "lat": 20.4388, "lon": 106.1621},
    {"name": "Nghệ An",    "lat": 18.6696, "lon": 105.6813},
    {"name": "Ninh Bình",  "lat": 20.2539, "lon": 105.9745},
    {"name": "Phú Thọ",    "lat": 21.4175, "lon": 105.2380},
    {"name": "Quảng Bình", "lat": 17.4833, "lon": 106.6000},
    {"name": "Quảng Nam",  "lat": 15.5394, "lon": 108.0191},
    {"name": "Quảng Ngãi", "lat": 15.1214, "lon": 108.8042},
    {"name": "Quảng Ninh", "lat": 21.0064, "lon": 107.2925},
    {"name": "Sơn La",     "lat": 21.3256, "lon": 103.9144},
    {"name": "Tây Ninh",   "lat": 11.3100, "lon": 106.0984},
    {"name": "Thanh Hóa",  "lat": 19.8079, "lon": 105.7764},
    {"name": "Tiền Giang", "lat": 10.3597, "lon": 106.3593},
    {"name": "Vĩnh Long",  "lat": 10.2395, "lon": 105.9571},
]

# WMO weather code -> (mô tả tiếng Việt, icon emoji, icon class)
WMO_CODES = {
    0:  ("Trời quang",          "☀️",  "sunny"),
    1:  ("Ít mây",              "🌤️", "mostly-sunny"),
    2:  ("Có mây",              "⛅",  "partly-cloudy"),
    3:  ("Nhiều mây",           "☁️",  "cloudy"),
    45: ("Sương mù",            "🌫️", "fog"),
    48: ("Sương mù đóng băng",  "🌫️", "fog"),
    51: ("Mưa phùn nhẹ",        "🌦️", "drizzle"),
    53: ("Mưa phùn",            "🌦️", "drizzle"),
    55: ("Mưa phùn dày",        "🌧️", "drizzle"),
    61: ("Mưa nhỏ",             "🌧️", "rain"),
    63: ("Mưa vừa",             "🌧️", "rain"),
    65: ("Mưa to",              "🌧️", "heavy-rain"),
    71: ("Tuyết nhẹ",           "🌨️", "snow"),
    73: ("Tuyết vừa",           "❄️",  "snow"),
    75: ("Tuyết dày",           "❄️",  "snow"),
    80: ("Mưa rào nhẹ",         "🌦️", "shower"),
    81: ("Mưa rào vừa",         "🌧️", "shower"),
    82: ("Mưa rào nặng hạt",    "⛈️",  "heavy-shower"),
    85: ("Mưa tuyết nhẹ",       "🌨️", "snow"),
    86: ("Mưa tuyết dày",       "🌨️", "snow"),
    95: ("Giông",               "⛈️",  "thunderstorm"),
    96: ("Giông có mưa đá",     "⛈️",  "thunderstorm"),
    99: ("Giông mưa đá lớn",    "⛈️",  "thunderstorm"),
}


def get_weather_icon_svg(code):
    """Trả về SVG icon dựa trên WMO code"""
    _, _, cls = WMO_CODES.get(code, ("Không rõ", "🌡️", "cloudy"))
    
    if cls in ("sunny", "mostly-sunny"):
        return """<svg viewBox="0 0 48 48" class="weather-icon"><circle cx="24" cy="24" r="10" fill="#FFB800"/><g stroke="#FFB800" stroke-width="2.5" stroke-linecap="round"><line x1="24" y1="4" x2="24" y2="10"/><line x1="24" y1="38" x2="24" y2="44"/><line x1="4" y1="24" x2="10" y2="24"/><line x1="38" y1="24" x2="44" y2="24"/><line x1="9" y1="9" x2="13.5" y2="13.5"/><line x1="34.5" y1="34.5" x2="39" y2="39"/><line x1="39" y1="9" x2="34.5" y2="13.5"/><line x1="13.5" y1="34.5" x2="9" y2="39"/></g></svg>"""
    elif cls in ("drizzle",):
        return """<svg viewBox="0 0 48 48" class="weather-icon"><path d="M12 30 Q8 27 8 22 Q8 14 16 12 Q16 6 24 6 Q32 6 34 13 Q40 13 40 22 Q40 28 34 30Z" fill="#5b9bd5"/><line x1="16" y1="36" x2="14" y2="42" stroke="#5b9bd5" stroke-width="2.5" stroke-linecap="round"/><line x1="24" y1="36" x2="22" y2="42" stroke="#5b9bd5" stroke-width="2.5" stroke-linecap="round"/><line x1="32" y1="36" x2="30" y2="42" stroke="#5b9bd5" stroke-width="2.5" stroke-linecap="round"/></svg>"""
    elif cls in ("rain", "heavy-rain"):
        return """<svg viewBox="0 0 48 48" class="weather-icon"><path d="M10 28 Q6 25 6 20 Q6 12 14 10 Q14 4 22 4 Q30 4 32 11 Q38 11 38 20 Q38 26 32 28Z" fill="#607d9e"/><line x1="13" y1="34" x2="11" y2="44" stroke="#5b9bd5" stroke-width="2.5" stroke-linecap="round"/><line x1="22" y1="34" x2="20" y2="44" stroke="#5b9bd5" stroke-width="2.5" stroke-linecap="round"/><line x1="31" y1="34" x2="29" y2="44" stroke="#5b9bd5" stroke-width="2.5" stroke-linecap="round"/></svg>"""
    elif cls in ("thunderstorm",):
        return """<svg viewBox="0 0 48 48" class="weather-icon"><path d="M8 26 Q4 23 4 18 Q4 10 12 8 Q12 2 20 2 Q28 2 30 9 Q36 9 36 18 Q36 24 30 26Z" fill="#607d9e"/><polygon points="22,28 16,38 22,36 18,46 30,33 23,35" fill="#FFB800"/></svg>"""
    elif cls in ("shower", "heavy-shower"):
        return """<svg viewBox="0 0 48 48" class="weather-icon"><circle cx="30" cy="14" r="8" fill="#FFB800" opacity="0.9"/><path d="M6 30 Q3 27 3 23 Q3 16 10 14 Q11 9 18 9 Q25 9 27 15 Q32 15 32 23 Q32 28 27 30Z" fill="#607d9e"/><line x1="11" y1="35" x2="9" y2="43" stroke="#5b9bd5" stroke-width="2.5" stroke-linecap="round"/><line x1="19" y1="35" x2="17" y2="43" stroke="#5b9bd5" stroke-width="2.5" stroke-linecap="round"/><line x1="27" y1="35" x2="25" y2="43" stroke="#5b9bd5" stroke-width="2.5" stroke-linecap="round"/></svg>"""
    else:  # cloudy, fog, snow, partly-cloudy, default
        return """<svg viewBox="0 0 48 48" class="weather-icon"><path d="M12 34 Q7 31 7 25 Q7 17 15 15 Q15 8 23 8 Q31 8 33 15 Q39 15 39 24 Q39 31 33 34Z" fill="#8bacc8"/><path d="M18 38 Q14 36 14 31 Q14 26 19 25 Q20 21 26 21 Q32 21 33 26 Q37 26 37 31 Q37 36 33 38Z" fill="#a8c4dc"/></svg>"""


def fetch_weather_batch(provinces):
    """Gọi Open-Meteo API theo batch (nhiều location cùng lúc)"""
    results = []
    
    # Open-Meteo hỗ trợ query nhiều location = dùng loop vì free tier
    # Dùng forecast API với current weather
    base_url = "https://api.open-meteo.com/v1/forecast"
    
    for p in provinces:
        params = {
            "latitude": p["lat"],
            "longitude": p["lon"],
            "current": "temperature_2m,apparent_temperature,precipitation,weather_code,wind_speed_10m",
            "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum",
            "timezone": "Asia/Ho_Chi_Minh",
            "forecast_days": "1",
        }
        
        url = base_url + "?" + urllib.parse.urlencode(params)
        
        try:
            with urllib.request.urlopen(url, timeout=10) as response:
                data = json.loads(response.read().decode())
            
            current = data.get("current", {})
            daily = data.get("daily", {})
            
            wmo_code = current.get("weather_code", 3)
            desc, _, _ = WMO_CODES.get(wmo_code, ("Không rõ", "☁️", "cloudy"))
            
            results.append({
                "name": p["name"],
                "temp_current": round(current.get("temperature_2m", 0)),
                "temp_max": round(daily.get("temperature_2m_max", [0])[0]),
                "temp_min": round(daily.get("temperature_2m_min", [0])[0]),
                "precipitation": round(current.get("precipitation", 0), 1),
                "wind_speed": round(current.get("wind_speed_10m", 0)),
                "weather_code": wmo_code,
                "description": desc,
                "icon_svg": get_weather_icon_svg(wmo_code),
            })
            print(f"  ✓ {p['name']}: {current.get('temperature_2m')}°C, {desc}")
            
        except Exception as e:
            print(f"  ✗ {p['name']}: Lỗi - {e}")
            results.append({
                "name": p["name"],
                "temp_current": "--",
                "temp_max": "--",
                "temp_min": "--",
                "precipitation": "--",
                "wind_speed": "--",
                "weather_code": 3,
                "description": "Không có dữ liệu",
                "icon_svg": get_weather_icon_svg(3),
            })
    
    return results


def generate_html(weather_data):
    """Tạo file HTML dashboard"""
    
    cards_html = ""
    for w in weather_data:
        cards_html += f"""
        <div class="card" data-name="{w['name'].lower()}">
            <div class="card-header">
                <span class="province-name">{w['name']}</span>
                <span class="star">☆</span>
            </div>
            <div class="card-body">
                <div class="icon-wrap">{w['icon_svg']}</div>
                <div class="temps">
                    <span class="temp-min">{w['temp_min']}°</span>
                    <span class="temp-max">{w['temp_max']}°</span>
                </div>
            </div>
            <div class="card-desc">{w['description']}</div>
            <div class="card-footer">
                <span class="precip">💧 {w['precipitation']} mm</span>
                <span class="wind">💨 {w['wind_speed']} km/h</span>
            </div>
        </div>
"""
    
    now = datetime.now().strftime("%d/%m/%Y %H:%M")
    count = len(weather_data)
    
    return f"""<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Thời Tiết Các Tỉnh Thành Việt Nam</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  
  body {{
    font-family: 'Segoe UI', system-ui, sans-serif;
    background: #f0f4f8;
    min-height: 100vh;
    color: #1e293b;
  }}

  /* HEADER */
  .header {{
    background: linear-gradient(135deg, #0f172a 0%, #1e3a5f 100%);
    color: white;
    padding: 18px 32px;
    display: flex;
    align-items: center;
    gap: 20px;
    position: sticky;
    top: 0;
    z-index: 100;
    box-shadow: 0 2px 20px rgba(0,0,0,0.3);
  }}

  .logo {{
    background: #1d4ed8;
    border-radius: 12px;
    width: 52px;
    height: 52px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 24px;
    flex-shrink: 0;
  }}

  .header-title h1 {{
    font-size: 20px;
    font-weight: 700;
    letter-spacing: 0.3px;
  }}

  .header-title p {{
    font-size: 12px;
    color: #34d399;
    margin-top: 3px;
    display: flex;
    align-items: center;
    gap: 6px;
  }}

  .header-title p::before {{
    content: '';
    width: 8px;
    height: 8px;
    background: #34d399;
    border-radius: 50%;
    animation: pulse 2s infinite;
  }}

  @keyframes pulse {{
    0%, 100% {{ opacity: 1; transform: scale(1); }}
    50% {{ opacity: 0.6; transform: scale(1.3); }}
  }}

  .header-right {{
    margin-left: auto;
    display: flex;
    align-items: center;
    gap: 16px;
  }}

  .stat-badge {{
    text-align: center;
    background: rgba(255,255,255,0.1);
    padding: 8px 16px;
    border-radius: 10px;
    border: 1px solid rgba(255,255,255,0.15);
  }}

  .stat-badge .num {{
    font-size: 28px;
    font-weight: 800;
    color: white;
    line-height: 1;
  }}

  .stat-badge .label {{
    font-size: 10px;
    color: #94a3b8;
    letter-spacing: 1px;
    text-transform: uppercase;
  }}

  .search-box {{
    background: rgba(255,255,255,0.1);
    border: 1px solid rgba(255,255,255,0.2);
    border-radius: 10px;
    padding: 10px 16px;
    color: white;
    font-size: 14px;
    width: 220px;
    outline: none;
    transition: all 0.2s;
  }}

  .search-box::placeholder {{ color: rgba(255,255,255,0.45); }}
  .search-box:focus {{ background: rgba(255,255,255,0.18); border-color: rgba(255,255,255,0.4); }}

  .updated-at {{
    font-size: 11px;
    color: #64748b;
    text-align: center;
    padding: 10px;
    margin-top: 4px;
  }}

  /* GRID */
  .container {{
    max-width: 1600px;
    margin: 0 auto;
    padding: 20px 16px;
  }}

  .grid {{
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 12px;
  }}

  @media (max-width: 900px)  {{ .grid {{ grid-template-columns: repeat(3, minmax(0, 1fr)); }} }}
  @media (max-width: 620px)  {{ .grid {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }} }}
  @media (max-width: 400px)  {{ .grid {{ grid-template-columns: 1fr; }} }}

  /* CARD */
  .card {{
    background: white;
    border-radius: 14px;
    padding: 14px 16px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06), 0 2px 10px rgba(0,0,0,0.04);
    transition: transform 0.2s, box-shadow 0.2s;
    border: 1px solid #e8eef4;
  }}

  .card:hover {{
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(0,0,0,0.09);
  }}

  .card.hidden {{ display: none; }}

  .card-header {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 10px;
  }}

  .province-name {{
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 0.5px;
    color: #334155;
    text-transform: uppercase;
  }}

  .star {{
    font-size: 16px;
    color: #cbd5e1;
    cursor: pointer;
    transition: color 0.2s;
  }}
  .star:hover {{ color: #f59e0b; }}

  .card-body {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 10px;
  }}

  .icon-wrap {{ width: 44px; height: 44px; flex-shrink: 0; }}
  .weather-icon {{ width: 100%; height: 100%; }}

  .temps {{
    display: flex;
    flex-direction: column;
    align-items: flex-end;
    gap: 0;
  }}

  .temp-min {{
    font-size: 15px;
    font-weight: 600;
    color: #2563eb;
  }}

  .temp-max {{
    font-size: 28px;
    font-weight: 800;
    color: #e11d48;
    line-height: 1;
  }}

  .card-desc {{
    background: #f1f5f9;
    border-radius: 7px;
    padding: 5px 10px;
    font-size: 12px;
    color: #475569;
    text-align: center;
    margin-bottom: 10px;
    font-weight: 500;
  }}

  .card-footer {{
    display: flex;
    justify-content: space-between;
    font-size: 12px;
    color: #64748b;
  }}

  .precip, .wind {{
    display: flex;
    align-items: center;
    gap: 4px;
  }}

  /* NO RESULT */
  .no-result {{
    display: none;
    text-align: center;
    padding: 60px 20px;
    color: #94a3b8;
    font-size: 16px;
    grid-column: 1/-1;
  }}

  /* RESPONSIVE */
  @media (max-width: 600px) {{
    .header {{ flex-wrap: wrap; padding: 14px 16px; }}
    .header-right {{ width: 100%; }}
    .search-box {{ width: 100%; }}
    .stat-badge .num {{ font-size: 22px; }}
  }}
</style>
</head>
<body>

<div class="header">
  <div class="logo">🗺️</div>
  <div class="header-title">
    <h1>Thời Tiết Các Tỉnh Thành</h1>
    <p>Cập nhật realtime từ Open-Meteo API</p>
  </div>
  <div class="header-right">
    <div class="stat-badge">
      <div class="num">{count}</div>
      <div class="label">Tỉnh Thành</div>
    </div>
    <input class="search-box" type="text" id="search" placeholder="Tìm tỉnh thành..." oninput="filterCards(this.value)">
  </div>
</div>

<div class="container">
  <p class="updated-at">Cập nhật lúc: {now} | Nguồn dữ liệu: Open-Meteo API (openmeteo.com)</p>
  <div class="grid" id="grid">
    {cards_html}
    <div class="no-result" id="noResult">Không tìm thấy tỉnh thành nào 🔍</div>
  </div>
</div>

<script>
function filterCards(q) {{
  const query = q.toLowerCase().trim();
  const cards = document.querySelectorAll('.card');
  let found = 0;
  cards.forEach(c => {{
    const match = c.dataset.name.includes(query);
    c.classList.toggle('hidden', !match);
    if (match) found++;
  }});
  document.getElementById('noResult').style.display = found === 0 ? 'block' : 'none';
}}
</script>

</body>
</html>"""


def main():
    print("🌤️  Đang lấy dữ liệu thời tiết từ Open-Meteo API...")
    print(f"   Tổng số tỉnh thành: {len(PROVINCES)}\n")
    
    weather_data = fetch_weather_batch(PROVINCES)
    
    print(f"\n📊 Đã lấy được {len(weather_data)} tỉnh thành")
    print("🎨 Đang tạo file HTML...")
    
    html = generate_html(weather_data)
    
    output_file = "index.html"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html)
    
    print(f"✅ Xong! Mở file: {output_file}")
    print("   Hoặc chạy: python -m http.server 8000 rồi vào http://localhost:8000/index.html")


if __name__ == "__main__":
    main()
