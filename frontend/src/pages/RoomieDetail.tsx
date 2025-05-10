import { Room } from "../types/room";
import { motion } from "framer-motion";
import { useNavigate } from "react-router-dom";
import { v4 as uuidv4 } from "uuid";
import { useState } from "react";
import LoadingSpinner from "../components/LoadingSpinner";

export default function RoomDetail({
  room,
  onClose,
}: {
  room: Room;
  onClose: () => void;
}) {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);

  const defaultImageUrl =
    "https://github.com/Livinterview/Livinterview/raw/dev/backend/empty-room-gen/inpaint/test.png";
  const imageUrl = room.imageUrl || defaultImageUrl;

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center h-full p-6 bg-white">
        <LoadingSpinner text="방 구조를 분석 중입니다..." />
      </div>
    );
  }

  return (
    <motion.div
      initial={{ y: "100%" }}
      animate={{ y: 0 }}
      exit={{ y: "100%" }}
      transition={{ duration: 0.3, ease: "easeOut" }}
      className="fixed inset-0 z-50 bg-white flex flex-col overflow-auto rounded-t-3xl"
    >
      <div className="flex justify-end p-4">
        <button
          onClick={onClose}
          className="text-sm text-gray-500 hover:underline"
        >
          닫기
        </button>
      </div>

      <div className="w-full h-60 bg-gray-100 flex items-center justify-center">
        <img
          src={imageUrl}
          alt="매물 사진"
          className="object-cover w-full h-full"
        />
      </div>

      <div className="p-6 text-left space-y-4">
        <h2 className="text-2xl font-bold">{room.title}</h2>
        <p className="text-gray-600">{room.address}</p>
        <p className="text-xl font-semibold text-blue-600">
          💰 {room.price}만원 / {room.size}평
        </p>
        <p className="text-sm text-gray-500">※ 본 정보는 예시.</p>

        <button
          onClick={async () => {
            const sessionId = uuidv4();
            setLoading(true);

            try {
              // 1) 원격 이미지 다운로드
              const downloadRes = await fetch(
                "http://localhost:8000/vision/download-image",
                {
                  method: "POST",
                  headers: { "Content-Type": "application/json" },
                  body: JSON.stringify({ image_url: imageUrl }),
                }
              );
              const { image_id } = await downloadRes.json();

              // 2) 구조 분석: 이제 image_id만 전달
              const structureRes = await fetch(
                "http://localhost:8000/vision/analyze-brief",
                {
                  method: "POST",
                  headers: { "Content-Type": "application/json" },
                  body: JSON.stringify({
                    session_id: sessionId,
                    image_id,      // 이전엔 image_url 이었음
                  }),
                }
              );
              const structureData = await structureRes.json();
              // 필요하다면 structureData.brief, detailed 등 사용

              // 3) RoomieClean 화면으로 이동
              navigate("/roomie/clean", {
                state: {
                  imageUrl,
                  title: room.title || "방 정보",
                  sessionId,
                  imageId: image_id,
                  originalImageId: image_id,
                },
              });
            } catch (err) {
              console.error("AI 인테리어 연결 실패:", err);
              alert("AI 인테리어 준비 중 오류가 발생했습니다.");
            } finally {
              setLoading(false);
            }
          }}
          className="w-full mt-4 bg-zipup-600 text-white text-sm py-3 rounded-xl hover:bg-blue-700 transition"
        >
          AI인테리어 도우미 연결
        </button>
      </div>
    </motion.div>
  );
}
