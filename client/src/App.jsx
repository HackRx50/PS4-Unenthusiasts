import React, { useState } from 'react'
import {BrowserRouter as Router, Route, Routes} from 'react-router-dom'
import { AuthPage, HomePage } from './pages'
import { UserProvider } from "./context/UserContext";
import { Spinner } from "@chakra-ui/react";

const App = () => {
  const [loading, setLoading] = useState(false);
  return (
    <div className="h-screen font-jakartasans w-screen bg-[#FDFDFD] flex items-center justify-center overflow-hidden">
      <UserProvider>
        <Router>
          <Routes>
            <Route path="/" element={<AuthPage setLoading={setLoading} />} />
            <Route
              path="/home"
              element={<HomePage setLoading={setLoading} />}
            />
          </Routes>
        </Router>
      </UserProvider>
      {loading && (
        <div className="w-screen fixed top-0 left-0 z-[300] flex items-center justify-center h-screen bg-black bg-opacity-10 backdrop-blur-sm">
          <Spinner
            thickness="4px"
            speed="0.65s"
            emptyColor="gray.200"
            color="blue.500"
            size="xl"
          />
        </div>
      )}
    </div>
  );
};

export default App