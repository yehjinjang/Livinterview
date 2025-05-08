import { useLocation, useNavigate } from "react-router-dom";
import { useEffect, useState, useRef } from "react";

export default function RoomieClean() {
  const { state } = useLocation();
  const navigate = useNavigate();
  const { imageUrl, title } = state as { imageUrl: string; title?: string };

  type Step = "analyzing" | "askClean" | "labeling";
  const [step, setStep] = useState<Step>("analyzing");
  const [imageId, setImageId] = useState<string>("");
  const [labels, setLabels] = useState<string[]>([]);
  const [selectedItems, setSelectedItems] = useState<string[]>([]);
  const [error, setError] = useState<string>();
  const [loading, setLoading] = useState(false);
  const [messages, setMessages] = useState<{
    type: "text" | "image";
    text?: string;
    src?: string;
    sender: "bot" | "user";
  }[]>([]);

  const didInit = useRef(false);

  useEffect(() => {
    if (!imageUrl || didInit.current) return;
    didInit.current = true;

    (async () => {
      try {
        // 빈방 이미지 분석 시작
        const vRes = await fetch("http://localhost:8000/vision/analyze-image", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ image_url: imageUrl }),
        });

        const reader = vRes.body?.getReader();
        if (!reader) throw new Error("스트림 없음");

        const decoder = new TextDecoder("utf-8");
        let id = "";
        while (!id) {
          const { done, value } = await reader.read();
          if (done) throw new Error("image_id 수신 실패");
          const chunk = decoder.decode(value, { stream: true });
          const m = chunk.match(/__IMAGE_ID__:(\S+)__END__STREAM__/);
          if (m) id = m[1];
        }

        setImageId(id);
        setStep("askClean");
      } catch (e) {
        console.error(e);
        setError("이미지 분석 중 오류가 발생했어요.");
      }
    })();
  }, [imageUrl]);

  useEffect(() => {
    if (!imageId || step !== "askClean") return;
    setMessages([
      { type: "text", text: "안녕! 난 인테리어 도우미 Roomie야 😊", sender: "bot" },
      { type: "image", src: imageUrl, sender: "bot" },
      { type: "text", text: "혹시 방에 치워야 할 가구들이 있다면 청소해줄 수 있어! 어떻게 할래?", sender: "bot" },
    ]);
  }, [step, imageId]);

  const handleAskClean = async (clean: boolean) => {
    if (!imageId) return;
  
    if (!clean) {
      // "이미 깨끗해" 선택 시 빈방 분석 모델을 실행하지 않고 바로 채팅 페이지로 이동
      try {
        navigate("/roomie/chat", {
          state: {
            imageUrl,
            blankRoomUrl: imageUrl,
            imageId, // 이미지 ID 전달
          },
        });
      } catch (e) {
        console.error(e);
        setError("대화 시작 중 오류가 발생했어요.");
      }
      return;
    }
  
    // "청소할래" 선택 시 가구 감지 및 레이블 가져오기
    setLoading(true);
  
    try {
      const fd = new FormData();
      fd.append("image_id", imageId);
      const { labels } = await fetch("http://localhost:8000/cleaning/labels", {
        method: "POST",
        body: fd,
      }).then((r) => r.json());
  
      setLabels(labels || []);
      setStep("labeling");
    } catch {
      setError("감지된 가구를 가져오지 못했어요.");
    } finally {
      setLoading(false);
    }
  };
  

  const toggleItem = (item: string) => {
    setSelectedItems((prev) =>
      prev.includes(item) ? prev.filter((i) => i !== item) : [...prev, item]
    );
  };

  const handleProtectConfirm = async () => {
    const fd = new FormData();
    fd.append("image_id", imageId);
  
    if (selectedItems.length > 0) {
      selectedItems.forEach((item) => {
        const idx = labels.indexOf(item);
        if (idx !== -1) fd.append("selected_indices", String(idx));
      });
    }
  
    try {
      await fetch("http://localhost:8000/cleaning/removal", { method: "POST", body: fd });
  
      const { inpainted_url } = await fetch("http://localhost:8000/cleaning/inpaint", {
        method: "POST",
        body: new URLSearchParams({ image_id: imageId }),
      }).then((r) => r.json());
  
      if (!inpainted_url) throw new Error();
      navigate("/roomie/chat", {
        state: { imageUrl: inpainted_url, title, blankRoomUrl: inpainted_url },
      });
    } catch {
      setError("청소 과정에서 문제가 생겼어요.");
    }
  };

  if (error) return <div className="p-4 text-red-500">{error}</div>;
  if (step === "analyzing") return <p className="p-4">방을 분석하고 있어요…</p>;

  return (
    <div className="p-6 space-y-6">
      {messages.map((msg, i) =>
        msg.type === "text" ? (
          <p key={i} className="bg-gray-100 p-3 rounded-xl w-fit max-w-md">{msg.text}</p>
        ) : (
          <img key={i} src={msg.src} className="w-full rounded-xl shadow" />
        )
      )}

      {step === "askClean" && (
        <div className="space-y-4">
          {loading && <p className="text-center text-gray-500 animate-pulse">가구를 감지 중입니다… 🕵️</p>}
          <div className="flex gap-4 justify-center">
            <button onClick={() => handleAskClean(true)} className="px-6 py-3 bg-blue-600 text-white rounded-xl">
              청소할래
            </button>
            <button onClick={() => handleAskClean(false)} className="px-6 py-3 bg-gray-300 rounded-xl">
              이미 깨끗해
            </button>
          </div>
        </div>
      )}

      {step === "labeling" && (
        <>
          <p className="font-semibold">감지된 물건 중 남길 항목을 선택해주세요:</p>
          <div className="flex flex-wrap gap-2">
            {labels.map((label, i) => (
              <button
                key={i}
                onClick={() => toggleItem(label)}
                className={`px-4 py-2 rounded-xl border ${
                  selectedItems.includes(label)
                    ? "bg-blue-600 text-white"
                    : "bg-gray-200 text-gray-800"
                }`}
              >
                {label}
              </button>
            ))}
          </div>

          <button
            onClick={handleProtectConfirm}
            className="mt-4 w-full py-3 bg-green-600 text-white rounded-xl"
          >
            청소 시작
          </button>
        </>
      )}
    </div>
  );
}
