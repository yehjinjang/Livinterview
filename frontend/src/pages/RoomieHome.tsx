import { useState } from "react"
import MapView from "../components/MapView"
import RoomInfo from "../components/RoomInfo"
import RoomDetail from "../pages/RoomieDetail"
import BottomTabBar from "../components/BottomTabBar"
import { Room } from "../types/room"

export default function RoomieHome() {
  const [selectedRoom, setSelectedRoom] = useState<Room | null>(null)
  const [showDetail, setShowDetail] = useState(false) // 상세 모달 상태

  return (
    <div className="w-full h-screen flex flex-col relative">
      <div className="flex-1 relative">
        <MapView onPinClick={(room) => {
          setSelectedRoom(room)
          setShowDetail(false) // 처음엔 요약부터
        }} />
      </div>

      <BottomTabBar />

      {/* RoomInfo modal */}
      {selectedRoom && !showDetail && (
        <RoomInfo
          room={selectedRoom}
          onExpand={() => setShowDetail(true)} // 다시 탭 → 확장
          onClose={() => setSelectedRoom(null)}
        />
      )}

      {/* 전체 상세 모달 */}
      {selectedRoom && showDetail && (
        <RoomDetail
          room={selectedRoom}
          onClose={() => {
            setSelectedRoom(null)
            setShowDetail(false)
          }}
        />
      )}
    </div>
  )
}