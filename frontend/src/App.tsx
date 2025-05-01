import { BrowserRouter, Routes, Route } from "react-router-dom";
import Home from "./pages/Home";
import LoginPage from "./pages/LoginPage"
import SurveyForm from "./pages/SurveyForm";
import Report from "./pages/Report"
import RoomieHome from "./pages/RoomieHome"
import ProfilePage from "./pages/ProfilePage"
import RoomieChat from "./pages/RoomieChat"
import RoomieResult from "./pages/RoomieResult"


function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<LoginPage />} />
        <Route path="/home" element={<Home />} />
        <Route path="/survey" element={<SurveyForm />} />
        <Route path="/report" element={<Report />} />
        <Route path="/profile" element={<ProfilePage />} /> 
        <Route path="/roomie" element={<RoomieHome />} /> 
        <Route path="/roomie/interior" element ={<RoomieChat />} />
        <Route path="/roomie/result" element={<RoomieResult />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;

