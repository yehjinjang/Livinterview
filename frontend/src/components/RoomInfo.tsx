import { Room } from "../types/room"
export default function RoomInfo({
  room,
  onClose,
}: {
  room: Room
  onClose: () => void
}) {
  return (
    <div className="absolute bottom-4 left-4 right-4 bg-white p-4 rounded-xl shadow-lg z-[999]">
      <div className="flex justify-between items-center mb-2">
        <h2 className="text-lg font-bold">{room.title}</h2>
        <button onClick={onClose} className="text-sm text-gray-500 hover:underline">
          닫기
        </button>
      </div>
      <p className="text-sm text-gray-600 mb-1">{room.address}</p>
      <p className="text-sm">💰 {room.price}만원 / {room.size}평</p>
    </div>
  )
}
