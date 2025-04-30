# insert_rooms.py

import os
import sys
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from pathlib import Path
from datetime import datetime
import schedule
import time

# 시스템 경로에 프로젝트 루트 추가 (room_list_crawler.py를 찾기 위함)
sys.path.append(str(Path(__file__).resolve().parent.parent))

# 모델 및 크롤링 함수 불러오기
from backend.models import Base, SeoulRoom
from crawling.room_list_crawler import crawl_all_dongs

def run_insert():
    # ───── 1. DB 연결 ─────
    load_dotenv()
    engine = create_engine(os.getenv("DB_URL"), echo=False)
    Session = sessionmaker(bind=engine)

    try:
        session = Session()
        session.execute(text("SELECT 1"))
        print("\n✅ DB 연결 성공!")
    except Exception as e:
        print("\n⛔ DB 연결 실패:", e)
        return

    # ───── 2. 테이블 생성 (최초 1회) ─────
    Base.metadata.create_all(bind=engine)

    # ───── 3. 크롤링 데이터 수집 ─────
    df = crawl_all_dongs()

    if df.empty:
        print("⛔ 크롤링 결과가 없어 저장을 생략합니다.")
        return

    print(f"🔍 크롤링된 매물 수: {len(df)}개")

    # ───── 4. NaN → None 변환 ─────
    df = df.replace({pd.NA: None, float("nan"): None})

    # ───── 5. ORM 방식으로 DB 저장 ─────
    session = Session()

    # 기존 데이터 전체 삭제
    deleted = session.query(SeoulRoom).delete()
    session.commit()
    print(f"🗑️ 기존 매물 {deleted}개 삭제 완료.")

    inserted_count = 0

    for _, row in df.iterrows():
        room = SeoulRoom(
            dong_code=row["dong_code"],
            gu_name=row["gu_name"],
            dong_name=row["dong_name"],
            seq=row["seq"],
            room_type=row["roomTypeName"],
            room_title=row["roomTitle"],
            room_desc=row["roomDesc"],
            price_type=row["priceTypeName"],
            price_info=row["priceTitle"],
            img_url_list=row["imgUrlList"],
            lat=row["lat"],
            lng=row["lng"],
            floor=row["floor"],
            area_m2=row["area_m2"],
            maintenance_fee=row["maintenance_fee"]
        )
        session.add(room)
        inserted_count += 1

    session.commit()
    session.close()
    print(f"✅ 총 {inserted_count}개 매물이 DB에 저장되었습니다. 🕒 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

def schedule_insert(hour="16", minute="40"):
    schedule_time = f"{hour.zfill(2)}:{minute.zfill(2)}"
    print(f"⏰ 매일 {schedule_time}에 자동 저장 작업이 실행됩니다.")
    schedule.every().day.at(schedule_time).do(run_insert)
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    schedule_insert()
