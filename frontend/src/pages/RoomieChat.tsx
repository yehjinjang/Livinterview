import { useLocation } from "react-router-dom"
import { useEffect, useState, useRef } from "react"

interface ChatMessage {
  type: "text" | "image"
  text?: string
  src?: string
  sender: "user" | "bot"
}

export default function RoomieChat() {
  const location = useLocation()
  const { imageUrl, title } = location.state || {}

  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [input, setInput] = useState<string>("")
  const [loading, setLoading] = useState(false)
  const bottomRef = useRef<HTMLDivElement>(null)

  // 🔵 방 사진 분석
  const analyzeImage = async (url: string) => {
    const res = await fetch(url)
    const blob = await res.blob()
    const formData = new FormData()
    formData.append("image", new File([blob], "room.jpg"))

    const response = await fetch("http://localhost:8000/analyze-image", {
      method: "POST",
      body: formData,
    })

    const data = await response.json()
    return data.description
  }

  // 🔵 초기 메시지 등록
  useEffect(() => {
    const init = async () => {
      if (imageUrl) {
        const description = await analyzeImage(imageUrl)

        setMessages([
          { type: "image", src: imageUrl, sender: "bot" },
          { type: "text", text: "나는 너의 인테리어 도우미 Roomie야!", sender: "bot" },
          { type: "text", text: `이 방은 ${description}이야. 어떤 스타일로 꾸미고 싶어?`, sender: "bot" },
        ])
      }
    }
    init()
  }, [imageUrl])

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages])

  // 🔵 사용자 입력 전송
  const sendMessage = async () => {
    if (!input.trim()) return

    const userMessage = input.trim()

    setMessages(prev => [...prev, { type: "text", text: userMessage, sender: "user" }])
    setInput("")
    setLoading(true)

    try {
      const formattedMessages = messages.map(m => {
        if (m.type === "image") {
          return {
            role: "assistant",
            content: `방 사진이 있어: ${m.src}`,
          }
        } else {
          return {
            role: m.sender === "user" ? "user" : "assistant",
            content: m.text || "",
          }
        }
      })

      formattedMessages.push({ role: "user", content: userMessage })

      const response = await fetch("http://localhost:8000/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ messages: formattedMessages }),
      })

      const data = await response.json()
      setMessages(prev => [...prev, { type: "text", text: data.reply, sender: "bot" }])
    } catch (error) {
      console.error("❌ 서버 통신 오류:", error)
      setMessages(prev => [...prev, { type: "text", text: "서버와 연결할 수 없습니다.", sender: "bot" }])
    } finally {
      setLoading(false)
    }
  }

  // 🔵 대화 요약 + ControlNet 프롬프트 요청 + 인테리어 이미지 생성
  const summarizeAndGenerateImage = async () => {
    if (loading) return
    setLoading(true)

    try {
      setMessages(prev => [...prev, { type: "text", text: "인테리어 이미지를 생성하고 있어! 잠깐만 기다려줘 🔥", sender: "bot" }])

      const conversation = messages
        .filter(m => m.type === "text")
        .map(m => `${m.sender === "user" ? "사용자" : "Roomie"}: ${m.text}`)
        .join("\n")

      // 1. 대화 요약
      const summaryRes = await fetch("http://localhost:8000/analyze/summary", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ conversation }),
      })
      const summaryData = await summaryRes.json()

      // 2. 프롬프트 생성
      const promptRes = await fetch("http://localhost:8000/analyze/controlnet", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ summary: summaryData.result }),
      })
      const promptData = await promptRes.json()

      const prompt = promptData.result

      // 3. 인테리어 이미지 생성
      const generatedImageUrl = await generateFakeImage(prompt)

      setMessages(prev => [
        ...prev,
        { type: "text", text: `요약 완료!\n\n${summaryData.result}`, sender: "bot" },
        { type: "text", text: "이 스타일로 꾸며봤어!", sender: "bot" },
        { type: "image", src: generatedImageUrl, sender: "bot" },
      ])
    } catch (error) {
      console.error("❌ 요약/생성 실패:", error)
      setMessages(prev => [...prev, { type: "text", text: "이미지 생성에 실패했어. 다시 시도해줘!", sender: "bot" }])
    } finally {
      setLoading(false)
    }
  }

  // 🔵 (임시) 이미지 생성 API
  const generateFakeImage = async (prompt: string) => {
    console.log("🖼️ 생성 프롬프트:", prompt)

    try {
      const response = await fetch("http://localhost:8000/generate-image", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt }),
      })

      const data = await response.json()
      return data.image_url
    } catch (error) {
      console.error("❌ 이미지 생성 실패:", error)
      return "/icons/images.jpg"
    }
  }

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      {/* 메시지 영역 */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={`flex ${msg.sender === "user" ? "justify-end" : "justify-start"}`}
          >
            {msg.type === "image" ? (
              <img
                src={msg.src}
                alt="매물 이미지"
                className="rounded-lg shadow w-64 h-40 object-cover"
              />
            ) : (
              <div
                className={`p-3 rounded-2xl max-w-[70%] text-sm ${
                  msg.sender === "user"
                    ? "bg-blue-500 text-white"
                    : "bg-white text-gray-800 border"
                }`}
              >
                {msg.text}
              </div>
            )}
          </div>
        ))}
        <div ref={bottomRef} />
      </div>

      {/* 입력창 + 인테리어 생성 버튼 */}
      <div className="p-3 bg-white border-t flex gap-2">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => { if (e.key === "Enter") sendMessage() }}
          placeholder="메시지를 입력하세요"
          className="border rounded-full px-4 py-2 flex-1 text-sm"
          disabled={loading}
        />
        <button
          onClick={sendMessage}
          className="bg-zipup-600 hover:bg-blue-700 text-white px-4 py-2 rounded-full text-sm"
          disabled={loading}
        >
          {loading ? "..." : "전송"}
        </button>
        <button
          onClick={summarizeAndGenerateImage}
          className="bg-gray-300 hover:bg-gray-400 text-gray-800 px-3 py-2 rounded-full text-sm"
          disabled={loading}
        >
          {loading ? "생성 중..." : "인테리어 생성"}
        </button>
      </div>
    </div>
  )
}