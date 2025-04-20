import { Home, Image, Settings } from "lucide-react"

export default function BottomTabBar() {
  return (
    <footer className="w-full bg-white border-t border-gray-200 py-3 flex justify-around items-center shadow-inner">
      <div className="flex flex-col items-center text-zipup-600">
        <Home size={24} />
        <span className="text-xs font-semibold mt-1">Homie</span>
      </div>
      <div className="flex flex-col items-center text-gray-500 hover:text-zipup-600 transition">
        <Image size={24} />
        <span className="text-xs mt-1">Roomie</span>
      </div>
      <div className="flex flex-col items-center text-gray-500 hover:text-zipup-600 transition">
        <Settings size={24} />
        <span className="text-xs mt-1">Setting</span>
      </div>
    </footer>
  )
}
