import { MapContainer, TileLayer, Marker, Popup } from "react-leaflet"
import "leaflet/dist/leaflet.css"
import { Room } from "../types/room"
import L from "leaflet"

// 마커 아이콘 fix (기본 마커 오류 해결용) 예시 -> 지도 뭐쓸지도 아직잘모르게씀
import markerIcon2x from "leaflet/dist/images/marker-icon-2x.png"
import markerIcon from "leaflet/dist/images/marker-icon.png"
import markerShadow from "leaflet/dist/images/marker-shadow.png"

delete (L.Icon.Default.prototype as any)._getIconUrl
L.Icon.Default.mergeOptions({
  iconRetinaUrl: markerIcon2x,
  iconUrl: markerIcon,
  shadowUrl: markerShadow,
})
// mockdata ->DB로 대체예정
const dummyRooms: Room[] = [
  {
    id: "1",
    title: "깔끔한 원룸",
    address: "서울시 강남구",
    lat: 37.4979,
    lng: 127.0276,
    price: 95,
    size: 12,
  },
  {
    id: "2",
    title: "넓은 투룸",
    address: "서울시 마포구",
    lat: 37.5565,
    lng: 126.9229,
    price: 130,
    size: 20,
  },
]

export default function MapView({ onPinClick }: { onPinClick: (room: Room) => void }) {
  return (
    <MapContainer center={[37.541, 126.986]} zoom={12} className="w-full h-full z-0">
      <TileLayer
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        attribution="&copy; OpenStreetMap contributors"
      />
      {dummyRooms.map((room) => (
        <Marker
          key={room.id}
          position={[room.lat, room.lng]}
          eventHandlers={{
            click: () => onPinClick(room),
          }}
        >
          <Popup>{room.title}</Popup>
        </Marker>
      ))}
    </MapContainer>
  )
}
