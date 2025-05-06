import { Room } from "../types/room"
import { motion } from "framer-motion"
import { useNavigate } from "react-router-dom"

export default function RoomDetail({
  room,
  onClose,
}: {
  room: Room
  onClose: () => void
}) {
  const navigate = useNavigate()

  return (
    <motion.div
      initial={{ y: "100%" }}
      animate={{ y: 0 }}
      exit={{ y: "100%" }}
      transition={{ duration: 0.3, ease: "easeOut" }}
      className="fixed inset-0 z-50 bg-white flex flex-col overflow-auto rounded-t-3xl"
    >
      {/* 상단 닫기 버튼 */}
      <div className="flex justify-end p-4">
        <button onClick={onClose} className="text-sm text-gray-500 hover:underline">
          닫기
        </button>
      </div>

      {/* 매물 이미지 예시 */}
      <div className="w-full h-60 bg-gray-100 flex items-center justify-center">
        <img
          src={room.imageUrl || "/icons/images.jpg"}
          alt="매물 사진"
          className="object-cover w-full h-full"
        />
      </div>

      {/* 상세 정보 */}
      <div className="p-6 text-left space-y-4">
        <h2 className="text-2xl font-bold">{room.title}</h2>
        <p className="text-gray-600">{room.address}</p>
        <p className="text-xl font-semibold text-blue-600">
          💰 {room.price}만원 / {room.size}평
        </p>
        <p className="text-sm text-gray-500">※ 본 정보는 예시.</p>

        {/* AI 인테리어 연결 */}
        <button
          onClick={() => navigate("/roomie/clean", {
            state: {
              imageUrl: room.imageUrl || "https://d1774jszgerdmk.cloudfront.net/1024/lm8eYHMOCkTo_TysRVv38", 
              title: room.title || "방 정보",
            }
          })}
          className="w-full mt-4 bg-zipup-600 text-white text-sm py-3 rounded-xl hover:bg-blue-700 transition"
        >
          AI인테리어 도우미 연결
        </button>
      </div>
    </motion.div>
  )
}