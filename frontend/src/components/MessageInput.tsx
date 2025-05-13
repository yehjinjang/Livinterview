export default function MessageInput({
    input,
    setInput,
    isSending,
    isGenerating,
    sendMessage,
    summarizeAndGenerateImage,
  }: {
    input: string
    setInput: (value: string) => void
    isSending: boolean
    isGenerating: boolean
    sendMessage: () => void
    summarizeAndGenerateImage: () => void
  }) {
    return (
      <div className="p-3 bg-white border-t flex gap-2">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => { if (e.key === "Enter") sendMessage() }}
          placeholder="메시지를 입력하세요"
          className="border rounded-full px-4 py-2 flex-1 text-sm"
          disabled={isSending || isGenerating}
        />
        <button
          onClick={sendMessage}
          className="bg-zipup-600 hover:bg-blue-700 text-white px-4 py-2 rounded-full text-sm"
          disabled={isSending || isGenerating}
        >
          {isSending ? "..." : "전송"}
        </button>
        <button
          onClick={summarizeAndGenerateImage}
          className="bg-gray-300 hover:bg-gray-400 text-gray-800 px-3 py-2 rounded-full text-sm"
          disabled={isGenerating}
        >
          {isGenerating ? "요약 중..." : "인테리어 생성"}
        </button>
      </div>
    )
  }  