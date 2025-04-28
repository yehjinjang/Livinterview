interface ChatMessage {
    type: "text" | "image"
    text?: string
    src?: string
    sender: "user" | "bot"
  }
  
  export default function ChatMessageList({ messages }: { messages: ChatMessage[] }) {
    return (
      <>
        {messages.map((msg, idx) => (
          <div key={idx} className={`flex ${msg.sender === "user" ? "justify-end" : "justify-start"}`}>
            {msg.type === "image" ? (
              <img src={msg.src} alt="매물" className="rounded-lg shadow w-64 h-40 object-cover" />
            ) : (
              <div className={`p-3 rounded-2xl max-w-[70%] text-sm ${
                msg.sender === "user" ? "bg-blue-500 text-white" : "bg-white text-gray-800 border"
              }`}>
                {msg.text}
              </div>
            )}
          </div>
        ))}
      </>
    )
  }
  