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

export default function RoomieChat() {
  const { state } = useLocation();
  const navigate = useNavigate();
  const [isAnalyzing, setIsAnalyzing] = useState(true);

  const {
    imageUrl,
    title,
    blankRoomUrl,
    imageId: passedImageId,
    sessionId,
    originalImageId,
    isClean,
  } = state as {
    imageUrl: string;
    title?: string;
    blankRoomUrl?: string;
    imageId: string;
    sessionId: string;
    originalImageId?: string;
    isClean: boolean;
  };

  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [typingText, setTypingText] = useState("");
  const [isSending, setIsSending] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const [summaryText, setSummaryText] = useState<string | null>(null);

  const bottomRef = useRef<HTMLDivElement>(null);
  const didInit = useRef(false);

  console.log("🔍 RoomieChat state", {
  imageUrl,
  blankRoomUrl,
  imageId: passedImageId,
  originalImageId,
  isClean,
  sessionId,
});

  // 초기 구조 분석 및 채팅 시작
  useEffect(() => {
    if (!passedImageId || didInit.current) return;
    didInit.current = true;

    const rawSrc = isClean
      ? blankRoomUrl!
      : `http://localhost:8000/data/uploads/${originalImageId}.jpg`;
    const resolvedSrc = rawSrc.startsWith("http")
      ? rawSrc
      : `http://localhost:8000${rawSrc}`;

    const preloadImg = new Image();
    preloadImg.src = resolvedSrc;
    preloadImg.onload = () => {
      console.log("✅ 이미지 preload 완료", resolvedSrc);

      // 첫 번째 메시지 추가 (방 이미지와 "좋아! 이제 방을 같이 꾸며보자 😊")
      setMessages([
        { type: "text", text: "좋아! 이제 방을 같이 꾸며보자 😊", sender: "bot" },
        { type: "image", src: resolvedSrc, sender: "bot" },
      ]);

      // 두 번째 메시지 추가 (1초 후에 "우선 방이 어떻게 생겼는지 볼게… 👀")
      setTimeout(() => {
        setMessages((prevMessages) => [
          ...prevMessages,
          {
            type: "text",
            text: "우선 방이 어떻게 생겼는지 볼게… 👀" ,
            sender: "bot",
          },
        ]);
      }, 1000); // 1초 후에 두 번째 메시지 추가

      // 스트리밍 시작
      setIsAnalyzing(false);
      runInitialChat(passedImageId, isClean);
    };
  }, [passedImageId]);

  // 첫 대화 흐름 실행
  const runInitialChat = async (id: string, clean: boolean) => {
    console.log("🟢 runInitialChat called with", { id, clean, sessionId });
    const res = await fetch("http://localhost:8000/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        image_id: id,
        is_clean: clean,
        session_id: sessionId,
      }),
    });

    if (!res.body) throw new Error("스트림 없음");

    const reader = res.body.getReader();
    const decoder = new TextDecoder("utf-8");

    let fullMessage = "";
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      const chunk = decoder.decode(value, { stream: true });
      if (chunk.includes("__END__STREAM__")) break;

      fullMessage += chunk;
      setMessages((prev) => {
        const last = prev[prev.length - 1];
        if (last?.sender === "bot" && last.type === "text") {
          return [...prev.slice(0, -1), { ...last, text: last.text + chunk }];
        } else {
          return [
            ...prev,
            { type: "text", text: chunk, sender: "bot" },
          ];
        }
      });
    }

    setTypingText("");
  };



  const sendMessage = async () => {
    if (!input.trim() || isSending || isGenerating) return;
    const userMsg = input.trim();

    setMessages((p) => [...p, { type: "text", text: userMsg, sender: "user" }]);
    setInput("");
    setIsSending(true);
    setTypingText("");

    if (summaryText && ["응", "yes", "네"].includes(userMsg.toLowerCase())) {
      // 1. 스트리밍 출력용 텍스트
      const message = "그럼 이대로 인테리어 해줄게! 잠시만 기다려줘.";

      setTypingText(""); // 혹시 남은 스트리밍 있으면 초기화
      for (const ch of message) {
        await new Promise((r) => setTimeout(r, 30)); // 부드러운 출력
        setTypingText((prev) => prev + ch);
      }

      setMessages((prev) => [...prev, { type: "text", text: message, sender: "bot" }]);
      setTypingText(""); // 스트리밍 종료

      // 2. 바로 이미지 생성 + 이동
      await generateImageAndNavigate(summaryText);
      setIsSending(false);
      return;
    }

    try {
      const res = await fetch("http://localhost:8000/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_input: userMsg, session_id: sessionId, }),
      });

      if (!res.body) throw new Error("스트림 없음");
      const reader = res.body.getReader();
      const decoder = new TextDecoder("utf-8");
      let full = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        const chunk = decoder.decode(value, { stream: true });
        full += chunk;
        if (chunk.includes("__END__STREAM__")) break;
        setTypingText((t) => t + chunk);
      }

      setMessages((p) => [
        ...p,
        { type: "text", text: full.replace("__END__STREAM__", "").trim(), sender: "bot" },
      ]);
    } catch {
      setMessages((p) => [...p, { type: "text", text: "서버 오류", sender: "bot" }]);
    } finally {
      setTypingText("");
      setIsSending(false);
    }
  };

  
  const summarizeAndGenerateImage = async () => {
    if (isSending || isGenerating) return;
    setIsGenerating(true);
    try {
      const res = await fetch("http://localhost:8000/analyze/summarize-memory", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ session_id: sessionId }),
      });

      if (!res.body) throw new Error("스트림 없음");
      const reader = res.body.getReader();
      const decoder = new TextDecoder("utf-8");

      let raw = "";
      setTypingText("");

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        const chunk = decoder.decode(value, { stream: true });
        if (chunk.includes("__END__STREAM__")) break;
        raw += chunk;
        setTypingText((prev) => prev + chunk);
      }

      setTypingText("");
      const trimmed = raw.trim().replace("__END__STREAM__", "");

      // 🛠 JSON 파싱 시도
      let summary = trimmed;
      try {
        const parsed = JSON.parse(trimmed);
        summary = parsed.result;
      } catch (e) {
        // JSON 아니면 그대로 사용 (ex: "요약할 대화가 없습니다.")
      }

      // 요약 불가 메시지 처리
      if (summary === "요약할 대화가 없습니다.") {
        const message = "아직 인테리어를 하기엔 부족해! 더 얘기해보자.";
        setMessages((p) => [...p, { type: "text", text: "", sender: "bot" }]);

        for (const ch of message) {
          await new Promise((r) => setTimeout(r, 30));
          setMessages((prev) => {
            const last = prev[prev.length - 1];
            if (last?.sender === "bot" && last.type === "text") {
              return [...prev.slice(0, -1), { ...last, text: last.text + ch }];
            } else {
              return [...prev, { type: "text", text: ch, sender: "bot" }];
            }
          });
        }

        return;
      }

      setSummaryText(summary);
      setMessages((p) => [
        ...p,
        {
          type: "text",
          text: `지금까지 대화를 정리했어!\n\n${summary}\n\n맞으면 "응"이라고 답해줘!`,
          sender: "bot",
        },
      ]);
    } catch {
      setMessages((p) => [...p, { type: "text", text: "요약 실패", sender: "bot" }]);
    } finally {
      setIsGenerating(false);
    }
  };



  const generateImageAndNavigate = async (prompt: string | null) => {
    if (!prompt) return;
    try {
      const { image_url } = await fetch("http://localhost:8000/generate-image", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt, session_id: sessionId, }),
      }).then((r) => r.json());

      localStorage.setItem("generatedImage", image_url);
      localStorage.setItem("originalImage", blankRoomUrl ?? imageUrl);

      navigate("/roomie-result", {
        state: {
          originalImage: blankRoomUrl ?? imageUrl,
          generatedImage: image_url,
          title,
        },
      });
    } catch {
      setMessages((p) => [...p, { type: "text", text: "이미지 생성 실패 ㅠㅠ", sender: "bot" }]);
    }
  };

  useEffect(() => {
    if (!messages.length && !typingText) return;
    const last = messages[messages.length - 1];
    if (last?.sender === "bot" && last.text?.includes("좋아! 이대로 방을 꾸며볼게")) {
      generateImageAndNavigate(summaryText);
    }
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, typingText]);

  if (isAnalyzing) {
  return <LoadingSpinner text="방을 불러오는 중이에요..." />;
}

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
          isSending={isSending || !!typingText}
          isGenerating={isGenerating}
          sendMessage={sendMessage}
          summarizeAndGenerateImage={summarizeAndGenerateImage}
        />
      </div>
    );
  }
