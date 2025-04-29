import { useEffect, useRef } from "react"
import { Room } from "../types/room"

declare global {
  interface Window {
    kakao: any
  }
}

interface MapViewProps {
  onPinClick: (room: Room) => void
}

export default function MapView({ onPinClick }: MapViewProps) {
  const mapRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    // 이미 로드되어 있으면 바로 실행
    if (window.kakao && window.kakao.maps && mapRef.current) {
      initMap()
      return
    }

    // 스크립트 동적으로 삽입
    const script = document.createElement("script")
    script.src = `https://dapi.kakao.com/v2/maps/sdk.js?appkey=${import.meta.env.VITE_KAKAO_API_KEY}&autoload=false&libraries=services`
    script.async = true
    document.head.appendChild(script)

    script.onload = () => {
      if (!window.kakao || !window.kakao.maps || !mapRef.current) {
        console.error("❌ Kakao SDK 로드 실패")
        return
      }

      window.kakao.maps.load(() => {
        initMap()
      })
    }

    return () => {
      document.head.removeChild(script)
    }
  }, [])

  const initMap = () => {
    if (!mapRef.current) return

    const map = new window.kakao.maps.Map(mapRef.current, {
      center: new window.kakao.maps.LatLng(37.5665, 126.978),
      level: 5,
    })

    const sampleRoom: Room = {
      id: "1",
      title: "예시 원룸",
      address: "서울시 중구 세종대로",
      lat: 37.5665,
      lng: 126.978,
      price: "1억",
      size: 18,
      imageUrl: "",
    }

    const marker = new window.kakao.maps.Marker({
      position: new window.kakao.maps.LatLng(sampleRoom.lat, sampleRoom.lng),
      map,
    })

    window.kakao.maps.event.addListener(marker, "click", () => {
      onPinClick(sampleRoom)
    })
  }

  return <div ref={mapRef} className="w-full h-full bg-gray-100" />
}