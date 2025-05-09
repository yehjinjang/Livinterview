import { useLocation, useNavigate } from "react-router-dom";
import { useRef } from "react";
import jsPDF from "jspdf";
import html2canvas from "html2canvas";

// 분리된 페이지
import ReportViewCover  from "./ReportViewCover";
import ReportViewGuide  from "./ReportViewGuide";
import ReportViewResult from "./ReportViewResult";

export default function ReportView() {
  const location  = useLocation();
  const navigate  = useNavigate();
  const answers   = (location.state?.answers as Record<string, string>) || {
    "1-subway": "보통이다",
    "2-convenience": "자주 간다",
    "3-police": "어느 정도 가까우면 좋다",
  };

  const reportRef = useRef<HTMLDivElement>(null);

  /* ★ PDF 다운로드 – 페이지별 캡처 방식 */
  const handleDownloadPDF = async () => {
    const pdf   = new jsPDF({ orientation: "portrait", unit: "px", format: [794, 1123] });
    const pages = ["pdf-cover", "pdf-guide", "pdf-result"];

    for (let i = 0; i < pages.length; i++) {
      const el = document.getElementById(pages[i]);
      if (!el) continue;
      if (i > 0) pdf.addPage();

      await document.fonts.ready;              /* ★ 폰트 로딩 대기 */
      await new Promise((res) => setTimeout(res, 100));
      const canvas = await html2canvas(el, {   /* ★ scale 3 로 고해상도 캡처 */
        scale: 3,
        useCORS: true,
        backgroundColor: null,
      });

      pdf.addImage(
        canvas.toDataURL("image/jpeg", 1.0),
        "JPEG",
        0,
        0,
        794,
        1123
      );
    }
    pdf.save("homie_report.pdf");
  };

  return (
    <div className="min-h-screen flex flex-col items-center bg-gray-100 py-12 px-4">
      {/* 상단 타이틀 & 버튼 */}
      <h1 className="text-2xl font-bold text-blue-600 mb-4">리포트 상세 보기</h1>
      <button
        onClick={handleDownloadPDF}
        className="self-end mb-6 px-6 py-2 bg-blue-600 text-white rounded shadow hover:bg-blue-700"
      >
        📄 PDF 다운로드
      </button>

      {/* ★ 각 페이지를 794×1123 로 고정 – absolute 레이아웃 그대로 */}
      <div ref={reportRef} id="report-page" className="flex flex-col gap-0">
        <ReportViewCover />
        <ReportViewGuide />
        <ReportViewResult />
      </div>

      {/* 하단 네비 */}
      <button
        onClick={() => navigate("/report", { state: { answers } })}
        className="mt-8 px-6 py-2 bg-gray-200 rounded hover:bg-gray-300"
      >
        🔙 결과 요약으로 돌아가기
      </button>
    </div>
  );
}
