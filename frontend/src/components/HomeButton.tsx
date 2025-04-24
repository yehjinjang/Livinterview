import { useNavigate } from "react-router-dom"
import { Home } from "lucide-react"

export default function HomeButton() {
  const navigate = useNavigate()

  const handleHomeClick = () => {
    const confirm = window.confirm(
      "홈으로 이동하면 지금까지의 선택이 모두 초기화됩니다.\n계속하시겠어요?"
    )
    if (confirm) {
      navigate("/")
    }
  }

  return (
    <button
      onClick={handleHomeClick}
      className="w-10 h-10 rounded-full text-gray text-gray flex items-center justify-center shadow hover:text-gray transition"
    >
      <Home size={18} />
    </button>
  )
}
