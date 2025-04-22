import { BrowserRouter, Routes, Route } from "react-router-dom";
import Home from "./pages/Home";
import SurveyForm from "./pages/SurveyForm";
import Report from "./pages/Report"
import RoomieHome from "./pages/RoomieHome"
 

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/survey" element={<SurveyForm />} />
        <Route path="/report" element={<Report />} />
        <Route path="/roomie" element={<RoomieHome />} /> 
      </Routes>
    </BrowserRouter>
  );
}

export default App;

