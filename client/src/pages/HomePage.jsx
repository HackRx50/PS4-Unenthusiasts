import React, { useEffect, useState } from 'react'
import { ChatSection, Sidebar } from '../components/home'
import sample_data from "../assets/sample_data.json"
import { useUser } from '../context/UserContext'
import axios from "axios";

const HomePage = () => {
  const { user } = useUser();
  const [chatData, setChatData] = useState(sample_data["chats"]);
  const [activeChatId, setActiveChatId] = useState(0);
  const [currentChatData, setCurrentChatData] = useState(null);
  const [darkMode, setDarkMode] = useState(false);

  const getChatData = async () => {
    const url = "http://localhost:8000/get_chats";
    await axios
      .get(url, {
        params: {
          session_id: "66cc847befc2d1c042dbcc4f",
        },
      })
      .then((response) => {
        let temp = response.data.sessions.context;
        let new_temp = [];
        for (let i = 0; i < temp.length; i++) {
          let query = temp[i].query;
          let response = temp[i].gpt_response;
          new_temp.push({
            message_id: 2 * i,
            sender: "user",
            content: query,
          });
          new_temp.push({
            message_id: 2 * i + 1,
            sender: "assistant",
            content: response,
          });
        }

        setChatData({
          chat_id: "1",
          messages: new_temp,
        });
      })
      .catch((error) => {
        console.error(error);
      });
  };

  useEffect(() => {
    getChatData();
  }, []);

  useEffect(() => {
    if (activeChatId) {
      const chatData = chatData.find(
        (chat) => chat.message_id === activeChatId
      );
      setCurrentChatData(chatData);
    } else {
      setCurrentChatData(null);
    }
  }, [activeChatId]);

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
};

export default HomePage