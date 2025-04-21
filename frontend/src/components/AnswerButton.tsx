export default function AnswerButton({ text, onClick }: { text: string; onClick: () => void }) {
    return (
      <button
        onClick={onClick}
        className="w-full bg-blue-600 text-white rounded-xl py-4 hover:bg-blue-700 transition"
      >
        {text}
      </button>
    )
  }