import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import "./index.css";
import Layout from "./components/Layout";
import Dashboard from "./pages/Dashboard";
import Skills from "./pages/Skills";
import Training from "./pages/Training";
import Evaluation from "./pages/Evaluation";

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <BrowserRouter>
      <Routes>
        <Route element={<Layout />}>
          <Route path="/" element={<Dashboard />} />
          <Route path="/skills" element={<Skills />} />
          <Route path="/training" element={<Training />} />
          <Route path="/evaluation" element={<Evaluation />} />
        </Route>
      </Routes>
    </BrowserRouter>
  </React.StrictMode>
);
