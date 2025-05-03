import { useLocation, useNavigate } from "react-router-dom"
import { useEffect, useState, useRef } from "react"
import ChatMessageList from "../components/ChatMessageList"
import MessageInput from "../components/MessageInput"
import TypingBubble from "../components/TypingBubble"
import LoadingSpinner from "../components/LoadingSpinner"

interface ChatMessage {
  type: "text" | "image"
  text?: string
  src?: string
  sender: "user" | "bot"
}

export default function RoomieChat() {
  const location = useLocation()
  const navigate = useNavigate()
  const { imageUrl, title } = location.state || {}

  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [input, setInput] = useState<string>("")
  const [typingText, setTypingText] = useState<string>("")
  const [isSending, setIsSending] = useState(false)
  const [isGenerating, setIsGenerating] = useState(false)
  const [isAnalyzing, setIsAnalyzing] = useState(true)
  const bottomRef = useRef<HTMLDivElement>(null)

  const analyzeImage = async (url: string) => {
    try {
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
    } catch {
      return "방 사진 분석 실패"
    }
  }

  useEffect(() => {
    const init = async () => {
      if (imageUrl) {
        const description = await analyzeImage(imageUrl)
        setMessages([
          { type: "image", src: imageUrl, sender: "bot" },
          { type: "text", text: "나는 너의 인테리어 도우미 Roomie야!", sender: "bot" },
          { type: "text", text: `이 방은 ${description} 어떤 스타일로 꾸미고 싶어?`, sender: "bot" },
        ])
        setIsAnalyzing(false)
      }
    }
    init()
  }, [imageUrl])

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages, typingText])

  const sendMessage = async () => {
    if (!input.trim() || isSending || isGenerating) return

    const userMessage = input.trim()
    setMessages(prev => [...prev, { type: "text", text: userMessage, sender: "user" }])
    setInput("")
    setIsSending(true)

    try {
      const formattedMessages = messages.map(m =>
        m.type === "image"
          ? { role: "assistant", content: `방 사진이 있어: ${m.src}` }
          : { role: m.sender === "user" ? "user" : "assistant", content: m.text || "" }
      )
      formattedMessages.push({ role: "user", content: userMessage })

      const response = await fetch("http://localhost:8000/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ messages: formattedMessages }),
      })

      const data = await response.json()
      typeWriterEffect(data.reply)
    } catch {
      setMessages(prev => [...prev, { type: "text", text: "서버 오류", sender: "bot" }])
      setIsSending(false)
    }
  }

  const typeWriterEffect = (fullText: string) => {
    setTypingText("")
    let index = 0
    const typing = () => {
      if (index < fullText.length) {
        setTypingText(prev => prev + fullText[index])
        index++
        setTimeout(typing, 30)
      } else {
        setMessages(prev => [...prev, { type: "text", text: fullText, sender: "bot" }])
        setTypingText("")
        setIsSending(false)
      }
    }
    typing()
  }

  const summarizeAndGenerateImage = async () => {
    if (isSending || isGenerating) return
    setIsGenerating(true)

    try {
      setMessages(prev => [...prev, { type: "text", text: "인테리어 생성 중...🔥", sender: "bot" }])

      const conversation = messages.filter(m => m.type === "text")
        .map(m => `${m.sender === "user" ? "사용자" : "Roomie"}: ${m.text}`)
        .join("\n")

      const summaryRes = await fetch("http://localhost:8000/analyze/summary", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ conversation }),
      })
      const summaryData = await summaryRes.json()

      const promptRes = await fetch("http://localhost:8000/analyze/controlnet", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ summary: summaryData.result }),
      })
      const promptData = await promptRes.json()

      const generatedImageUrl = await generateImage(promptData.result)

      navigate("/roomie/result", {
        state: { originalImage: imageUrl, generatedImage: generatedImageUrl, title }
      })
    } catch {
      setMessages(prev => [...prev, { type: "text", text: "이미지 생성 실패", sender: "bot" }])
    } finally {
      setIsGenerating(false)
    }
  }

  const generateImage = async (prompt: string) => {
    try {
      const res = await fetch("http://localhost:8000/generate-image", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt }),
      })
      const data = await res.json()
      return data.image_url
    } catch {
      return "/icons/images.jpg"
    }
  }

  if (isAnalyzing) {
    return <LoadingSpinner text="방 분석 중...잠시만 기다려주세요!" />
  }

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        <ChatMessageList messages={messages} />
        {typingText && <TypingBubble text={typingText} />}
        <div ref={bottomRef} />
      </div>

      <MessageInput
        input={input}
        setInput={setInput}
        isSending={isSending || typingText.length > 0}
        isGenerating={isGenerating}
        sendMessage={sendMessage}
        summarizeAndGenerateImage={summarizeAndGenerateImage}
      />
    </div>
  )
}
