type ReportViewInfoProps = {
  dongName: string;
  fullLocation: string;
  userName: string;
  topIndicators: string[];
};

export default function ReportViewInfo_1({ dongName, fullLocation, userName, topIndicators }: ReportViewInfoProps) {
  
  const indicatorText = topIndicators.map((item) => `${item}지표`).join(", ");

  // 📌 더미 데이터
  const dongFeatures = ["생활지표", "안전지표", "교통지표"];

  const descriptionTexts: string[] = [
    "역촌동은 지하철 6호선이 지나가는 응암역, 구산역, 역촌역 근처에 있는 동네로, 서울 북서부에 위치한 동네입니다.",
    "역촌동에서 조금만 남쪽으로 내려오면 응암역 근처부터 불광천이 시작됩니다. 이 불광천에서 봄에는 벚꽃이, 겨울에는 축제가 많이 펼쳐집니다.",
    "동네에는 크고 작은 다세대주택이 많아 거주성과 젊은 사람들이 매우 많은 동네고, 다양한 카페뿐만 아니라 생활과 관련된 식당이 잘 되어 있습니다.",
    "현재 역촌동 내 약 24개의 오피스텔이 있습니다.",
  ];

  return (
    <div className="flex flex-col items-start w-[794px] mt-12">
      <span className="text-sm text-gray-500 font-medium mb-1">4 페이지</span>

      <div
        id="pdf-info_1"
        style={{
          width: "794px",
          height: "1123px",
          backgroundImage: "url('/icons/report/all_report_view/04_informaion_1.jpg')",
          backgroundSize: "100% 100%",
          backgroundPosition: "top left",
          boxShadow: "0 0 8px rgba(0,0,0,0.1)",
          padding: "80px 60px",
          boxSizing: "border-box",
          position: "relative",
          fontFamily: "Pretendard-Regular",
        }}
      >
        {/* 사용자 이름 */}
        <div
          style={{
            position: "absolute",
            top: "210px",
            left: "55px",
            fontSize: "18px",
            fontWeight: "bold",
          }}
        >
          <span>{userName}</span>
        </div>

        {/* 지도 이미지 삽입 위치 */}
        <div
          style={{
            position: "absolute",
            top: "100px",
            right: "60px",
            width: "220px",
            height: "auto",
            border: "1px solid #ccc",
            borderRadius: "8px",
            overflow: "hidden",
            backgroundColor: "white",
          }}
        >
          <img
            src={`/icons/report/all_report_view/map_image/${dongName}_map.png`}
            alt={`${dongName} 위치 지도`}
            style={{ width: "100%", height: "auto", display: "block" }}
          />
        </div>

        {/* 중요지표 문구 (종이 위) */}
        <div
          style={{
            position: "absolute",
            top: "440px",
            left: "490px",
            width: "240px",
            fontSize: "17px",
            lineHeight: "1.6",
            textAlign: "center",
            color: "#333",
          }}
        >
          <span>{userName}</span> 님의 중요지표인<br />
          <span style={{ fontWeight: "bold", color: "#4c8689" }}>{indicatorText}</span><span>가</span>
          <br />
          특징인 동네를 분석하여 <br></br>추천해드립니다.
        </div>

        {/* 동 이름 */}
        <div
          style={{
            position: "absolute",
            top: "620px",
            left: "560px",
            fontWeight: "bold",
            fontSize: "17px",
          }}
        >
          {dongName}
        </div>

        {/* 위치 */}
        <div
          style={{
            position: "absolute",
            top: "690px",
            left: "560px",
            fontSize: "17px",
            fontWeight: "bold",
          }}
        >
          {fullLocation}
        </div>

        {/* 동네 주요 특징 */}
        <div style={{ position: "absolute", top: "900px", left: "300px", fontSize: "15px" }}>
          {dongFeatures[0]}
        </div>
        <div style={{ position: "absolute", top: "900px", left: "590px", fontSize: "15px" }}>
          {dongFeatures[1]}
        </div>

        {/* 설명 */}
        <div
          style={{
            position: "absolute",
            top: "935px",
            left: "180px",
            fontSize: "12.5px",
            lineHeight: "1.4",
            width: "565px",
            fontFamily: "Pretendard-Regular",
            color: "#333",
          }}
        >
          {descriptionTexts.map((text: string, idx: number) => (
            <div key={idx} style={{ display: "flex", marginBottom: "5px" }}>
              <span style={{ color: "#0E6D62", fontWeight: "bold", marginRight: "6px" }}>●</span>
              <p style={{ margin: 0, padding: 0 }}>{text}</p>
            </div>
          ))}
        </div>

      </div>
    </div>
  );
}
