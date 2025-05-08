export default function ReportViewResult() {
  return (
    <div className="flex flex-col items-start w-[794px] mt-12">
      <span className="text-sm text-gray-500 font-medium mb-1">3 페이지</span>
      <div
        id="pdf-result"
        style={{
          width: "794px",
          height: "1123px",
          background: "#ffffff",
          boxShadow: "0 0 8px rgba(0,0,0,0.1)",
        }}
      >
        <img
          src="/icons/report/all_report_view/03_result.jpg"
          alt="결과"
          style={{ width: "100%", height: "100%", objectFit: "cover", display: "block" }}
        />
      </div>
    </div>
  );
}
