import { useLocation, useNavigate } from "react-router-dom";
import { useRef } from "react";

// html2pdf.js는 전역 객체로 로드되므로, TS에게 알려줘야 함
declare global {
  interface Window {
    html2pdf: any;
  }
}

export default function ReportView() {
  const location = useLocation();
  const navigate = useNavigate();

  // fallback: 값이 없을 경우를 대비한 기본 mock 데이터
  const answers = (location.state?.answers as Record<string, string>) || {
    "1-subway": "보통이다",
    "2-convenience": "자주 간다",
    "3-police": "어느 정도 가까우면 좋다",
  };

  // 캡처 대상 ref
  const reportRef = useRef<HTMLDivElement>(null);

  // html2pdf 저장
  const handleDownloadPDF = () => {
    if (reportRef.current) {
      window.html2pdf()
        .from(reportRef.current)
        .set({
          margin: 0,
          filename: "homie_report.pdf",
          image: { type: "jpeg", quality: 0.98 },
          html2canvas: { scale: 2 },
          jsPDF: { unit: "mm", format: "a4", orientation: "portrait" },
          pagebreak: {
            mode: ["avoid"],
            avoid: ".pdf-page",
          },
        })
        .save();
    }
  };

  return (
    <div className="relative bg-gray-100 p-6 flex flex-col items-center min-h-screen">
      {/* 상단 제목 */}
      <h1 className="text-2xl font-bold text-blue-600 mb-4">리포트 상세 보기</h1>

      {/* PDF 저장 버튼 */}
      <div className="absolute top-6 right-6">
        <button
          onClick={handleDownloadPDF}
          className="px-6 py-2 bg-blue-600 text-white rounded shadow hover:bg-blue-700"
        >
          📄 PDF 다운로드
        </button>
      </div>

      {/* 캡처 대상 */}
      <div ref={reportRef} className="w-full flex flex-col items-center gap-12 overflow-hidden">
        {/* 페이지 1: 커버 */}
        <div className="pdf-page h-[1123px] w-[794px] bg-[#f9f9fb] relative flex flex-col items-center justify-center overflow-hidden">
          {/* 상단 텍스트 */}
          <div className="text-center mb-8 z-10">
            <p className="text-sm text-gray-500 font-medium tracking-widest">ZIPUP | Report</p>
            <h1 className="text-5xl font-bold text-gray-800 leading-tight">
              삶권분석<br />리포트
            </h1>
          </div>

          {/* 중심 마커 아이콘 */}
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 z-0">
            <span className="text-[240px] text-indigo-500">📍</span>
          </div>

          {/* 아이콘 배치 */}
          <span className="absolute top-[20%] left-[20%] text-4xl">☕</span>
          <span className="absolute top-[30%] right-[18%] text-4xl">🛒</span>
          <span className="absolute bottom-[18%] left-[25%] text-4xl">🎬</span>
          <span className="absolute bottom-[20%] right-[20%] text-4xl">🏥</span>
          <span className="absolute top-[55%] left-[10%] text-4xl">🌳</span>
          <span className="absolute top-[58%] right-[10%] text-4xl">🍽️</span>
          <span className="absolute bottom-[10%] left-[50%] text-4xl rotate-6">📮</span>
          <span className="absolute top-[10%] right-[50%] text-4xl rotate-[-12deg]">💄</span>

          {/* ✅ 안내 문구 위치 수정 */}
          <p className="mt-12 text-sm text-gray-400 z-10">
            당신이 선택한 지역 정보를 기반으로 자동 생성된 리포트입니다.
          </p>
        </div>

        {/* 페이지 2: 제목/생성일 */}
        <div className="pdf-page h-[1123px] w-[794px] overflow-hidden flex flex-col items-center justify-center text-center">
          <h2 className="text-4xl font-bold mb-4">🏠 HOMIE 리포트</h2>
          <p className="text-lg">이 리포트는 입력하신 정보를 기반으로 자동 생성되었습니다.</p>
          <p className="mt-8 text-gray-500 text-sm">생성일: {new Date().toLocaleDateString()}</p>
        </div>

        {/* 페이지 3: 추천 동네 */}
        <div className="pdf-page h-[1123px] w-[794px] overflow-hidden">
          <h2 className="text-2xl font-semibold mb-4 border-b pb-2">📌 추천 동네</h2>
          <ul className="list-disc ml-6 text-lg space-y-2">
            <li>천호동 – 상업시설 밀집 + 교통 편리</li>
            <li>암사동 – 조용한 주거 + 병원 접근성</li>
            <li>성내동 – 생활편의/교육시설 풍부</li>
          </ul>
        </div>

        {/* 페이지 4: 응답 결과 */}
        <div className="pdf-page h-[1123px] w-[794px] overflow-hidden last:mb-0">
          <h2 className="text-2xl font-semibold mb-4 border-b pb-2">📋 세부 응답 결과</h2>
          <div className="grid grid-cols-2 gap-4 max-w-4xl">
            {Object.entries(answers).map(([key, value]) => (
              <div
                key={key}
                className="bg-white border border-gray-200 rounded-xl p-4 shadow-sm"
              >
                <p className="text-sm text-gray-500">{key}</p>
                <p className="text-base font-semibold mt-1">{value}</p>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* 하단 네비게이션 */}
      <div className="flex gap-4 mt-10">
        <button
          onClick={() => navigate("/report", { state: { answers } })}
          className="px-6 py-2 bg-gray-200 text-gray-800 rounded hover:bg-gray-300"
        >
          🔙 결과 요약으로 돌아가기
        </button>
      </div>
    </div>
  );
}
