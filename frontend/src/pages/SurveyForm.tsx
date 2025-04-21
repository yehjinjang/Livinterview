import { useState } from "react"
import { useNavigate } from "react-router-dom"
import { questions } from "../data/questions"
import SurveyRenderer from "../components/SurveyRenderer"
import ProgressBar from "../components/ProgressBar"
import BackButton from "../components/BackButton"

function SurveyForm() {
  // 현재 질문 index (0부터 시작)
  const [index, setIndex] = useState(0)

  // 사용자 응답 저장 객체 (key: 질문 id, value: 선택값)
  const [answers, setAnswers] = useState<Record<string, any>>({})

  // 현재 질문 데이터
  const current = questions[index]

  const navigate = useNavigate()

  // 사용자가 답변을 선택했을 때 호출되는 함수
  const handleAnswer = (value: any) => {
    // 유효하지 않은 값이면 넘어가지 않음
    if (value === null || value === undefined || value === "") {
      alert("답변을 선택해주세요!")
      return
    }

    // 현재 질문 id에 대한 답변 저장
    setAnswers((prev) => ({ ...prev, [current.id]: value }))

    // 다음 질문으로 이동 or 설문 종료
    if (index < questions.length - 1) {
      setIndex((i) => i + 1)
    } else {
      // 결과 페이지로 navigate
      navigate("/report", { state: { answers } })
    }
  }

  // 🔙 이전 질문으로 이동
  const handlePrev = () => {
    if (index > 0) {
      const prevId = questions[index].id
      setAnswers((prev) => {
        const copy = { ...prev }
        delete copy[prevId]
        return copy
      })
      setIndex((i) => i - 1)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-white text-center p-8">
      <div className="w-full max-w-md relative">

        {/* 왼쪽 상단 이전 버튼 */}
        {index > 0 && (
          <div className="mb-4">
            <BackButton onClick={handlePrev} />
          </div>
        )}


        {/* 진행 바 */}
        <div className="mt-6 mb-4">
          <ProgressBar current={index + 1} total={questions.length} />
        </div>

        {/* 질문 텍스트 */}
        <h2 className="text-xl font-bold text-gray-800 mb-4">
          {current.title}
        </h2>

        {/* 아이콘 이미지 (질문 아래에 표시) */}
        {current.icon && (
          <img
            src={current.icon}
            alt="질문 아이콘"
            className="w-[200px] h-auto mx-auto my-6"
          />
        )}

        {/* 질문 유형별 렌더링 (버튼/셀렉트/입력 등) */}
        <div key = {current.id} className="animate-fade-in duration-500">
          <SurveyRenderer question={current} onAnswer={handleAnswer} />
        </div>
      </div>
    </div>
  )
}

export default SurveyForm;