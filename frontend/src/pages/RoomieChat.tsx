import { useLocation, useNavigate } from "react-router-dom";
import { useEffect, useState, useRef } from "react";
import ChatMessageList from "../components/ChatMessageList";
import MessageInput from "../components/MessageInput";
import TypingBubble from "../components/TypingBubble";
import LoadingSpinner from "../components/LoadingSpinner";

interface ChatMessage {
  type: "text" | "image";
  text?: string;
  src?: string;
  sender: "user" | "bot";
}

/* fetch(url) → File 객체로 변환 */
const urlToFile = async (url: string): Promise<File> => {
  const res = await fetch(url);
  const blob = await res.blob();
  const ext = blob.type.split("/")[1] || "png";
  return new File([blob], `upload.${ext}`, { type: blob.type });
};

export default function RoomieChat() {
  const { state } = useLocation();
  const navigate = useNavigate();
  const { imageUrl, title } = state || {};

  /* ───────── state ───────── */
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [typingText, setTypingText] = useState("");
  const [isSending, setIsSending] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(true);
  const [summaryText, setSummaryText] = useState<string | null>(null); // ★ 요약 저장

  const bottomRef = useRef<HTMLDivElement>(null);
  const didInit = useRef(false);

  /* 이미지 분석 */
  useEffect(() => {
    if (!imageUrl || didInit.current) return;
    didInit.current = true;

    (async () => {
      try {
        // 1. 인삿말 먼저 추가
        setMessages([
          { type: "text", text: "안녕! 난 인테리어 도우미 Roomie야 😊", sender: "bot" },
          { type: "image", src: imageUrl, sender: "bot" },
        ]);

        setIsAnalyzing(false); // ✅ 바로 채팅 UI 띄움

        const res = await fetch("http://localhost:8000/chat", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ image_url: imageUrl }),
        });

        if (!res.body) throw new Error("스트림 없음");

        const reader = res.body.getReader();
        const decoder = new TextDecoder("utf-8");
        let typing = "";

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;
          const chunk = decoder.decode(value, { stream: true });
          if (chunk.includes("__END__STREAM__")) break;
          typing += chunk;
          setTypingText(prev => prev + chunk);
        }

        // ✅ 스트리밍된 텍스트를 메시지로 추가
        setMessages(prev => [
          ...prev,
          { type: "text", text: typing, sender: "bot" }
        ]);
        setTypingText("");
      } catch {
        setMessages([{ type: "text", text: "초기 메시지 실패", sender: "bot" }]);
        setIsAnalyzing(false);
      }
    })();
  }, [imageUrl]);

  

/* 채팅 스크롤 & 자동 전환 */
useEffect(() => {
  if (!messages.length && !typingText) return;

  const last = messages[messages.length - 1];
  if (last?.sender === "bot" && last.text?.includes("좋아! 이대로 방을 꾸며볼게"))
    generateImageAndNavigate(summaryText); // summaryText가 null이면 재검사

  bottomRef.current?.scrollIntoView({ behavior: "smooth" });
}, [messages, typingText]);


  /* 사용자 메시지 → /chat */
  const sendMessage = async () => {
    if (!input.trim() || isSending || isGenerating) return;
    const userMsg = input.trim();

    setMessages(prev => [...prev, { type: "text", text: userMsg, sender: "user" }]);
    setInput("");
    setIsSending(true);
    setTypingText("");

    /* “응” → 바로 이미지 생성 */
    if (summaryText && ["응", "yes", "네"].includes(userMsg.toLowerCase())) {
      await generateImageAndNavigate(summaryText);
      setIsSending(false);
      return;
    }

    try {
      const res = await fetch("http://localhost:8000/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_input: userMsg }),
      });
      if (!res.body) throw new Error();

      const reader = res.body.getReader();
      const decoder = new TextDecoder("utf-8");
      let full = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        const chunk = decoder.decode(value, { stream: true });
        full += chunk;
        if (chunk.includes("__END__STREAM__")) break;
        setTypingText(prev => prev + chunk);
      }

      const clean = full.replace("__END__STREAM__", "").trim();
      setMessages(prev => [...prev, { type: "text", text: clean, sender: "bot" }]);
    } catch {
      setMessages(prev => [...prev, { type: "text", text: "서버 오류", sender: "bot" }]);
    } finally {
      setTypingText("");
      setIsSending(false);
    }
  };

  /* 대화 요약 */
  const summarizeAndGenerateImage = async () => {
    if (isSending || isGenerating) return;
    setIsGenerating(true);

    try {
      const res = await fetch("http://localhost:8000/analyze/summarize-memory", {
        method: "POST",
      });
      const { result } = await res.json();

      if (result === "요약할 대화가 없습니다.") {
        setMessages(prev => [
          ...prev,
          { type: "text", text: "아직 인테리어를 하기엔 부족해! 대화를 더 해보자!", sender: "bot" },
        ]);
        return;
      }

      /* 요약 저장 + 동의 요청 */
      setSummaryText(result);
      setMessages(prev => [
        ...prev,
        {
          type: "text",
          text: `지금까지 대화한 내용을 정리해봤어!! \n\n${result}\n\n맞으면 "응"이라고 답해줘!`,
          sender: "bot",
        },
      ]);
    } finally {
      setIsGenerating(false);
    }
  };

  /* 이미지 생성 */
  const generateImageAndNavigate = async (prompt: string | null) => {
    if (!prompt) return; // 안전 가드
    try {
      const res = await fetch("http://localhost:8000/generate-image", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt }),
      });
      const { image_url } = await res.json();
      navigate("/roomie-result", {
        state: { originalImage: imageUrl, generatedImage: image_url, title },
      });
    } catch {
      setMessages(prev => [
        ...prev,
        { type: "text", text: "이미지 생성 실패 ㅠㅠ 다시 시도해줘.", sender: "bot" },
      ]);
    }
  };

  /* ───────── UI ───────── */
  if (isAnalyzing) return <LoadingSpinner text="방 분석 중... 잠시만 기다려주세요!" />;

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        <ChatMessageList messages={messages} />
        {typingText && <TypingBubble text={typingText} />}
        <div ref={bottomRef} />
      </div>

      <MessageInput
        input={input}
        setInput={setInput}
        isSending={isSending || typingText.length > 0}
        isGenerating={isGenerating}
        sendMessage={sendMessage}
        summarizeAndGenerateImage={summarizeAndGenerateImage}
      />
    </div>
  );
}