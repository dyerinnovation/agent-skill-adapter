import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import "./index.css";
import Dashboard from "./pages/Dashboard";
import Skills from "./pages/Skills";
import Training from "./pages/Training";

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/skills" element={<Skills />} />
        <Route path="/training" element={<Training />} />
      </Routes>
    </BrowserRouter>
  </React.StrictMode>
);
