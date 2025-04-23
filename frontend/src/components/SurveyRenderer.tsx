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
        const [isInvalid, setIsInvalid] = useState(false)
      
        return (
          <div className="flex flex-col gap-3">
            <div className="flex pl-2 items-center gap-2 ml-3">
              <input
                type="text"
                placeholder="예: 6 (숫자만 입력 가능해요)"
                className={`flex-1 border p-2 p1-5 rounded transition-all duration-300 ${
                  isInvalid ? "border-red-500 animate-shake" : "border-gray-300"
                }`}
                value={tempValue ?? ""}
                onChange={(e) => {
                  const value = e.target.value
      
                  if (value === "") {
                    setTempValue(null)
                    setIsInvalid(false)
                    return
                  }
      
                  if (!/^\d+$/.test(value)) {
                    setIsInvalid(true)
                    setTimeout(() => setIsInvalid(false), 300) // 애니메이션 초기화
                    return
                  }
      
                  setTempValue(Number(value))
                  setIsInvalid(false)
                }}
              />
      
              <button
                onClick={() => {
                  if (tempValue === null || isNaN(tempValue)) {
                    setIsInvalid(true)
                    setTimeout(() => setIsInvalid(false), 300)
                    return
                  }
      
                  onAnswer({ [question.rangeIds?.[0] ?? "min"]: tempValue })
                }}
                className="ml-1 px-3 py-2 bg-zipup-600 text-white rounded-2xl hover:bg-blue-700 transition"
              >
                입력 완료
              </button>
            </div>
      
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

        case "autocomplete":
          const [inputValue, setInputValue] = useState("")
          const [selectedOption, setSelectedOption] = useState<string | null>(null)
        
          const filteredOptions = question.options?.filter((opt) =>
            opt.toLowerCase().includes(inputValue.toLowerCase())
          )
        
          return (
            <div className="flex flex-col gap-2 text-left">
              <input
                type="text"
                value={inputValue}
                onChange={(e) => {
                  setInputValue(e.target.value)
                  setSelectedOption(null) // 입력이 바뀌면 선택 초기화
                }}
                placeholder="지하철역 이름을 입력하세요"
                className="w-full border border-gray-300 rounded p-3 text-gray-800 focus:outline-none focus:ring-2 focus:ring-blue-400"
              />
        
              {inputValue.length > 0 && (
                <ul className="border rounded shadow bg-white max-h-48 overflow-y-auto">
                  {filteredOptions?.map((opt) => (
                    <li
                      key={opt}
                      onClick={() => {
                        if (selectedOption === opt) {
                          onAnswer(opt) // 두 번 클릭 시 확정
                        } else {
                          setSelectedOption(opt)
                          setInputValue(opt) // 선택된 항목 input에 채우기
                        }
                      }}
                      className={`px-4 py-2 cursor-pointer ${
                        selectedOption === opt ? "bg-blue-100" : "hover:bg-gray-100"
                      }`}
                    >
                      {opt}
                    </li>
                  ))}
                  {filteredOptions?.length === 0 && (
                    <li className="px-4 py-2 text-gray-400">일치하는 항목이 없습니다</li>
                  )}
                </ul>
              )}
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