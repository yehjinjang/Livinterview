import { Home, Image, Settings } from "lucide-react"
import { Link, useLocation } from "react-router-dom"

export default function BottomTabBar() {
  const location = useLocation()
  const currentPath = location.pathname

  return (
    <footer className="w-full bg-white border-t border-gray-200 py-3 flex justify-around items-center shadow-inner">
      <Link to="/">
        <div className={`flex flex-col items-center transition ${currentPath === "/" ? "text-zipup-600 font-semibold" : "text-gray-500 hover:text-zipup-600"}`}>
          <Home size={24} />
          <span className="text-xs mt-1">Homie</span>
        </div>
      </Link>

      <Link to="/roomie">
        <div className={`flex flex-col items-center transition ${currentPath === "/roomie" ? "text-zipup-600 font-semibold" : "text-gray-500 hover:text-zipup-600"}`}>
          <Image size={24} />
          <span className="text-xs mt-1">Roomie</span>
        </div>
      </Link>

      <Link to="/settings">
        <div className={`flex flex-col items-center transition ${currentPath === "/settings" ? "text-zipup-600 font-semibold" : "text-gray-500 hover:text-zipup-600"}`}>
          <Settings size={24} />
          <span className="text-xs mt-1">Setting</span>
        </div>
      </Link>
    </footer>
  )
}