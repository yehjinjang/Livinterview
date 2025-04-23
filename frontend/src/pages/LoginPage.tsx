import { useEffect } from "react"
import { useNavigate } from "react-router-dom"

export default function LoginPage() {
  const backend = import.meta.env.VITE_API_URL
  const navigate = useNavigate()

  // 이미 로그인한 유저는 바로 survey로 이동
  useEffect(() => {
    const user = sessionStorage.getItem("user") // 또는 localStorage
    if (user) navigate("/survey")
  }, [])

  const handleLogin = (provider: string) => {
    window.location.href = `${backend}/auth/${provider}`
  }

  const handleGuestAccess = () => {
    sessionStorage.removeItem("user") // 혹시라도 기존 로그인 흔적 제거
    navigate("/roomie")
  }

  return (
    <div className="flex flex-col items-center justify-center h-screen bg-gray-50 px-4">
      <h1 className="text-3xl font-black text-zipup-600 mb-8">ZIPUP</h1>
      <p className="text-gray-600 text-sm mb-10 text-center">
        아래 소셜 계정으로 간편하게 시작해보세요!
      </p>

      <div className="space-y-4 w-full max-w-xs">
        <button
          onClick={() => handleLogin("google")}
          className="flex items-center justify-center gap-2 w-full bg-white border border-gray-300 rounded-lg px-4 py-3 text-sm font-medium hover:bg-gray-100 transition"
        >
          <img src="/icons/google.svg" alt="Google" className="w-5 h-5" />
          구글로 시작하기
        </button>

        <button
          onClick={() => handleLogin("kakao")}
          className="flex items-center justify-center gap-2 w-full bg-[#FEE500] rounded-lg px-4 py-3 text-sm font-medium hover:bg-yellow-300 transition"
        >
          <img src="/icons/kakao.svg" alt="Kakao" className="w-5 h-5" />
          카카오로 시작하기
        </button>

        <button
          onClick={() => handleLogin("naver")}
          className="flex items-center justify-center gap-2 w-full bg-[#03C75A] text-white rounded-lg px-4 py-3 text-sm font-medium hover:bg-green-600 transition"
        >
          <img src="/icons/naver.svg" alt="Naver" className="w-5 h-5" />
          네이버로 시작하기
        </button>
      </div>

      {/* 비회원 접근 */}
      <button
        onClick={handleGuestAccess}
        className="mt-6 text-xs text-gray-400 hover:underline transition"
      >
        비회원으로 둘러보기
      </button>
    </div>
  )
}