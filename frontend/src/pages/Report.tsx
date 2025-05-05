import { useLocation, useNavigate } from "react-router-dom";

export default function Report() {
  const location = useLocation();
  const answers = location.state?.answers
  const navigate = useNavigate();

  return (
    <div className="min-h-screen flex flex-col items-center justify-center p-6 space-y-6">
      <h1 className="text-2xl font-bold text-blue-600">리포트 결과</h1>

      <pre className="bg-gray-100 p-4 rounded w-full max-w-md text-left overflow-x-auto">
        {JSON.stringify(answers, null, 2)}
      </pre>

      <div className="flex gap-4">
        <button
          onClick={() => navigate("/roomie")}
          className="px-4 py-2 bg-zipup-600 text-white rounded-lg shadow hover:bg-blue-700 transition"
        >
          매물 확인하기
        </button>

        {/* answers를 state로 명확히 넘김 */}
        <button
          onClick={() => navigate("/report/view", { state: { answers } })}
          className="px-4 py-2 bg-gray-100 text-blue-600 border border-blue-400 rounded-lg hover:bg-blue-100 transition"
        >
          📝 리포트 보기
        </button>
      </div>
    </div>
  );
}
