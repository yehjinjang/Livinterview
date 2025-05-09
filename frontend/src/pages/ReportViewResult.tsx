import { useLocation } from "react-router-dom";

export default function ReportViewResult() {
  // 🔐 로그인한 사용자 이름 불러오기
  const storedUser = sessionStorage.getItem("user");
  const parsedUser = storedUser ? JSON.parse(storedUser) : null;
  const userName = parsedUser?.name || "이름 없음";

  // 📊 리포트 데이터 (설문 결과 기반)
  const location = useLocation();
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

  const indicatorDescription: Record<string, string> = {
    교통: "지역권역의 위치, 거주의 위치를 실내공간으로 중요하게 생각하는 편임",
    편의: "편의점, 다이소를 자주 이용하지 않지만 집 근처에 위치하는 것에 상대적으로 중요하게 생각함",
    안전: "집 근처 안전관련 기관 및 동네 안전지수 등을 중요하게 생각함",
    건강: "평소에 병/의원을 잘 찾아가지 않는 편으로 집 주변의 병/의원 위치가 중요하지 않음",
    녹지: "집 주변의 푸르른 환경에 대하여 선호도가 낮은 편임",
    생활: "장을 보거나 은행, 우체국 등의 생활관련시설 방문 횟수가 적지 않아 중요도가 높은 편임",
    놀이: "영화관, 코인노래방, PC 방등 취미활동 할 수 있는 공간에 대한 필요성이 낮아 중요도가 낮음",
    운동: "평소 운동을 선호하나, 집 주변 운동시설을 찾기보다는 거리가 약간 있어도 기존에 운동했던 시설에서 하는 것을 더 선호하는 편임",
  };

  return (
    <div className="flex flex-col items-start w-[794px] mt-12">
      <span className="text-sm text-gray-500 font-medium mb-1">3 페이지</span>

      <div
        id="pdf-result"
        style={{
          width: "794px",
          height: "1123px",
          backgroundImage: "url('/icons/report/all_report_view/03_result.jpg')",
          backgroundSize: "cover",
          backgroundPosition: "center",
          position: "relative",
          boxShadow: "0 0 8px rgba(0,0,0,0.1)",
        }}
      >
        {/* 🧑 사용자 이름 */}
        <div style={{ position: "absolute", top: "205px", left: "470px", fontSize: "20px", fontWeight: "bold", fontFamily: "Pretendard-Regular" }}>
          {userName}
        </div>

        {/* 🧑 사용자 이름 */}
        <div style={{ position: "absolute", top: "295px", left: "50px", fontSize: "18px", fontWeight: "bold", fontFamily: "Pretendard-Regular" }}>
          {userName}
        </div>

        {/* 📌 중요 지표 리스트 */}
        <div style={{ position: "absolute", top: "295px", left: "370px", fontSize: "18px", display: "flex", gap: "27px", fontFamily: "Pretendard-Regular" }}>
          {topIndicators.map((indicator: string, idx: number) => (
            <span key={idx} style={{ display: "inline-block" }}>
              {indicator}
            </span>
          ))}
        </div>

        {/* 🖼️ 중요 지표 아이콘 이미지 3개 */}
        {topIndicators.map((indicator: string, idx: number) => {

          const indicatorImageMap: Record<string, string> = {
            생활: "life",
            안전: "safety",
            교통: "transfer",
            편의: "convenience",
            건강: "health",
            녹지: "green",
            놀이: "play",
            운동: "workout",
          };
          const folderName = indicatorImageMap[indicator];
          const imagePath = `/icons/report/${folderName}/0.svg`;

          return (
            <div key={idx}>
              <img
                src={imagePath}
                alt={`${indicator} 이미지`}
                style={{
                  position: "absolute",
                  top: "350px",
                  left: `${65 + idx * 240}px`,
                  width: "180px",
                  height: "180px",
                  objectFit: "contain",
                }}
              />
              <div
                style={{
                  position: "absolute",
                  top: "540px",
                  left: `${95 + idx * 240}px`,
                  fontSize: "27px",
                  fontWeight: "bold",
                  color: "white",
                }}
              >
                {indicator} 지표
              </div>
            </div>
          );
        })}

        {/* 📌 설명 텍스트 영역 */}
        <div
          style={{
            position: "absolute",
            top: "600px",
            left: "29px",
            fontFamily: "Pretendard-Regular",
            fontSize: "14px",
            color: "#333",
            lineHeight: "1.6",
            width: "720px",
            boxSizing: "border-box",
          }}
        >
          {[
            "집을 찾으실 때 다양한 부분들을 복합적으로 고려하시겠지만, 집 근처 대형 마트, 은행, 우체국 등의 시설이 집 근처에 있는지 중요하게 생각하시는 군요. 그 외 그 동네가 얼마나 안전한지, 경찰서는 집에서 얼마나 가까운 곳에 있는지, 집 근처 지하철 역의 위치 등이 집과 가까운지 등을 신경 쓰시는 스타일이시네요.",
            "실제 내가 살아보면 어떨까에 대해 생각하면서 여러 요소를 꼼꼼하게 확인하고 주거지를 고르는 당신을 위해 안전하면서도 편안함이 있는 오피스텔들을 찾아볼게요!",
          ].map((text, idx) => (
            <div key={idx} style={{ display: "flex", marginBottom: "6px" }}>
              <span style={{ color: "#0E6D62", fontWeight: "bold", marginRight: "8px" }}>●</span>
              <p style={{ margin: 0, padding: 0 }}>{text}</p>
            </div>
          ))}
        </div>


        {/* 📊 하단 지표 결과 */} 
        <div style={{ position: "absolute", top: "745px", left: "29px", fontFamily: "Pretendard-Regular", fontSize: "13px", width: "720px", maxHeight: "380px", overflow: "hidden",  boxSizing: "border-box" }}>
          <div style={{ backgroundColor: "#4c8689", color: "white", padding: "5px 12px", fontSize: "15px", lineHeight: "1.6", whiteSpace: "nowrap", width: "251px" }}>
            <span style={{ fontWeight: "bold", fontSize: "18px" }}>{userName}</span> 님의 8가지 지표 분석
          </div>

          <table style={{ width: "100%", borderCollapse: "collapse", tableLayout: "fixed" }}>
            <thead>
              <tr style={{ backgroundColor: "#E9F0EF", color: "#333", fontSize: "15px" }}>
                <th style={{ padding: "5px", border: "1px solid #2D7F7F", width: "50px", textAlign: "center", color: "#4c8689", backgroundColor: "#d4e4e5" }}>지표</th>
                <th style={{ padding: "5px", border: "1px solid #2D7F7F", width: "200px", textAlign: "center", color: "#4c8689" }}>중요도</th>
                <th style={{ padding: "5px", border: "1px solid #2D7F7F", textAlign: "center", color: "#4c8689" }}>설명</th>
              </tr>
            </thead>
            <tbody>
              {Object.entries(scores as Record<string, number>).map(([label, score]) => (
                <tr key={label}>
                  <td style={{ padding: "3px", border: "1px solid #2D7F7F", fontWeight: "bold", backgroundColor: "#d4e4e5", textAlign: "center", color: "#4c8689", fontSize: "15px" }}>{label}</td>
                  <td style={{ padding: "3px", border: "1px solid #2D7F7F", backgroundColor: "white", color: "#0E6D62", fontSize: "14px" }}>
                    <div style={{ display: "flex", alignItems: "center", gap: "10px", justifyContent: "center" }}>
                      <span>{score}</span>
                      <div style={{ width: "150px", backgroundColor: "#E5E7EB", height: "8px", borderRadius: "4px" }}>
                        <div style={{ width: `${score}%`, height: "100%", backgroundColor: "#0E6D62", borderRadius: "4px" }} />
                      </div>
                    </div>
                  </td>
                  <td style={{
                    padding: "4px",
                    border: "1px solid #2D7F7F",
                    lineHeight: "1.4",
                    backgroundColor: "white",
                    textAlign: "left",           
                    wordBreak: "break-word",          
                    overflow: "hidden",      
                  }}>
                    {indicatorDescription[label] || ""}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>


  

      </div>
    </div>
  );
}
