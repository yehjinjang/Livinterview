export default function ReportViewGuide() {
  return (
    <div className="flex flex-col items-start w-[794px] mt-12">
      <span className="text-sm text-gray-500 font-medium mb-1">2 페이지</span>

      <div
        id="pdf-guide"
        style={{
          width: "794px",
          height: "1123px",
          backgroundImage: "url('/icons/report/all_report_view/02_guide.jpg')",
          backgroundSize:"100% 100%",
          backgroundPosition:"top left",
          boxShadow: "0 0 8px rgba(0,0,0,0.1)",
          padding: "80px 60px",
          boxSizing: "border-box",
          position: "relative",
        }}
      >
        {/* 오른쪽 상단 텍스트 */}
        <div
          style={{
            fontFamily: "210NuriGothicR",
            fontSize: "16px",
            lineHeight: "1.85",
            letterSpacing: "-0.3px",
            color: "#222",
            whiteSpace: "pre-line",
            textAlign: "justify", // 왼쪽과 오른쪽 모두 정렬
            position: "absolute",
            top: "145px",
            left: "250px",
            right: "70px",
          }}
        >
          {/* 안녕하세요, 삶권분석 리포트를 제작하고 있는 데보팀입니다.
          삶권분석 서비스를 신청해주셔서 감사드리며, 보내드리는
          삶권분석 리포트 읽으실 때 도움이 되실 수 있도록 안내를
          몇 가지 드리려고 합니다. 삶권분석 리포트를 읽으시기 전에
          참고 부탁드립니다. */}
        </div>

        {/* 중간 왼쪽 정렬 텍스트 */}


        {/* 내용 1 */}
        <div
          style={{
            position: "absolute",
            top: "455px",
            left: "150px", // 초록 번호 오른쪽으로 적당히 띄움
            right: "60px",
            fontSize: "16px",
            lineHeight: "1.85",
            letterSpacing: "-0.3px",
            textAlign: "justify",
            fontFamily: "Pretendard-Regular",
          }}
        >
          보내드리는 삶권분석 리포트는 처음 작성해주신 삶권분석 설문과 2022년 7월 기준 최근 1년 간의 데이터를 기반으로 제작하였습니다.
        </div>

        {/* 내용 2 */}
        <div
          style={{
            position: "absolute",
            top: "620px",
            left: "150px",
            right: "60px",
            fontSize: "16px",
            lineHeight: "1.85",
            letterSpacing: "-0.3px",
            textAlign: "justify",
            fontFamily: "Pretendard-Regular",
          }}
        >
          작성해주신 지하철역을 기준으로 250m, 500m, 1km 이내의 오피스텔을 위주로 분석해서 맞춤형 삶권분석 리포트를 전달해 드립니다. 추후 빌라, 다세대주택 등 다양한 주거 형태까지 분석해서 전달드릴 수 있도록 열심히 노력하겠습니다.
        </div>

        {/* 내용 3 */}
        <div
          style={{
            position: "absolute",
            top: "780px",
            left: "150px",
            right: "60px",
            fontSize: "16px",
            lineHeight: "1.85",
            letterSpacing: "-0.3px",
            textAlign: "justify",
            fontFamily: "Pretendard-Regular",
          }}
        >
          작성해주신 삶권분석 설문 답변과 데브디에서 개발한 8개 지표를 기준으로 맞춤형 오피스텔을 추천해드립니다. 8개 지표는 교통, 편의, 안전, 건강, 녹지, 생활, 놀이, 운동으로, 학군 등의 정보보다 1인가구에게 유의미한 항목들로 구성되었으며, 앞으로도 1인가구들이 거주지를 선택할 때 중요하게 생각하는 요소들을 지표로 개발할 예정입니다.
        </div>

        {/* 내용 4 */}
        <div
          style={{
            position: "absolute",
            top: "960px",
            left: "150px",
            right: "60px",
            fontSize: "16px",
            lineHeight: "1.85",
            letterSpacing: "-0.3px",
            textAlign: "justify",
            fontFamily: "Pretendard-Regular",
          }}
        >
          이 자료를 바탕으로 여러분의 라이프스타일에 맞는 좋은 집을 찾으실 수 있기를 진심으로 희망합니다. 하지만 변화무쌍한 데이터의 특성상 데브디가 제공하는 모든 정보는 참고 용도로만 사용할 수 있다는 점 다시 한번 말씀드립니다. 리포트를 읽으시면서 궁금하신 점이 있으시면 언제든지 contact@zipup.co.kr 로 연락주시기 바랍니다.
        </div>

      </div>
    </div>
  );
}
