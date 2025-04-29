import { useEffect, useState } from "react"
import { useNavigate } from "react-router-dom"
import BottomTabBar from "../components/BottomTabBar"
import { User, Star, LogOut } from "lucide-react"

export default function ProfilePage() {
  const [email, setEmail] = useState<string>("")
  const [name, setName] = useState<string>("")
  const [provider, setProvider] = useState<string>("") // 로그인 플랫폼
  const navigate = useNavigate()

  useEffect(() => {
    fetch("http://localhost:8000/me", {
      credentials: "include",
    })
      .then((res) => {
        if (!res.ok) throw new Error("Not logged in")
        return res.json()
      })
      .then((data) => {
        console.log("🙋 전체 회원 정보:", data)
        console.log("🛡 로그인 소셜:", data.provider)
        console.log("🧑‍💻 이름:", data.name)
        console.log("📧 이메일:", data.email)

        sessionStorage.setItem("user", JSON.stringify(data))
        setEmail(data.email)
        setName(data.name)
        setProvider(data.provider)
      })
      .catch(() => {
        sessionStorage.removeItem("user")
        navigate("/profile")
      })
  }, [])

  const handleLogout = () => {
    sessionStorage.removeItem("user")
    navigate("/profile")
  }

  return (
    <div className="flex flex-col h-screen bg-white relative">
      <div className="flex flex-col items-center px-6 pt-48 pb-20">
        <div className="w-20 h-20 bg-purple-100 rounded-full flex items-center justify-center text-purple-600">
          <User className="w-10 h-10" />
        </div>

        <p className="mt-4 text-gray-800 font-medium text-lg">{name}</p>
        <p className="text-sm text-gray-500">{email}</p>
        {/* 추가: 소셜 플랫폼 표시 */}
        {provider && (
          <p className="text-xs text-gray-400 mt-1">
            로그인 플랫폼: {provider.toUpperCase()}
          </p>
        )}

        <div className="mt-10 w-full space-y-4">
          <div
            className="flex items-center justify-between border-t pt-4 cursor-pointer"
            onClick={() => alert("아직 구현중이에요!")}
          >
            <div className="flex items-center gap-3 text-gray-700">
              <Star className="w-5 h-5" />
              <span>History</span>
            </div>
            <span className="text-gray-400">›</span>
          </div>

          <div
            className="flex items-center justify-between border-t pt-4 cursor-pointer"
            onClick={handleLogout}
          >
            <div className="flex items-center gap-3 text-gray-700">
              <LogOut className="w-5 h-5" />
              <span>Logout</span>
            </div>
            <span className="text-gray-400">›</span>
          </div>
        </div>
      </div>

      <div className="absolute bottom-0 w-full">
        <BottomTabBar />
      </div>
    </div>
  )
}