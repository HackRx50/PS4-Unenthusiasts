import React, { useEffect, useState } from 'react'
import { TbMessageChatbot } from "react-icons/tb";

const Cell = ({
  chatId,
  title,
  lastUpdated,
  activeChatId,
  setActiveChatId,
  darkMode,
}) => {
  const today = new Date().toLocaleDateString();
  const chatDate = new Date(lastUpdated).toLocaleDateString();
  const hour = new Date(lastUpdated).getHours();
  const minute = new Date(lastUpdated).getMinutes();
  const lastUpdatedTime = `${hour}:${minute < 10 ? `0${minute}` : minute}`;
  const month = new Date(lastUpdated).getMonth() + 1;
  const date = new Date(lastUpdated).getDate();
  const lastUpdatedDate = `${month}/${date < 10 ? `0${date}` : date}`;

  if (today === chatDate) {
    lastUpdated = lastUpdatedTime;
  } else {
    lastUpdated = `${lastUpdatedDate} ${lastUpdatedTime}`;
  }

  return (
    <div
      className={`flex items-center gap-2 transition-all duration-200 justify-between w-full px-3 py-1 cursor-pointer ${chatId === activeChatId
          ? `${darkMode ? "bg-gray-600" : "bg-gray-100"}`
          : ""
        } ${darkMode ? "hover:bg-gray-600" : "hover:bg-gray-100"}`}
      onClick={() => {
        setActiveChatId(chatId);
      }}
    >
      <div className="w-6">
        <div
          className={`w-4 h-4 items-center justify-center flex transition-all duration-200 rounded-full ${chatId === activeChatId
              ? `bg-gradient-to-tr ${darkMode
                ? "from-white to-[#937ee3]"
                : "from-[#4A25E1] to-[#937ee3]"
              }`
              : "bg-gray-400 bg-opacity-50"
            }`}
        >
          <div
            className={`h-[0.64rem] w-[0.64rem] transition-all duration-200 rounded-full ${darkMode ? "bg-gray-800" : "bg-white"
              }`}
          />
        </div>
      </div>
      <div className="flex items-center w-full gap-3">
        <div className="flex flex-col">
          <div
            className={`font-semibold transition-all duration-200 text-sm ${chatId === activeChatId
                ? `bg-gradient-to-t ${darkMode
                  ? "from-white to-[#937ee3]"
                  : "from-[#4A25E1] to-[#937ee3]"
                } bg-clip-text text-transparent`
                : `font-thin ${darkMode ? "text-white" : "text-[#1B2559]"}`
              }`}
          >
            {title}
          </div>
          <div className="text-[#B8C1DA] text-xs">{lastUpdated}</div>
        </div>
      </div>
    </div>
  );
};


const Sidebar = ({
  activeChatId,
  setActiveChatId,
  chatData,
  darkMode,
  setDarkMode,
}) => {
  const [todayChats, setTodayChats] = useState(null);
  const [otherChats, setOtherChats] = useState(null);

  useEffect(() => {
    if (chatData !== null) {
      const today = new Date().toLocaleDateString();
      const todayChats = chatData.filter(
        (chat) => new Date(chat.updated_at).toLocaleDateString() === today
      );
      const otherChats = chatData.filter(
        (chat) => new Date(chat.updated_at).toLocaleDateString() !== today
      );
      setTodayChats(todayChats);
      setOtherChats(otherChats);
    }
  }, [chatData]);

  return (
    <div
      className={`w-80 h-screen z-[10000] transition-all duration-200 flex flex-col items-center justify-center gap-3 shadow-lg ${darkMode ? "bg-gray-800 shadow-gray-950" : "bg-white shadow-gray-200"
        }`}
    >
      <div
        className={`w-full transition-all duration-200 text-3xl py-10 flex items-center justify-center ${darkMode ? "text-white" : "text-[#1B2559]"
          }`}
      >
        <div className="font-bold">UNENTHU</div>
        <div className="">BOT</div>
      </div>
      <div
        className={`w-full transition-all duration-200 h-[1px] ${darkMode ? "bg-white" : "bg-[#1B2559]"
          }`}
      />
      <div className="flex transition-all duration-200 flex-col py-4 gap-2 w-full h-full overflow-y-auto">
        <button class="bg-white text-black border border-gray-300 rounded-lg px-4 py-2 shadow hover:bg-gray-100 transition duration-200 ease-in-out mx-3" onClick={()=>setActiveChatId(0)}>
          + New Chat
        </button>

        {todayChats?.length > 0 && (
          <div
            className={`px-3 text-xs ${darkMode ? "text-white" : "text-[#1B2559]"
              }`}
          >
            TODAY
          </div>
        )}
        {todayChats?.map((chat) => (
          <Cell
            key={chat.chat_id}
            chatId={chat.chat_id}
            title={chat.chat_title}
            lastUpdated={chat.updated_at}
            activeChatId={activeChatId}
            setActiveChatId={setActiveChatId}
            darkMode={darkMode}
          />
        ))}
        {todayChats?.length > 0 && otherChats.length > 0 && (
          <div
            className={`w-full transition-all duration-200 h-[1px] ${darkMode ? "bg-white" : "bg-[#1B2559]"
              }`}
          />
        )}
        {otherChats?.length > 0 && (
          <div
            className={`px-3 transition-all duration-200 text-xs ${darkMode ? "text-white" : "text-[#1B2559]"
              }`}
          >
            Older chats
          </div>
        )}
        {otherChats?.map((chat) => (
          <Cell
            key={chat.chat_id}
            chatId={chat.chat_id}
            title={chat.chat_title}
            lastUpdated={chat.updated_at}
            activeChatId={activeChatId}
            setActiveChatId={setActiveChatId}
            darkMode={darkMode}
          />
        ))}
      </div>
      <div className="w-full h-96 px-4 pb-4 pt-9">
        <div className="w-full flex flex-col items-center justify-center h-full bg-gradient-to-t from-[#4A25E1] to-[#937ee3] rounded-2xl relative">
          <div className="absolute -top-[1.5rem] left-0 w-full flex justify-center items-center">
            <div className="w-[3rem] h-[3rem] flex items-center justify-center rounded-full border-4 border-white bg-gradient-to-tr from-[#4A25E1] to-[#937ee3]">
              <TbMessageChatbot className="text-white w-7 h-7" />
            </div>
          </div>
          <div className="text-white text-center font-bold text-sm mt-4">
            Go unlimited with PRO
          </div>
          <div className="text-white text-center w-[80%] font-thin tracking-tighter text-xs">
            Get your AI Project to another level and start doing more with
            Horizon AI Template PRO!
          </div>
          <div className="bg-white bg-opacity-10 px-4 text-white text-xs cursor-pointer mt-2 mx-5 py-1 rounded-2xl text-center hover:bg-opacity-20">
            Get started with PRO
          </div>
        </div>
      </div>
    </div>
  );
};

export default Sidebar