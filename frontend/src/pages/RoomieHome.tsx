import { useState } from "react"
import MapView from "../components/MapView"
import RoomInfo from "../components/RoomInfo"
import RoomDetail from "./RoomieDetail"
import BottomTabBar from "../components/BottomTabBar"
import { Room } from "../types/room"

export default function RoomieHome() {
  const [selectedRoom, setSelectedRoom] = useState<Room | null>(null)
  const [showDetail, setShowDetail] = useState(false)

  return (
    <div className="flex flex-col w-full h-screen">
      {/* 지도 영역  */}
      <div className="flex-1">
        <MapView
          onPinClick={(room) => {
            setSelectedRoom(room)
            setShowDetail(false)
          }}
        />
      </div>

      <div className="h-14">
        <BottomTabBar />
      </div>

      {/* 요약 정보 모달 */}
      {selectedRoom && !showDetail && (
        <RoomInfo
          room={selectedRoom}
          onExpand={() => setShowDetail(true)}
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
