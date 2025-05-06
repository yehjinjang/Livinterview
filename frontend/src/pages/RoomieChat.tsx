import { useLocation, useNavigate } from "react-router-dom";
import { useEffect, useState, useRef } from "react";
import ChatMessageList from "../components/ChatMessageList";
import MessageInput     from "../components/MessageInput";
import TypingBubble     from "../components/TypingBubble";
import LoadingSpinner   from "../components/LoadingSpinner";

interface ChatMessage {
  type: "text" | "image";
  text?: string;
  src?: string;
  sender: "user" | "bot";
}

export default function RoomieChat() {
  const { state } = useLocation();
  const navigate  = useNavigate();

  /* RoomieClean 에서 넘어온 blankRoomUrl 도 받는다 */
  const { imageUrl, title, blankRoomUrl } = state as {
    imageUrl: string;
    title?:  string;
    blankRoomUrl?: string;
  };

  /* -------------- state -------------- */
  const [messages,   setMessages]   = useState<ChatMessage[]>([]);
  const [input,      setInput]      = useState("");
  const [typingText, setTypingText] = useState("");
  const [isSending,  setIsSending]  = useState(false);
  const [isGenerating,setIsGenerating]=useState(false);
  const [isAnalyzing,setIsAnalyzing]=useState(true);
  const [summaryText,setSummaryText]=useState<string|null>(null);

  const bottomRef = useRef<HTMLDivElement>(null);
  const didInit   = useRef(false);

  /* ---------- 최초 인삿말 & 이미지 ---------- */
  useEffect(() => {
    if (!imageUrl || didInit.current) return;
    didInit.current = true;

    setMessages([
      { type:"text",  text:"안녕! 난 인테리어 도우미 Roomie야 😊", sender:"bot" },
      /* 원본 대신 blankRoomUrl 이 있으면 그걸 보여준다 */
      { type:"image", src: blankRoomUrl ?? imageUrl,               sender:"bot" },
    ]);
    setIsAnalyzing(false);

    /* 스트리밍 로직 */
    (async () => {
      try {
        const res = await fetch("http://localhost:8000/chat",{
          method :"POST",
          headers:{ "Content-Type":"application/json"},
          body   : JSON.stringify({ image_url: blankRoomUrl ?? imageUrl }) /* ✅ */
        });
        if(!res.body) throw new Error("스트림 없음");
        const reader  = res.body.getReader();
        const decoder = new TextDecoder("utf-8");
        let typing = "";
        while(true){
          const {done,value}=await reader.read();
          if(done)break;
          const chunk=decoder.decode(value,{stream:true});
          if(chunk.includes("__END__STREAM__"))break;
          typing+=chunk;
          setTypingText(t=>t+chunk);
        }
        setMessages(p=>[...p,{type:"text",text:typing,sender:"bot"}]);
        setTypingText("");
      }catch{
        setMessages([{type:"text",text:"초기 메시지 실패",sender:"bot"}]);
        setIsAnalyzing(false);
      }
    })();
  }, [imageUrl, blankRoomUrl]);

  /* ---------- 자동 스크롤 ---------- */
  useEffect(() => {
    if (!messages.length && !typingText) return;

    const last = messages[messages.length-1];
    if(last?.sender==="bot" && last.text?.includes("좋아! 이대로 방을 꾸며볼게"))
      generateImageAndNavigate(summaryText);

    bottomRef.current?.scrollIntoView({behavior:"smooth"});
  }, [messages, typingText]);

  /* ---------- 메시지 전송 ---------- */
  const sendMessage = async () => {
    if (!input.trim() || isSending || isGenerating) return;
    const userMsg = input.trim();

    setMessages(p=>[...p,{type:"text",text:userMsg,sender:"user"}]);
    setInput(""); setIsSending(true); setTypingText("");

    if(summaryText && ["응","yes","네"].includes(userMsg.toLowerCase())){
      await generateImageAndNavigate(summaryText);
      setIsSending(false);
      return;
    }

    try{
      const res = await fetch("http://localhost:8000/chat",{
        method :"POST",
        headers:{ "Content-Type":"application/json"},
        body   : JSON.stringify({ user_input:userMsg })
      });
      if(!res.body) throw new Error();
      const reader  = res.body.getReader();
      const decoder = new TextDecoder("utf-8");
      let full="";
      while(true){
        const {done,value}=await reader.read();
        if(done)break;
        const chunk=decoder.decode(value,{stream:true});
        full+=chunk;
        if(chunk.includes("__END__STREAM__"))break;
        setTypingText(t=>t+chunk);
      }
      setMessages(p=>[...p,{type:"text",text:full.replace("__END__STREAM__","").trim(),sender:"bot"}]);
    }catch{
      setMessages(p=>[...p,{type:"text",text:"서버 오류",sender:"bot"}]);
    }finally{
      setTypingText(""); setIsSending(false);
    }
  };

  /* ---------- 요약 & 이미지 생성 ---------- */
  const summarizeAndGenerateImage = async () => {
    if(isSending||isGenerating) return;
    setIsGenerating(true);
    try{
      const { result } = await fetch("http://localhost:8000/analyze/summarize-memory",
                                     {method:"POST"}).then(r=>r.json());
      if(result==="요약할 대화가 없습니다."){
        setMessages(p=>[...p,{type:"text",text:"아직 인테리어를 하기엔 부족해!",sender:"bot"}]);
        return;
      }
      setSummaryText(result);
      setMessages(p=>[...p,{type:"text",
        text:`지금까지 대화를 정리했어!\n\n${result}\n\n맞으면 "응"이라고 답해줘!`,
        sender:"bot"}]);
    }finally{ setIsGenerating(false); }
  };

  const generateImageAndNavigate = async (prompt:string|null) => {
    if(!prompt) return;
    try{
      const { image_url } = await fetch("http://localhost:8000/generate-image",{
        method:"POST", headers:{ "Content-Type":"application/json"},
        body:JSON.stringify({ prompt })
      }).then(r=>r.json());

      navigate("/roomie-result",{
        state:{
          originalImage : blankRoomUrl ?? imageUrl,
          generatedImage: image_url,
          title,
        }
      });
    }catch{
      setMessages(p=>[...p,{type:"text",text:"이미지 생성 실패 ㅠㅠ",sender:"bot"}]);
    }
  };

  /* ---------- 렌더링 ---------- */
  if(isAnalyzing) return <LoadingSpinner text="채팅 준비 중..." />;

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        <ChatMessageList messages={messages}/>
        {typingText && <TypingBubble text={typingText}/>}
        <div ref={bottomRef}/>
      </div>

      <MessageInput
        input={input}
        setInput={setInput}
        isSending={isSending||!!typingText}
        isGenerating={isGenerating}
        sendMessage={sendMessage}
        summarizeAndGenerateImage={summarizeAndGenerateImage}
      />
    </div>
  );
}
