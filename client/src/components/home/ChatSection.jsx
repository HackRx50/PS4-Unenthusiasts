import React,{useState} from "react";
import {
  Avatar,
  Button,
  Icon,
  Menu,
  MenuButton,
  MenuItem,
  MenuList,
} from "@chakra-ui/react";
import { ChevronDownIcon } from "@chakra-ui/icons";
import { FaRegUserCircle } from "react-icons/fa";
import { BiLogOut } from "react-icons/bi";
import { IoMdPricetags } from "react-icons/io";
import { IoSearch } from "react-icons/io5";
import { MdNightlight } from "react-icons/md";
import { FaSun } from "react-icons/fa6";
import NullImage from "../../assets/BgImageNull.svg";
import { BsStars } from "react-icons/bs";
import { FaUser } from "react-icons/fa";
import { useUser } from "../../context/UserContext"
import axios from "axios";

const ChatSection = ({ currentChatData, darkMode, setDarkMode }) => {
  const { user } = useUser();
  const [message, setMessage] = useState("");
  const handleSubmit = async () => {
    if (!message.trim()) return;

    const url = "http://localhost:8000/chat";

    try {

      const response = await axios.post(url, {
        query: message
      }, {
        headers: {
          Authorization: `Bearer ${user?.access_token}`
        }
      });
      console.log("Response:", response.data);
      setMessage("");
    } catch (error) {
      console.error("Error:", error);
    }
  };

  const handleKeyPress = (event) => {
    if (event.key === 'Enter') {
      handleSubmit(); 
    }
  };

  return (
    <div className="w-full h-full flex flex-col items-center justify-center">
      <div
        className={`py-3 transition-all duration-200 shadow-lg px-8 w-full flex justify-between items-center z-[5000]
        ${darkMode ? "bg-gray-800 shadow-gray-950" : "bg-white shadow-gray-100"}
      `}
      >
        <div
          className={`text-2xl font-semibold ${darkMode ? "text-white" : "text-[#1B2559]"
            }`}
        >
          {currentChatData ? currentChatData.chat_title : "Chat"}
        </div>
        <div className="flex items-center justify-center gap-3">
          <div
            className={`p-2 rounded-full bg-gray-600 transition-all duration-200`}
            onClick={() => setDarkMode(!darkMode)}
          >
            {darkMode ? (
              <MdNightlight className="text-white cursor-pointer" />
            ) : (
              <FaSun className="text-white cursor-pointer" w="4" h="4" />
            )}
          </div>
          <Menu>
            <MenuButton as={Button} variant="unstyled">
              <div
                className={`flex items-center justify-center gap-2 rounded-2xl px-3 py-2 ${darkMode
                  ? "bg-gray-600 text-white"
                  : "bg-white text-[#1B2559]"
                  }`}
                style={{
                  boxShadow: "0 0 4px 4px #11111115",
                }}
              >
                <Avatar
                  name="Dan Abrahmov"
                  src="https://bit.ly/dan-abramov"
                  w="6"
                  h="6"
                />
                <div className="text-sm font-semibold">{user?.username}</div>
                <ChevronDownIcon />
              </div>
            </MenuButton>
            <MenuList>
              <MenuItem>
                <div className="flex items-center justify-center gap-2">
                  <FaRegUserCircle />
                  <div className="">Edit Profile</div>
                </div>
              </MenuItem>
              <MenuItem>
                <div className="flex items-center justify-center gap-2">
                  <IoMdPricetags />
                  <div className="">Billing</div>
                </div>
              </MenuItem>
              <MenuItem>
                <div className="flex items-center justify-center gap-2">
                  <BiLogOut />
                  <div className="">Logout</div>
                </div>
              </MenuItem>
            </MenuList>
          </Menu>
        </div>
      </div>
      <div
        className={`h-full transition-all duration-200 w-full py-4 px-20 ${darkMode ? "bg-gray-900" : "bg-gray-100"
          }`}
      >
        <div className="w-full h-full flex flex-col gap-2 items-center justify-center">
          {currentChatData ? (
            <div className="w-full py-2 h-full flex flex-col items-center justify-end overflow-y-auto">
              {currentChatData.messages.map((message, index) => (
                <div
                  key={index}
                  className={`flex items-center gap-4 w-full ${message.sender === "user" ? "justify-end" : "justify-start"
                    }`}
                >
                  <div
                    className={`flex items-center gap-2 ${message.sender === "user"
                      ? "flex-row-reverse"
                      : "flex-row"
                      }`}
                  >
                    <div
                      className={`${darkMode ? "text-white" : "text-[#1B2559]"
                        } transition-all duration-200`}
                    >
                      {message.sender === "user" ? <FaUser /> : <BsStars />}
                    </div>
                    <div
                      className={`text-sm transition-all duration-200 rounded-2xl px-4 py-2 ${message.sender === "user"
                        ? "bg-[#1B2559] text-white"
                        : `text-[#1B2559] ${darkMode ? "bg-gray-100" : "bg-white"}`
                        }`}
                    >
                      {message.content}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="w-full h-full flex flex-col items-center justify-center">
              <img src={NullImage} alt="null" className="h-[10rem]" />
            </div>
          )}
          <div className="w-full h-14 gap-4 flex justify-center items-center">
            <input
              type="text"
              placeholder="Send a message..."
              className="bg-white border-2 focus:border-[#1B2559] active:border-[#1B2559] border-gray-100 rounded-2xl text-sm px-4 h-full w-full"
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              onKeyPress={handleKeyPress} // Call handleKeyPress on key press
            />
            <button
              className="bg-[#1B2559] hover:bg-opacity-80 text-white flex items-center justify-center gap-3 rounded-2xl px-6 h-full"
              onClick={handleSubmit} // Call handleSubmit on button click
            >
              <IoSearch />
              <div className="text-sm font-semibold">Search</div>
            </button>
          </div>
          <div className="w-full h-8 flex text-xs text-gray-400 justify-between items-center">
            <div>© 2023 Unenthusiasts. All Rights Reserved.</div>
            <div className="flex items-center justify-center gap-2">
              <div>License</div>
              <div>Terms of Use</div>
              <div>Privacy Policy</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatSection;
