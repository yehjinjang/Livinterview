import { useNavigate } from "react-router-dom"
import BottomTabBar from "../components/BottomTabBar"

export default function HomePage() {
  const navigate = useNavigate()

  return (
    <div className="min-h-screen flex flex-col justify-between bg-white font-sans text-gray-800">
      <div className="min-h-screen flex flex-col items-center justify-center px-6 text-center pb-24">
        <h1 className="text-[40px] font-black text-zipup-600 mb-3 tracking-wide">
          ZIPUP
        </h1>

        <h2 className="text-xl font-bold text-zipup-600 mb-1">
          &lt;삶권분석&gt; <br />
          리포트 설문지
        </h2>
        <p className="text-sm text-gray-600 leading-relaxed mb-6">
          취향을 알려주시면 <br />
          알맞은 동네로 안내해드릴게요!
        </p>

        <img
          src="/icons/entericon.svg"
          alt="대표"
          className="w-[240px] h-auto my-6"
        />

        <button
            onClick={() => navigate("/login")}
            className="w-full max-w-xs bg-blue-600 text-white text-xl font-bold py-6 px-10 rounded-full shadow-lg hover:bg-blue-700 transition-all border-none mt-10"
            >
            시작하기 →
        </button>
      </div>

      <BottomTabBar />
    </div>
  )
}
