import { BrowserRouter, Routes, Route } from "react-router-dom";
import Home from "./pages/Home";
import LoginPage from "./pages/LoginPage"
import SurveyForm from "./pages/SurveyForm";
import Report from "./pages/Report"
import RoomieHome from "./pages/RoomieHome"
import ProfilePage from "./pages/ProfilePage"


function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<LoginPage />} />
        <Route path="/roomie" element={<RoomieHome />} /> 
        <Route path="/home" element={<Home />} />
        <Route path="/survey" element={<SurveyForm />} />
        <Route path="/report" element={<Report />} />
        <Route path="/profile" element={<ProfilePage />} /> 
      </Routes>
    </BrowserRouter>
  );
}

export default App;

