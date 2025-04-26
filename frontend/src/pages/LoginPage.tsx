import { useEffect } from "react"
import { useNavigate } from "react-router-dom"

export default function LoginPage() {
  const backend = import.meta.env.VITE_API_URL
  const navigate = useNavigate()

  useEffect(() => {
    fetch(`${backend}/me`, {
      credentials: "include",
    })
      .then((res) => {
        if (!res.ok) throw new Error("Not logged in")
        return res.json()
      })
      .then((data) => {
        console.log("로그인 상태 감지:", data)
        sessionStorage.setItem("user", JSON.stringify(data)) // 저장해두기
        navigate("/roomie") // 바로 이동
      })
      .catch(() => {
        sessionStorage.removeItem("user") // 로그인 안 되어 있으면 유지
      })
  }, [])

  const handleLogin = (provider: string) => {
    window.location.href = `${backend}/auth/${provider}`
  }


  return (
    <div className="flex flex-col items-center justify-center h-screen bg-gray-50 px-4">
      {/* 로고 영역 */}
      <div className="flex items-center gap-2 mb-8 animate-bounceLogo">
        <img
          src="/icons/main.png"
          alt="ZIPUP 로고"
          className="w-[50px] h-[50px]"
        />
        <span className="text-3xl font-black text-zipup-600">ZIPUP</span>
      </div>

      <p className="text-gray-600 text-sm mb-10 text-center">
        함께 집업과의 여정을 떠나봐요!
      </p>

      {/* 소셜 로그인 버튼 */}
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

      {/* 비회원으로 이용 */}
      {/* <button
        onClick={handleGuestAccess}
        className="mt-6 text-xs text-gray-400 hover:underline transition"
      >
        비회원으로 둘러보기
      </button> */}
    </div>
  )
}