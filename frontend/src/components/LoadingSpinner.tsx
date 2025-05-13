export default function LoadingSpinner({ text }: { text: string }) {
    return (
      <div className="flex flex-col items-center justify-center h-screen bg-gray-50">
        <div className="animate-spin rounded-full h-12 w-12 border-4 border-gray-300 border-t-zipup-600 mb-4" />
        <p className="text-gray-600 text-lg">{text}</p>
      </div>
    )
  }
  