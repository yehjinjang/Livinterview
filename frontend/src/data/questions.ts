import { Question } from "../types/question";
import { subwayStations } from "../data/stations";

export const questions: Question[] = [
// -MARK: 교통 
  {
    id: "1",
    category: "교통",
    title: "가장 가까웠으면 하는 지하철역이 있으신가요?",
    type: "autocomplete",
    icon: "/icons/report/transfer/subway.svg",
    options: subwayStations
  },
  {
    id: "1-subway",
    category: "교통",
    title: "지하철은 얼마나 자주 이용하시나요?",
    type: "radio",
    icon: "/icons/report/transfer/subway.svg",
    options: [
      "거의 이용하지 않는다",
      "가끔 이용한다",
      "보통이다",
      "자주 이용한다",
      "매우 자주 이용한다"
    ]
  },
  {
    id: "1-bus",
    category: "교통",
    title: "버스는 얼마나 자주 이용하시나요?",
    type: "radio",
    icon: "/icons/report/transfer/bus.svg",
    options: [
      "거의 이용하지 않는다",
      "가끔 이용한다",
      "보통이다",
      "자주 이용한다",
      "매우 자주 이용한다"
    ]
  },
  {
    id: "1-publicbicycle",
    category: "교통",
    title: "따릉이 대여소가 가까이 있으면 어떠신가요?",
    type: "radio",
    icon: "/icons/report/transfer/bicycle.svg",
    options: [
      "전혀 필요 없다",
      "거의 이용하지 않을 듯하다",
      "있으면 가끔 이용할 것 같다",
      "자주 이용할 것 같다",
      "꼭 있어야 한다"
    ]
  },
// -MARK: 편의 
  {
    id: "2-convenience",
    category: "편의",
    title: "편의점 이용 빈도가 어느 정도인가요?",
    type:"radio",
    icon: "/icons/report/convenience/convenience-store.svg",
    options: [
        "거의 안 간다 (한 달에 1~2번 이하)",
        "가끔 간다 (일주일 1회 이하)",
        "보통이다 (일주일 2~3회)",
        "자주 간다 (일주일 4~5회)",
        "매우 자주 간다 (거의 매일)"
      ],
  },
  {
    id: "2-daiso",
    category: "편의",
    title: "다이소는 얼마나 자주 가시나요?",
    type: "radio",
    icon: "/icons/report/convenience/daiso.svg",
    options: [
      "거의 안 간다 (한 달에 1~2번 이하)",
      "가끔 간다 (일주일 1회 이하)",
      "보통이다 (일주일 2~3회)",
      "자주 간다 (일주일 4~5회)",
      "매우 자주 간다 (거의 매일)"
    ],
  },
  {
    id: "2-laundry",
    category: "편의",
    title: "셀프빨래방이 근처에 있으면 좋으세요?",
    type: "radio",
    icon: "/icons/report/convenience/washing-machine.svg",
    options: [
      "전혀 필요 없다",
      "별로 상관 없다",
      "있으면 가끔 이용할 듯",
      "자주 이용할 듯",
      "꼭 필요하다 (최우선)"
    ],
  },
  {
    id: "2-bigmart",
    category: "편의",
    title: "대형마트를 얼마나 자주 가시나요?",
    type: "radio",
    icon: "/icons/report/convenience/bigmarket.svg",
    options: [
        "거의 안 간다 (한 달에 1~2번 이하)",
        "가끔 간다 (일주일 1회 이하)",
        "보통이다 (일주일 2~3회)",
        "자주 간다 (일주일 4~5회)",
        "매우 자주 간다 (거의 매일)"
    ],
  },
// -MARK: 안전
  {
    id: "3-firestation",
    category: "안전",
    title: "소방서나 119안전센터가 가까우면 더 안전하다고 느끼시나요?",
    type: "radio",
    icon: "/icons/report/safety/firefight.svg",
    options:[
        "전혀 신경 안 쓴다",
        "별로 중요하지 않다",
        "보통이다",
        "어느 정도 가까우면 좋다",
        "매우 중요하다 (최대한 가까워야 좋다)"
    ],
  },
  {
    id: "3-police",
    category: "안전",
    title: "경찰서나 파출소가 가까우면 더 안전하다고 느끼시나요?",
    type: "radio",
    icon: "/icons/report/safety/police.svg",
    options:[
        "전혀 신경 안 쓴다",
        "별로 중요하지 않다",
        "보통이다",
        "어느 정도 가까우면 좋다",
        "매우 중요하다 (최대한 가까워야 좋다)"
    ],
  },
// -MARK: 건강 
{
    id: "4-medical",
    category: "건강",
    title: "의료 시설은 얼마나 자주 이용하시나요?",
    type: "radio",
    icon: "/icons/report/health/hospital.svg",
    options: [
        "거의 안 감 (1년에 한두 번 이하)",
        "가끔 감 (분기별 1~2번)",
        "보통이다 (두 달에 1번 정도)",
        "자주 감 (한 달에 1~2번)",
        "매우 자주 감 (월 3번 이상)"
    ],
  },
  {
    id: "4-medical",
    category: "건강",
    title: "일반의원과 한의원 중 어떤 것을 더 선호하시나요?",
    type: "radio",
    icon: "/icons/report/health/hospital.svg",
    options: [
        "일반 의원",
        "한의원",
        "상관없음",
    ],
  },
  {
    id: "4-pharmacy",
    category: "건강",
    title: "약국을 얼마나 자주 이용하시나요?",
    type: "radio",
    icon: "/icons/report/health/pharmacy.svg",
    options: [
        "한달에 1~2회 이상",
        "분기 별로 1~2회",
        "거의 안가요",
    ],
  },
// -MARK: 자연 
{
    id: "5-green",
    category: "녹지",
    title: "자연 환경 중 어떤 걸 가장 선호하시나요?",
    type: "radio",
    icon: "/icons/report/green/stream.svg",
    options: [
        "한강이나 하천",
        "숲이나 산",
        "공원",
        "다 좋아요",
        "시티뷰가 더 좋음"
    ],
  },
  // -MARK: 생활 
  {
    id: "6-cafe",
    category: "생활",
    title: "집 근처에 카페가 많으면 좋으세요?",
    type: "radio",
    icon: "/icons/report/life/cafe.svg",
    options: [
        "전혀 필요 없다(거의 안간다)",
        "별로 상관없다",
        "보통이다",
        "자주 간다",
        "매우 자주 간다"
    ],
  },
  {
    id: "6-library",
    category: "생활",
    title: "도서관이 주변에 있으면 어떠신가요?",
    type: "radio",
    icon: "/icons/report/life/library.svg",
    options: [
        "전혀 필요 없다(거의 안간다)",
        "별로 상관없다",
        "보통이다",
        "자주 간다",
        "매우 자주 간다"
    ],
  },
  {
    id: "6-center",
    category: "생활",
    title: "주민센터가 주변에 있으면 어떠신가요?",
    type: "radio",
    icon: "/icons/report/life/center.svg",
    options: [
        "전혀 필요 없다(거의 안간다)",
        "별로 상관없다",
        "보통이다",
        "자주 간다",
        "매우 자주 간다"
    ],
  },
  {
    id: "6-sidedish",
    category: "생활",
    title: "반찬가게 같은 곳이 근처에 있으면 어떠신가요?",
    type: "radio",
    icon: "/icons/report/life/sidedish.svg",
    options: [
        "전혀 필요 없다(거의 안간다)",
        "별로 상관없다",
        "보통이다",
        "자주 간다",
        "매우 자주 간다"
    ],
  },
  {
    id: "6-bank",
    category: "생활",
    title: "은행이 주변에 있으면 어떠신가요?",
    type: "radio",
    icon: "/icons/report/life/bank.svg",
    options: [
        "전혀 필요 없다(거의 안간다)",
        "별로 상관없다",
        "보통이다",
        "자주 간다",
        "매우 자주 간다"
    ],
  },

// -MARK: 놀이 
{
    id: "7-karaoke",
    category: "놀이",
    title: "코인 노래방이나 PC방을 얼마나 자주 가시나요?",
    type: "radio",
    icon: "/icons/report/play/karaoke.svg",
    options: [
        "거의 안 간다 (한 달에 1~2번 이하)",
        "가끔 간다 (일주일 1회 이하)",
        "보통이다 (일주일 2~3회)",
        "자주 간다 (일주일 4~5회)",
        "매우 자주 간다 (거의 매일)"
    ],
  },
  {
    id: "7-theater",
    category: "놀이",
    title: "영화관(직접 관람) 이용 빈도는 어느 정도인가요?",
    type: "radio",
    icon: "/icons/report/play/movietheater.svg",
    options: [
        "거의 안 간다 (한 달에 1~2번 이하)",
        "가끔 간다 (일주일 1회 이하)",
        "보통이다 (일주일 2~3회)",
        "자주 간다 (일주일 4~5회)",
        "매우 자주 간다 (거의 매일)"
    ],
  },
  {
    id: "7-cultural",
    category: "놀이",
    title: "문화생활공간이 주변에 있으면 어떠신가요?",
    type: "radio",
    icon: "/icons/report/play/cultural-life.svg",
    options:[
        "전혀 신경 안 쓴다",
        "별로 중요하지 않다",
        "보통이다",
        "어느 정도 가까우면 좋다",
        "매우 중요하다"
    ],
  },

// -MARK: 운동
{
    id: "8-workout",
    category: "운동",
    title: "헬스장을 얼마나 자주 이용하시나요?",
    type: "radio",
    icon: "/icons/report/workout/healthcenter.svg",
    options: [
        "거의 안 간다 (한 달에 1~2번 이하)",
        "가끔 간다 (일주일 1회 이하)",
        "보통이다 (일주일 2~3회)",
        "자주 간다 (일주일 4~5회)",
        "매우 자주 간다 (거의 매일)"
    ],
  },
  {
    id: "8-workout",
    category: "운동",
    title: "공공체육시설이 근처에 있으면 어떠신가요?",
    type: "radio",
    icon: "/icons/report/workout/publicworkoutcenter.svg",
    options:[
        "전혀 신경 안 쓴다",
        "별로 중요하지 않다",
        "보통이다",
        "어느 정도 가까우면 좋다",
        "매우 중요하다"
    ],
  },

// MARK: 공간 스펙 
{
    id: "area_range",
    category: "주거",
    title: "찾으시는 오피스텔의 최소 평수를 입력해주세요.",
    type: "range",
    unit: "평",
    rangeIds: ["minSize"]
  },
  
// -MARK: 공간 형태 
{
    id: "residence_type",
    category: "주거",
    title: "어떤 주거 유형을 찾고 계세요?",
    type: "radio",
    options: ["원룸", "투룸", "쓰리룸 이상", "빌라", "오피스텔"],
    multi: true,
},

{
    id: "contract_type",
    category: "주거",
    title: "계약 형태는 어떤 걸 선호하시나요?",
    type: "radio",
    options: ["월세", "전세", "아직 잘 모르겠어요 (둘 다 괜찮아요)"],
  },
]