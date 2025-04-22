import { useState } from "react"
import MapView from "../components/MapView"
import RoomInfo from "../components/RoomInfo"
import BottomTabBar from "../components/BottomTabBar"
import { Room } from "../types/room"

export default function RoomieHome() {
  const [selectedRoom, setSelectedRoom] = useState<Room | null>(null)

  return (
    <div className="w-full h-screen flex flex-col relative">
      {/* 지도 + 모달 영역 */}
      <div className="flex-1 relative">
        <MapView onPinClick={(room) => setSelectedRoom(room)} />
        {selectedRoom && (
          <RoomInfo room={selectedRoom} onClose={() => setSelectedRoom(null)} />
        )}
      </div>

      {/* 하단 탭바 */}
      <BottomTabBar />
    </div>
  )
}