import React, { useEffect, useState } from 'react'
import { ChatSection, Sidebar } from "../components/home";
import { useUser } from "../context/UserContext";
import axios from "axios";
import { useToast } from "@chakra-ui/react";

const HomePage = () => {
  const { user } = useUser();
  const [chatData, setChatData] = useState([]);
  const [activeChatId, setActiveChatId] = useState(0);
  const [currentChatData, setCurrentChatData] = useState(null);
  const [darkMode, setDarkMode] = useState(false);

  const getChatData = async () => {
    const url = "http://127.0.0.1:8000/get_chats";
    await axios
      .get(url, {
        params: {
          user_id: user.userid,
        },
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${user?.token}`,
        },
      })
      .then((response) => {
        let temp = response.data.sessions;
        let data = [];
        for (let i = 0; i < temp.length; i++) {
          let chat = {
            chat_id: temp[i]._id,
            chat_title: "Chat " + (i + 1),
          };
          let messages = [];
          for (let j = 0; j < temp[i].context.length; j++) {
            let user = {
              message_id: 2 * j,
              sender: "user",
              content: temp[i].context[j].query,
            };
            messages.push(user);
            let assistant = {
              message_id: 2 * j + 1,
              sender: "assistant",
              content: temp[i].context[j].gpt_response,
            };
            messages.push(assistant);
          }
          chat["messages"] = messages;
          if (chat["messages"].length > 0) data.push(chat);
        }

        setChatData(data);
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
      const activeChatData = chatData.find(
        (chat) => chat.chat_id === activeChatId
      );
      setCurrentChatData(activeChatData);
    } else {
      setCurrentChatData(null);
    }
  }, [activeChatId, chatData]);

  const [isAction, setIsAction] = useState(false);
  const [msgId, setMsgId] = useState(null);

  const [logStatus, setLogStatus] = useState(null);

  const toast = useToast();

  useEffect(() => {
    if (isAction && msgId) {
      axios
        .get(`http://127.0.0.1:8000/log/${msgId}`)
        .then((response) => {
          if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
          } else {
            setIsAction(false);
            return response.json();
          }
        })
        .then((data) => setLogStatus(data))
        .catch((error) => console.error("Error:", error));
    } else {
      setLogStatus(null);
    }
  }, [msgId, isAction]);

  useEffect(() => {
    if (logStatus) {
      toast({
        title: "Log Status",
        description: logStatus,
        status: "info",
        duration: 9000,
        isClosable: true,
      });
    }
  }, [logStatus]);

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
        getChatData={getChatData}
        activeChatId={activeChatId}
        currentChatData={currentChatData}
        darkMode={darkMode}
        setIsAction={setIsAction}
        setMsgId={setMsgId}
        setDarkMode={setDarkMode}
      />
    </div>
  );
};

export default HomePage