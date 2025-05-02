import { useLocation, useNavigate } from "react-router-dom";
import { useRef } from "react";
import jsPDF from "jspdf";
import html2canvas from "html2canvas";

// html2canvas 방식으로 PDF 저장
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

  // html2canvas + jsPDF로 PDF 저장
  const handleDownloadPDF = async () => {
    const pdf = new jsPDF({
      orientation: "portrait",
      unit: "px",
      format: [794, 1123],
    });
  
    const pages = ["pdf-cover", "pdf-guide", "pdf-result"];
    for (let i = 0; i < pages.length; i++) {
      const element = document.getElementById(pages[i]);
      if (element) {
        if (i > 0) pdf.addPage();
        const canvas = await html2canvas(element, { scale: 2, useCORS: true });
        const imgData = canvas.toDataURL("image/jpeg", 1.0);
        pdf.addImage(imgData, "JPEG", 0, 0, 794, 1123);
      }
    }
  
    // 저장
    pdf.save("homie_report.pdf");
  };
  

  return (
    <div className="min-h-screen flex flex-col items-center bg-gray-100 py-12 px-4 overflow-x-hidden">
      {/* 상단 제목 */}
      <h1 className="text-2xl font-bold text-blue-600 mb-8">리포트 상세 보기</h1>
  
      {/* PDF 저장 버튼 */}
      <div className="absolute top-6 right-6">
        <button onClick={handleDownloadPDF} className="px-6 py-2 bg-blue-600 text-white rounded shadow hover:bg-blue-700">📄 PDF 다운로드</button>
      </div>
  
      {/* 캡처 대상 */}
      <div ref={reportRef} id="report-page" style={{ width: "794px", margin: "0 auto" }} className="flex flex-col items-center gap-12">
  
        {/* 페이지 1: 표지 */}
        <div className="flex flex-col items-start w-[794px]">
          <span className="text-sm text-gray-500 font-medium mb-1">1 페이지</span>
          <div id="pdf-cover" style={{ width: "794px", height: "1123px", background: "#ffffff", boxShadow: "0 0 8px rgba(0,0,0,0.1)" }}>
            <img src="/icons/report/all_report_view/01_cover.jpg" alt="리포트 커버" style={{ width: "100%", height: "100%", objectFit: "cover", display: "block" }} />
          </div>
        </div>
  
        {/* 페이지 2: 가이드 */}
        <div className="flex flex-col items-start w-[794px] mt-12">
          <span className="text-sm text-gray-500 font-medium mb-1">2 페이지</span>
          <div id="pdf-guide" style={{ width: "794px", height: "1123px", background: "#ffffff", boxShadow: "0 0 8px rgba(0,0,0,0.1)" }}>
            <img src="/icons/report/all_report_view/02_guide.jpg" alt="가이드" style={{ width: "100%", height: "100%", objectFit: "cover", display: "block" }} />
          </div>
        </div>

        {/* 페이지 3: 설문 결과 */}
        <div className="flex flex-col items-start w-[794px] mt-12">
          <span className="text-sm text-gray-500 font-medium mb-1">3 페이지</span>
          <div id="pdf-result" style={{ width: "794px", height: "1123px", background: "#ffffff", boxShadow: "0 0 8px rgba(0,0,0,0.1)" }}>
            <img src="/icons/report/all_report_view/03_result.jpg" alt="가이드" style={{ width: "100%", height: "100%", objectFit: "cover", display: "block" }} />
          </div>
        </div>
  
      </div>
  
      {/* 하단 네비게이션 */}
      <div className="flex gap-4 mt-10">
        <button onClick={() => navigate("/report", { state: { answers } })} className="px-6 py-2 bg-gray-200 text-gray-800 rounded hover:bg-gray-300">🔙 결과 요약으로 돌아가기</button>
      </div>
    </div>
  );
  
    
}
