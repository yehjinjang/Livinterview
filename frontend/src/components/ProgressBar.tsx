export default function ProgressBar({ current, total }: { current: number; total: number }) {
    const percent = (current / total) * 100
    return (
      <div className="w-full bg-gray-200 h-5 rounded-full mb-4">
        <div
          className="bg-zipup-600 h-5 rounded-full transition-all"
          style={{ width: `${percent}%` }}
        ></div>
      </div>
    )
  }