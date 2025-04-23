export default function LoginPage() {
    const backend = import.meta.env.VITE_API_URL;
    
  
    const handleLogin = (provider: string) => {
      window.location.href = `${backend}/auth/${provider}`
    }
  
    return (
      <div className="flex flex-col items-center justify-center h-screen">
        <h1 className="text-xl mb-6">소셜 로그인</h1>
        <button onClick={() => handleLogin("google")} className="mb-4">구글 로그인</button>
        <button onClick={() => handleLogin("kakao")} className="mb-4">카카오 로그인</button>
        <button onClick={() => handleLogin("naver")}>네이버 로그인</button>
      </div>
    )
  }
  
  