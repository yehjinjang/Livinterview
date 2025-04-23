import { ArrowLeft } from "lucide-react"

type BackButtonProps = {
  onClick: () => void
  className?: string
}

export default function BackButton({ onClick, className = "" }: BackButtonProps) {
  return (
    <button
      onClick={onClick}
      className={`w-9 h-9 flex items-center justify-center rounded-full bg-zipup-600 hover:bg-blue-600 text-white transition ${className}`}
    >
      <ArrowLeft size={18} />
    </button>
  )
}