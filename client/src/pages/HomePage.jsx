import React, { useEffect, useState } from 'react'
import { ChatSection, Sidebar } from '../components/home'
import sample_data from "../assets/sample_data.json"
import { useUser } from '../context/UserContext'

const HomePage = () => {
  const { user } = useUser();
  const chatData = sample_data['chats'];
  const [activeChatId, setActiveChatId] = useState(0)
  const [currentChatData, setCurrentChatData] = useState(null)
  const [darkMode, setDarkMode] = useState(false);

  useEffect(() => {
    if (activeChatId) {
      const chatData = sample_data[
        "chats"
      ].find(
        (chat) => chat.chat_id === activeChatId
      );
      setCurrentChatData(chatData)
    } else {
      setCurrentChatData(null)
    }
  }, [activeChatId])

  return (
    <div className="h-full w-full flex items-center justify-center">
      <Sidebar
        activeChatId={activeChatId}
        setActiveChatId={setActiveChatId}
        chatData={chatData}
        darkMode={darkMode}
        setDarkMode={setDarkMode}
      />
      <ChatSection
        currentChatData={currentChatData}
        darkMode={darkMode}
        setDarkMode={setDarkMode}
      />
    </div>
  );
}

export default HomePage