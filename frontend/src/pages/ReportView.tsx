import { useLocation, useNavigate } from "react-router-dom";
import { useRef, useEffect } from "react";
import jsPDF from "jspdf";
import html2canvas from "html2canvas";

// 분리된 페이지
import ReportViewCover  from "./ReportViewCover";
import ReportViewGuide  from "./ReportViewGuide";
import ReportViewResult from "./ReportViewResult";
import ReportViewInfo_1 from "./ReportViewInfo_1";

export default function ReportView() {
  const location  = useLocation();
  const navigate  = useNavigate();

  // 🔐 사용자 정보 세션에서 가져오기
  const storedUser = sessionStorage.getItem("user");
  const parsedUser = storedUser ? JSON.parse(storedUser) : null;
  const userName = parsedUser?.name || "이름 없음";

  // 📋 설문 결과 및 분석 결과 기본값
  const answers = (location.state?.answers as Record<string, string>) || {
    "1-subway": "보통이다",
    "2-convenience": "자주 간다",
    "3-police": "어느 정도 가까우면 좋다",
  };

  const topIndicators = location.state?.topIndicators || ["생활", "안전", "교통"];
  const scores = location.state?.scores || {
      교통: 60,
      편의: 60,
      안전: 70,
      건강: 20,
      녹지: 45,
      생활: 70,
      놀이: 25,
      운동: 50,
    };

  const dongName = location.state?.dongName || "구의동"; // 추천 동
  const guName = location.state?.guName || "광진구"; 
  const fullLocation = `서울특별시 ${guName} ${dongName}`;

  const reportRef = useRef<HTMLDivElement>(null);

   // 페이지 진입 시 자동 지도 생성 API 호출
   useEffect(() => {
    console.log("📦 fullLocation →", fullLocation);
  
    const generateMap = async () => {
      try {
        const res = await fetch("http://localhost:8000/generate-map", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ full_location: fullLocation }),
        });
  
        if (!res.ok) {
          const error = await res.json();
          console.error("❌ 지도 생성 실패:", error);
          return;
        }
  
        console.log("✅ 지도 이미지 생성 완료");
      } catch (error) {
        console.error("❌ 네트워크 오류:", error);
      }
    };
  
    generateMap();
  }, [fullLocation]);



  /* ★ PDF 다운로드 – 페이지별 캡처 방식 */
  const handleDownloadPDF = async () => {
    const pdf   = new jsPDF({ orientation: "portrait", unit: "px", format: [794, 1123] });
    const pages = ["pdf-cover", "pdf-guide", "pdf-result","pdf-info_1"];

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

      pdf.addImage(canvas.toDataURL("image/jpeg", 1.0), "JPEG", 0, 0, 794, 1123);
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
        <ReportViewResult
          userName={userName}
          topIndicators={topIndicators}
          scores={scores}
        />
        <ReportViewInfo_1
          dongName={dongName}
          fullLocation = {fullLocation}
          userName={userName}
          topIndicators={topIndicators}
        />
      </div>

      {/* 결과로 돌아가기 */}
      <button
        onClick={() => navigate("/report", { state: { answers } })}
        className="mt-8 px-6 py-2 bg-gray-200 rounded hover:bg-gray-300"
      >
        🔙 결과 요약으로 돌아가기
      </button>
    </div>
  );
}
