import { useState, useEffect } from "react"
import { Question } from "../types/question"


export default function SurveyRenderer({
  question,
  onAnswer,
}: {
  question: Question
  onAnswer: (v: any) => void
}) {
  // 선택 상태 저장 (radio, select, input에 따라 다르게 사용됨)
  const [selected, setSelected] = useState<string | number | null>(null)

  // 질문이 바뀔 때 selected 초기화
  useEffect(() => 
    setSelected(null))

  // 공통 선택 처리 함수
  const handleSelect = (value: string | number) => {
    setSelected(value)
    onAnswer(value)
  }

  // 질문 타입에 따라 렌더링
  switch (question.type) {
    case "radio":
      return (
        <div className="flex flex-col gap-3">
          {question.options?.map((opt) => (
            <button
              key={opt}
              onClick={() => handleSelect(opt)}
              className={`w-full py-4 rounded-xl font-semibold transition ${
                selected === opt
                  ? "bg-blue-600 text-white"
                  : "bg-gray-100 text-gray-700 hover:bg-gray-200"
              }`}
            >
              {opt}
            </button>
          ))}
        </div>
      )

    case "select":
      return (
        <select
          value={selected?.toString() || ""}
          onChange={(e) => handleSelect(e.target.value)}
          className="w-full border border-gray-300 rounded p-3 text-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-400"
        >
          <option value="">선택해주세요</option>
          {question.options?.map((opt) => (
            <option key={opt} value={opt}>
              {opt}
            </option>
          ))}
        </select>
      )

    case "input":
      return (
        <input
          type="number"
          value={selected?.toString() || ""}
          onChange={(e) => handleSelect(Number(e.target.value))}
          className="w-full border border-gray-300 rounded p-3 text-gray-800 focus:outline-none focus:ring-2 focus:ring-blue-400"
          placeholder={question.unit ? `숫자 입력 (${question.unit})` : "숫자 입력"}
        />
      )
      case "range":
        const [tempValue, setTempValue] = useState<number | null>(null)
      
        return (
          <div className="flex flex-col gap-3">
            {/* 입력과 버튼을 전체적으로 왼쪽, 위로  */}
            <div className="flex items-center gap-2 ml-3 mt-">
              <input
                type="number"
                placeholder="예: 6"
                className="flex-1 border p-2 rounded"
                value={tempValue ?? ""}
                onChange={(e) => setTempValue(Number(e.target.value))}
              />
              <button
                onClick={() =>
                  onAnswer({ [question.rangeIds?.[0] ?? "min"]: tempValue })
                }
                className="ml-1 px-3 py-2 bg-zipup-600 text-white rounded-2xl hover:bg-blue-700 transition"
                disabled={tempValue === null}
              >
                입력 완료
              </button>
            </div>
      
            {/* 건너뛰기 버튼 */}
            <div className="flex justify-end mr-2">
              <button
                onClick={() =>
                  onAnswer({ [question.rangeIds?.[0] ?? "min"]: null })
                }
                className="text-sm text-gray-500 hover:underline"
              >
                건너뛰기
              </button>
            </div>
          </div>
        )      


    default:
      return (
        <p className="text-sm text-red-500 mt-4">
          ⚠️ 지원되지 않는 질문 타입입니다.
        </p>
      )
  }
}