import { Room } from "../types/room"

export default function RoomInfo({
  room,
  onExpand,
  onClose
}: {
  room: Room
  onExpand: () => void
  onClose: () => void
}) {
  return (
    <div
      className="absolute bottom-16 left-4 right-4 bg-white p-4 rounded-xl shadow-lg cursor-pointer z-50"
      onClick={onExpand}
    >
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-lg font-bold">{room.title}</h2>
          <p className="text-sm text-gray-600">{room.address}</p>
          <p className="text-blue-600 font-semibold mt-1">
            {room.price}만원 / {room.size}평
          </p>
        </div>
        <button onClick={(e) => {
          e.stopPropagation()
          onClose()
        }} className="text-xs text-gray-400 hover:text-red-400">닫기</button>
      </div>
    </div>
  )
}