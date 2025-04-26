import json, time, pandas as pd
import requests
import re
from pathlib import Path

# ORM 및 DB 연결
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv


import sys
from pathlib import Path
# Livinterview 디렉토리를 sys.path에 추가
sys.path.append(str(Path(__file__).resolve().parent.parent))

from backend.models import SeoulRoom

load_dotenv()

DATABASE_URL = os.getenv("DB_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)


# ───── 기본 설정 (유지) ─────
PAGE_SIZE   = 50
MAX_PAGES   = 20
ZOOM        = 13
USE_MAP     = "naver"
BASE_URL    = "https://www.dabangapp.com/api/v5/room-list/category/one-two/region"

HEADERS = {
    "accept": "application/json, text/plain, */*",
    "user-agent": "Mozilla/5.0",
    "d-api-version": "5.0.0",
    "d-call-type": "web",
    "d-app-version": "1",
    "csrf": "token"
}

FILTERS = {
    "sellingTypeList": ["MONTHLY_RENT", "LEASE"],
    "depositRange": {"min": 0, "max": 999999},
    "priceRange":   {"min": 0, "max": 999999},
    "isIncludeMaintenance": False,
    "pyeongRange": {"min": 0, "max": 999999},
    "useApprovalDateRange": {"min": 0, "max": 999999},
    "roomFloorList": ["GROUND_FIRST", "GROUND_SECOND_OVER", "SEMI_BASEMENT", "ROOFTOP"],
    "roomTypeList":  ["ONE_ROOM", "TWO_ROOM"],
    "dealTypeList":  ["AGENT", "DIRECT"],
    "canParking": False,
    "isShortLease": False,
    "hasElevator": False,
    "hasPano": False,
    "isDivision": False,
    "isDuplex": False,
}

KEEP_COLS = [
    "id", "seq", "roomTypeName", "roomTitle", "roomDesc", "priceTypeName",
    "priceTitle", "randomLocation", "imgUrlList"
]

# ───── roomDesc 파싱 함수 ─────
def parse_room_desc(desc):
    floor, area, fee = None, None, 0
    if isinstance(desc, str):
        parts = [p.strip() for p in desc.split(",")]
        if len(parts) == 3:
            floor = parts[0]
            area_raw = parts[1].replace("m²", "").strip()
            area = float(area_raw) if area_raw else None

            fee_raw = parts[2].replace("관리비", "").strip()
            if "없음" in fee_raw:
                fee = 0
            elif "만" in fee_raw:
                fee = float(fee_raw.replace("만", "")) * 10000
            else:
                fee = float(re.sub(r"[^\d.]", "", fee_raw) or 0)
    return pd.Series([floor, area, int(fee)])


# ───── 수동 매핑 함수 ─────
def df_to_seoulroom_records(df):
    # NaN 값을 None으로 변환 (MySQL 저장 오류 방지)
    df = df.replace({pd.NA: None, pd.NaT: None, float('nan'): None})

    mapped_records = []
    for _, row in df.iterrows():
        record = {
            "dong_code": str(row.get("dong_code") or "").strip(),
            "gu_name": str(row.get("gu_name") or "").strip(),
            "dong_name": str(row.get("dong_name") or "").strip(),
            "seq": int(row.get("seq") or 0),
            "room_type": str(row.get("roomTypeName") or "").strip(),
            "room_title": str(row.get("roomTitle") or "").strip(),
            "room_desc": str(row.get("roomDesc") or "").strip(),
            "price_type": str(row.get("priceTypeName") or "").strip(),
            "price_info": str(row.get("priceTitle") or "").strip(),
            "img_url_list": json.dumps(row.get("imgUrlList") or []),
            "lat": row.get("lat") if pd.notna(row.get("lat")) else None,
            "lng": row.get("lng") if pd.notna(row.get("lng")) else None,
            "floor": str(row.get("floor") or "").strip(),
            "area_m2": row.get("area_m2") if pd.notna(row.get("area_m2")) else None,
            "maintenance_fee": int(row.get("maintenance_fee") or 0),
        }
        mapped_records.append(record)
    return mapped_records


# ───── 메인 크롤링 함수 ─────
# 함수명 + CSV 제거 + DB 저장 로직으로 변경
def crawl_all_dongs():
    session = SessionLocal()
    dong_df = pd.read_sql("SELECT * FROM Seoul_dong_codes", session.bind)
    dong_df["code"] = dong_df["code"].astype(str)

    all_rows = []

    for _, row in dong_df.iterrows():
        dong_code = row["code"]
        dong_name = row["dong_name"]
        gu_name   = row["gu_name"]
        region_code = dong_code[:8]
        bbox = {
            "sw": {"lat": 37.4451338, "lng": 126.925623},
            "ne": {"lat": 37.5546292, "lng": 127.0488759}
        }

        print(f"{gu_name} {dong_name}({region_code}) 수집 시작")
        rows = []
        for page in range(1, MAX_PAGES + 1):
            params = {
                "filters": json.dumps(FILTERS, separators=(',', ':')),
                "bbox": json.dumps(bbox, separators=(',', ':')),
                "zoom": ZOOM,
                "useMap": USE_MAP,
                "page": page,
                "code": region_code,
            }

            try:
                r = requests.get(BASE_URL, headers=HEADERS, params=params, timeout=20)
            except requests.exceptions.ReadTimeout:
                print(f"[{dong_name}] page {page}: ReadTimeout 발생. 해당 페이지 스킵")
                break

            if r.status_code != 200:
                print(f"[{dong_name}] page {page}: HTTP {r.status_code} → 재시도 중 …")
                time.sleep(1)
                for _ in range(2):
                    try:
                        r = requests.get(BASE_URL, headers=HEADERS, params=params, timeout=20)
                        if r.status_code == 200:
                            break
                    except requests.exceptions.ReadTimeout:
                        continue
                    time.sleep(1)
                else:
                    print("   계속 실패, 루프 중단")
                    break

            data = r.json()["result"]
            rows.extend(data["roomList"])
            for premium_block in data.get("premiumList", []):
                rows.extend(premium_block["roomList"])

            if not data.get("hasMore"):
                break
            time.sleep(0.5)

        for r in rows:
            r["dong_code"] = dong_code
            r["dong_name"] = dong_name
            r["gu_name"] = gu_name
            if isinstance(r.get("randomLocation"), dict):
                r["lat"] = r["randomLocation"].get("lat")
                r["lng"] = r["randomLocation"].get("lng")

        all_rows.extend(rows)

    if all_rows:
        df = pd.DataFrame(all_rows)
        df[["floor", "area_m2", "maintenance_fee"]] = df["roomDesc"].apply(parse_room_desc)
        df = df[["dong_code", "gu_name", "dong_name"] + KEEP_COLS + ["lat", "lng", "floor", "area_m2", "maintenance_fee"]]

        # ORM 기반 DB 저장
        try:
            records = df_to_seoulroom_records(df)  # 수동 맵핑 적용
            session.bulk_insert_mappings(SeoulRoom, records)
            session.commit()
            print("✅ DB 저장 완료 → seoul_rooms 테이블")

        except Exception as e:
            session.rollback()
            print(f"⛔ 저장 실패: {e}")
        finally:
            session.close()
    else:
        print("⛔ 저장할 데이터가 없습니다.")

if __name__ == "__main__":
    crawl_all_dongs()
