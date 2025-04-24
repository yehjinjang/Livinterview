import { useEffect, useState } from "react"
import { useNavigate } from "react-router-dom"
import BottomTabBar from "../components/BottomTabBar"
import { User, Star, LogOut } from "lucide-react"

export default function ProfilePage() {
  const [email, setEmail] = useState<string>("")
  const [name, setName] = useState<string>("")
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
        console.log("🙋 회원 정보:", data)
        sessionStorage.setItem("user", JSON.stringify(data))
        setEmail(data.email)
        setName(data.name)
      })
      .catch(() => {
        sessionStorage.removeItem("user")
        navigate("/login")
      })
  }, [])

  const handleLogout = () => {
    sessionStorage.removeItem("user")
    navigate("/login")
  }

  return (
    <div className="flex flex-col h-screen bg-white relative">
      <div className="flex flex-col items-center px-6 pt-48 pb-20">
        <div className="w-20 h-20 bg-purple-100 rounded-full flex items-center justify-center text-purple-600">
          <User className="w-10 h-10" />
        </div>
        <p className="mt-4 text-gray-800 font-medium text-lg">{name}</p>
        <p className="text-sm text-gray-500">{email}</p>

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