export default function ReportViewCover() {
  return (
    <div
      id="pdf-cover"
      style={{
        width: "794px",
        height: "1123px",
        position: "relative",          
        backgroundColor: "white",      
        boxShadow: "0 0 8px rgba(0,0,0,0.1)",
        boxSizing: "border-box",
        overflow: "hidden",            
      }}
    >
      <img
        src="/icons/report/all_report_view/01_cover.jpg"
        alt="리포트 커버"
        style={{
          width: "100%",
          height: "100%",
          objectFit: "cover",
          display: "block",
        }}
      />
    </div>
  );
}