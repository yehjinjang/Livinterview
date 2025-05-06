import { useLocation, useNavigate } from "react-router-dom";
import { useEffect, useState, ChangeEvent } from "react";

export default function RoomieClean() {
  /* ─── ① 전달‑값 ─── */
  const { state }      = useLocation();
  const navigate       = useNavigate();
  const { imageUrl, title } = state as { imageUrl: string; title?: string };

  /* ─── ② 상태 ─── */
  type Step = "analyzing" | "askClean" | "labeling";
  const [step,   setStep]   = useState<Step>("analyzing");
  const [blankUrl, setBlankUrl] = useState<string>("");     // 빈 방 URL
  const [imageId,  setImageId]  = useState<string>("");     // 서버에 저장된 ID
  const [labels,   setLabels]   = useState<string[]>([]);
  const [error,    setError]    = useState<string>();

  /* ─── ③ 빈방 생성 파이프라인 ─── */
  useEffect(() => {
    if (!imageUrl) { setError("이미지 URL 누락"); return; }

    (async () => {
      try {
        /* 1) vision → image_id 스트림 수신 */
        const vRes    = await fetch("http://localhost:8000/vision/analyze-image",{
          method :"POST",
          headers: { "Content-Type":"application/json" },
          body   : JSON.stringify({ image_url: imageUrl }),
        });
        const reader  = vRes.body?.getReader();
        if (!reader)  throw new Error("스트림 없음");

        const decoder = new TextDecoder("utf-8");
        let   id      = "";
        while (!id) {
          const { done, value } = await reader.read();
          if (done) throw new Error("image_id 수신 실패");
          const chunk = decoder.decode(value,{ stream:true });
          const m     = chunk.match(/__IMAGE_ID__:(\S+)__END__STREAM__/);
          if (m) id = m[1];
        }
        setImageId(id);

        /* 2) cleaning/inpaint → 빈방 URL */
        const { inpainted_url } = await fetch("http://localhost:8000/cleaning/inpaint",{
          method:"POST",
          body  : new URLSearchParams({ image_id:id }),
        }).then(r=>r.json());

        if (!inpainted_url) throw new Error("빈 방 생성 실패");
        setBlankUrl(inpainted_url);
        setStep("askClean");
      } catch (e) {
        console.error(e);
        setError("빈 방 생성 단계에서 오류가 발생했어요.");
      }
    })();
  }, [imageUrl]);

  /* ─── ④ “청소할래?” 결정 ─── */
  const handleAskClean = async (clean: boolean) => {
    if (!blankUrl) return;

    /* 청소 안 하고 바로 챗 */
    if (!clean) {
      navigate("/roomie/chat",{ state:{ imageUrl: blankUrl, title, blankRoomUrl: blankUrl } });
      return;
    }

    /* 1) 감지된 라벨 요청 */
    try{
      const fd = new FormData();
      fd.append("image_id", imageId);
      const { labels } = await fetch("http://localhost:8000/cleaning/labels",{
        method:"POST", body:fd
      }).then(r=>r.json());

      setLabels(labels || []);
      setStep("labeling");
    }catch{
      setError("감지된 가구를 가져오지 못했어요.");
    }
  };

  /* ─── ⑤ 보호 항목 입력 후 청소 실행 ─── */
  const handleProtectSubmit = async (e: ChangeEvent<HTMLInputElement>) => {
    const keepItems = e.target.value.split(",").map(t=>t.trim()).filter(Boolean);
    if (!keepItems.length) return;

    const fd = new FormData();
    fd.append("image_id", imageId);
    keepItems.forEach(it => fd.append("selected_items", it));

    try{
      /* 마스크 생성 */
      await fetch("http://localhost:8000/cleaning/removal",{ method:"POST", body:fd });

      /* 최종 인페인트 */
      const { inpainted_url } = await fetch("http://localhost:8000/cleaning/inpaint",{
        method:"POST",
        body:new URLSearchParams({ image_id:imageId }),
      }).then(r=>r.json());

      if (!inpainted_url) throw new Error();
      navigate("/roomie/chat",{
        state:{ imageUrl: inpainted_url, title, blankRoomUrl: inpainted_url }
      });
    }catch{
      setError("청소 과정에서 문제가 생겼어요.");
    }
  };

  /* ─── ⑥ 렌더링 ─── */
  if (error)                return <div className="p-4 text-red-500">{error}</div>;
  if (step==="analyzing")   return <p className="p-4">방을 분석하고 있어요…</p>;

  return (
    <div className="p-6 space-y-6">
      {blankUrl && <img src={blankUrl} alt="빈 방" className="w-full rounded-xl shadow" />}

      {step==="askClean" && (
        <div className="flex gap-4 justify-center">
          <button onClick={()=>handleAskClean(true)}
                  className="px-6 py-3 bg-blue-600 text-white rounded-xl">청소할래</button>
          <button onClick={()=>handleAskClean(false)}
                  className="px-6 py-3 bg-gray-300 rounded-xl">이미 깨끗해</button>
        </div>
      )}

      {step==="labeling" && (
        <>
          <p className="font-semibold">감지된 물건: {labels.join(", ") || "없음"}</p>
          <input
            className="w-full p-3 border rounded"
            placeholder="콤마로 구분해서 남길 가구 입력 ‑ 예: sofa,bed"
            onBlur={handleProtectSubmit}
          />
        </>
      )}
    </div>
  );
}
