export default function ReportViewCover() {
  return (
    <div className="flex flex-col items-start w-[794px]">
      <span className="text-sm text-gray-500 font-medium mb-1">1 페이지</span>
      <div
        id="pdf-cover"
        style={{
          width: "794px",
          height: "1123px",
          background: "#ffffff",
          boxShadow: "0 0 8px rgba(0,0,0,0.1)",
        }}
      >
        <img
          src="/icons/report/all_report_view/01_cover.jpg"
          alt="리포트 커버"
          style={{ width: "100%", height: "100%", objectFit: "cover", display: "block" }}
        />
      </div>
    </div>
  );
}
