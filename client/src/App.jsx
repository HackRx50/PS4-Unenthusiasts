import React, { useState } from 'react'
import {BrowserRouter as Router, Route, Routes} from 'react-router-dom'
import { AuthPage, HomePage } from './pages'
import { UserProvider } from "./context/UserContext";

const App = () => {
  return (
    <div className="h-screen w-screen bg-[#FDFDFD] flex items-center justify-center overflow-hidden">
      <UserProvider>
      <Router>
        <Routes>
          <Route path="/" element={<AuthPage />} />
          <Route path="/home" element={<HomePage />} />
        </Routes>
      </Router>
      </UserProvider>
    </div>
  );
}

export default App