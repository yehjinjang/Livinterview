import { Question } from "../types/question";

export async function fetchQna(): Promise<Question[]> {
  const response = await fetch("http://localhost:8000/data/qna", {
    method: "GET",
    credentials: "include", // 세션 기반이라면 필요
  });

  if (!response.ok) {
    throw new Error("서버 요청 실패");
  }

  const data = await response.json();
  return data as Question[];
}
