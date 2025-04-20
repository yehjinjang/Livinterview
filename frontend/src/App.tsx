import { BrowserRouter, Routes, Route } from "react-router-dom";
import Home from "./pages/Home";
import SurveyForm from "./pages/SurveyForm";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/survey" element={<SurveyForm />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;

