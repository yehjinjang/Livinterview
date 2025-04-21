import { BrowserRouter, Routes, Route } from "react-router-dom";
import Home from "./pages/Home";
import SurveyForm from "./pages/SurveyForm";
import Report from "./pages/Report"

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/survey" element={<SurveyForm />} />
        <Route path="/report" element={<Report />} /> 
      </Routes>
    </BrowserRouter>
  );
}

export default App;

