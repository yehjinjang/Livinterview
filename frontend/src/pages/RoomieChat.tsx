import { useLocation } from "react-router-dom"
import { useEffect, useState } from "react"

export default function RoomieChat() {
  const location = useLocation()
  const { imageUrl, title } = location.state || {}

  const [messages, setMessages] = useState<any[]>([])
  const [input, setInput] = useState<string>("")
  const [loading, setLoading] = useState(false)

  // 첫 매물 이미지, 안내 메시지 등록
  useEffect(() => {
    if (imageUrl) {
        
      setMessages([
        { type: "image", src: imageUrl },
        { type: "text", text: `이 방은 "${title}"이야. 어떤 스타일로 꾸미고 싶어?` },
      ])
    }
  }, [imageUrl, title])

  // 사용자 입력 보내는 함수
  const sendMessage = async () => {
    if (!input.trim()) return

    const userMessage = input.trim()

    // 사용자 입력 추가
    setMessages(prev => [...prev, { type: "text", text: userMessage }])
    setInput("")
    setLoading(true)

    try {
      // FastAPI 서버로 POST 요청
      const response = await fetch("http://localhost:8000/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ message: userMessage }),
      })

      const data = await response.json()

      // 서버 응답(챗봇 답변) 추가
      setMessages(prev => [...prev, { type: "text", text: data.reply }])
    } catch (error) {
      console.error("❌ 서버 통신 오류:", error)
      setMessages(prev => [...prev, { type: "text", text: "서버와 연결할 수 없습니다. 다시 시도해 주세요." }])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex flex-col p-4 space-y-4">
      {/* 메시지 리스트 */}
      {messages.map((msg, idx) =>
        msg.type === "image" ? (
          <img
            key={idx}
            src={msg.src}
            alt="매물 이미지"
            className="w-full rounded-lg shadow"
          />
        ) : (
          <div
            key={idx}
            className="p-3 rounded-lg bg-blue-100 text-gray-700 max-w-[70%]"
          >
            {msg.text}
          </div>
        )
      )}

      {/* 입력창 */}
      <div className="flex gap-2 mt-4">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => { if (e.key === "Enter") sendMessage() }}
          className="border rounded-lg p-2 flex-1"
          placeholder="메시지를 입력하세요"
          disabled={loading}
        />
        <button
          onClick={sendMessage}
          className="bg-zipup-600 text-white px-4 py-2 rounded-lg"
          disabled={loading}
        >
          {loading ? "..." : "전송"}
        </button>
      </div>
    </div>
  )
}
