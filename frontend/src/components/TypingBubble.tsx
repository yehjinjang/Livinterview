export default function TypingBubble({ text }: { text: string }) {
    return (
      <div className="flex justify-start">
        <div className="p-3 rounded-2xl max-w-[70%] text-sm bg-white text-gray-800 border">
          {text}
        </div>
      </div>
    )
  }
  