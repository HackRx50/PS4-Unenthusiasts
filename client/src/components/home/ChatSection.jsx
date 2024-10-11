import React, { useEffect, useRef, useState } from "react";
import {
  Avatar,
  Button,
  Checkbox,
  Drawer,
  DrawerBody,
  DrawerCloseButton,
  DrawerContent,
  DrawerFooter,
  DrawerHeader,
  DrawerOverlay,
  Input,
  Menu,
  MenuButton,
  MenuItem,
  MenuList,
  useDisclosure,
} from "@chakra-ui/react";
import { ChevronDownIcon } from "@chakra-ui/icons";
import { FaRegUserCircle } from "react-icons/fa";
import { BiLogOut } from "react-icons/bi";
import { IoMdPricetags } from "react-icons/io";
import { IoSearch } from "react-icons/io5";
import { MdCheckCircle, MdNightlight } from "react-icons/md";
import { FaSun } from "react-icons/fa6";
import NullImage from "../../assets/BgImageNull.svg";
import { BsStars } from "react-icons/bs";
import { FaUser } from "react-icons/fa";
import { useUser } from "../../context/UserContext";
import axios from "axios";
import { IoIosMic } from "react-icons/io";
import { VscFileSubmodule } from "react-icons/vsc";
import { FaCircle } from "react-icons/fa";

import { GrDocumentWord, GrDocumentPdf, GrDocumentPpt } from "react-icons/gr";
import { AiOutlineFileUnknown } from "react-icons/ai";

const sampleFileNames = [
  {
    id: 1,
    name: "Bajaj.pptx",
  },
  {
    id: 2,
    name: "Hero.docx",
  },
  {
    id: 3,
    name: "Honda.pdf",
  },
  {
    id: 4,
    name: "Yamaha.pdf",
  },
  {
    id: 5,
    name: "Suzuki.pdf",
  },
  {
    id: 6,
    name: "TVS.pdf",
  },
  {
    id: 7,
    name: "Royal Enfield.pdf",
  },
  {
    id: 8,
    name: "KTM.pdf",
  },
  {
    id: 9,
    name: "Mahindra.pdf",
  },
  {
    id: 10,
    name: "Vespa.pdf",
  },
  {
    id: 11,
    name: "Ducati.pdf",
  },
  {
    id: 12,
    name: "BMW.pdf",
  },
  {
    id: 13,
    name: "Harley-Davidson.pdf",
  },
  {
    id: 14,
    name: "Aprilia.pdf",
  },
  {
    id: 15,
    name: "Triumph.pdf",
  },
  {
    id: 16,
    name: "Kawasaki.pdf",
  },
  {
    id: 17,
    name: "MV Agusta.pdf",
  },
  {
    id: 18,
    name: "Benelli.pdf",
  },
  {
    id: 19,
    name: "Piaggio.pdf",
  },
  {
    id: 20,
    name: "Moto Guzzi.pdf",
  },
];

const ChatSection = ({ currentChatData, darkMode, setDarkMode }) => {
  const { user } = useUser();
  const [message, setMessage] = useState("");
  const handleSubmit = async () => {
    if (!message.trim()) return;

    const url = "http://localhost:8000/chat";

    try {
      const response = await axios.post(
        url,
        {
          query: message,
        },
        {
          headers: {
            Authorization: `Bearer ${user?.access_token}`,
          },
        }
      );
      console.log("Response:", response.data);
      setMessage("");
    } catch (error) {
      console.error("Error:", error);
    }
  };

  const handleKeyPress = (event) => {
    if (event.key === "Enter") {
      handleSubmit();
    }
  };
  const {
    isOpen: isFilesViewOpen,
    onOpen: onFilesViewOpen,
    onClose: onFilesViewClose,
  } = useDisclosure();
  const btnFilesViewRef = useRef();

  const [filteredFiles, setFilteredFiles] = useState([]); //actual files to be used for query
  const [selectedFiles, setSelectedFiles] = useState([]); // files used for filtering in modal
  const [searchedFiles, setSearchedFiles] = useState([]);
  const [searchQuery, setSearchQuery] = useState("");

  useEffect(() => {
    if (searchQuery.trim() === "") {
      setSearchedFiles(sampleFileNames);
    } else {
      const files = sampleFileNames.filter((file) =>
        file.name.toLowerCase().includes(searchQuery.toLowerCase())
      );
      setSearchedFiles(files);
    }
  }, [searchQuery]);

  return (
    <div className="w-full h-full flex flex-col items-center justify-center">
      <div
        className={`py-3 transition-all duration-200 shadow-lg px-8 w-full flex justify-between items-center z-[250]
        ${darkMode ? "bg-gray-800 shadow-gray-950" : "bg-white shadow-gray-100"}
      `}
      >
        <div
          className={`text-2xl font-semibold ${
            darkMode ? "text-white" : "text-[#1B2559]"
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
                className={`flex items-center justify-center gap-2 rounded-2xl px-3 py-2 ${
                  darkMode
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
        className={`h-full transition-all duration-200 w-full py-4 px-20 ${
          darkMode ? "bg-gray-900" : "bg-gray-100"
        }`}
      >
        <div className="w-full h-full flex flex-col gap-2 items-start justify-center relative">
          <div className="w-[80%] flex py-2 items-center justify-center">
            {filteredFiles.length > 0 && (
              <div className="text-xs w-20 text-gray-400">Using Files</div>
            )}
            <div className="py-1 w-full flex gap-2 overflow-x-auto">
              {filteredFiles.map((file, index) => (
                <div
                  key={index}
                  className="flex items-center gap-2 px-2 py-1 bg-white text-sm rounded-2xl"
                >
                  <FaCircle className="text-green-500" />
                  <div className="text-xs">{file.name}</div>
                </div>
              ))}
            </div>
          </div>
          <button
            className="absolute text-gray-500 hover:text-gray-700 transition-all duration-200 flex items-center justify-center cursor-pointer hover:bg-gray-100 w-32 gap-2 top-0 right-0 px-3 py-2 bg-white rounded-2xl"
            style={{
              boxShadow: "0 0 2px 2px #11111115",
            }}
            ref={btnFilesViewRef}
            onClick={() => {
              onFilesViewOpen();
            }}
          >
            <div className="text-sm">View Files</div>
            <VscFileSubmodule />
          </button>
          {currentChatData ? (
            <div className="w-full py-2 h-full flex flex-col items-center justify-end overflow-y-auto">
              {currentChatData.messages.map((message, index) => (
                <div
                  key={index}
                  className={`flex items-center gap-4 w-full ${
                    message.sender === "user" ? "justify-end" : "justify-start"
                  }`}
                >
                  <div
                    className={`flex items-center gap-2 ${
                      message.sender === "user"
                        ? "flex-row-reverse"
                        : "flex-row"
                    }`}
                  >
                    <div
                      className={`${
                        darkMode ? "text-white" : "text-[#1B2559]"
                      } transition-all duration-200`}
                    >
                      {message.sender === "user" ? <FaUser /> : <BsStars />}
                    </div>
                    <div
                      className={`text-sm transition-all duration-200 rounded-2xl px-4 py-2 ${
                        message.sender === "user"
                          ? "bg-[#1B2559] text-white"
                          : `text-[#1B2559] ${
                              darkMode ? "bg-gray-100" : "bg-white"
                            }`
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
            <div className="bg-white h-full w-full gap-2 flex justify-center items-center px-4 rounded-2xl">
              <input
                type="text"
                placeholder="Send a message..."
                className="border-none ring-none outline-none text-sm h-full w-full"
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                onKeyPress={handleKeyPress}
              />
              <div className="p-2 rounded-full transition-all duration-200 hover:bg-gray-100 text-gray-300 hover:text-gray-600 cursor-pointer">
                <IoIosMic className="text-lg" />
              </div>
            </div>
            <button
              className="bg-[#1B2559] h-full hover:bg-opacity-80 text-white flex items-center justify-center gap-3 rounded-2xl px-6"
              onClick={handleSubmit}
            >
              <IoSearch />
              <div className="text-sm font-semibold">Search</div>
            </button>
          </div>
          <div className="w-full h-8 flex text-xs text-gray-400 justify-between items-center">
            <div>© 2023 Unenthusiasts.</div>
            <div className="flex items-center justify-center gap-2">
              <div>License</div>
              <div>Terms of Use</div>
              <div>Privacy Policy</div>
            </div>
          </div>
        </div>
      </div>
      <Drawer
        isOpen={isFilesViewOpen}
        placement="right"
        onClose={onFilesViewClose}
        finalFocusRef={btnFilesViewRef}
        zIndex={10000}
      >
        <DrawerOverlay />
        <DrawerContent>
          <DrawerCloseButton />
          <DrawerHeader>View Files</DrawerHeader>

          <DrawerBody>
            <div className="w-full h-full">
              <Input
                placeholder="Type here..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                fontSize={14}
              />
              <div className="flex flex-col w-full h-full">
                {searchedFiles.map((file, index) => (
                  <div
                    key={index}
                    className="flex items-center justify-between w-full gap-4 py-2"
                  >
                    <div
                      className="flex items-center cursor-pointer py-2 rounded-xl hover:bg-gray-50 w-full px-4 gap-2"
                      onClick={() => {
                        if (selectedFiles.includes(file.id)) {
                          setSelectedFiles((prev) =>
                            prev.filter((id) => id !== file.id)
                          );
                        } else {
                          setSelectedFiles((prev) => [...prev, file.id]);
                        }
                      }}
                    >
                      {file.name.includes(".pdf") && (
                        <GrDocumentPdf className="text-gray-700" />
                      )}
                      {file.name.includes(".docx") && (
                        <GrDocumentWord className="text-gray-700" />
                      )}
                      {file.name.includes(".pptx") && (
                        <GrDocumentPpt className="text-gray-700" />
                      )}
                      {!file.name.includes(".pdf") &&
                        !file.name.includes(".doc") &&
                        !file.name.includes(".ppt") && (
                          <AiOutlineFileUnknown className="text-gray-700" />
                        )}
                      <div
                        className="flex w-full items-end"
                        onClick={() => {
                          if (selectedFiles.includes(file.id)) {
                            setSelectedFiles((prev) =>
                              prev.filter((id) => id !== file.id)
                            );
                          } else {
                            setSelectedFiles((prev) => [...prev, file.id]);
                          }
                        }}
                      >
                        <div className="text-gray-700 pr-4 text-sm">
                          {file.name.split(".")[0]}
                        </div>
                        <div className="text-gray-400 text-xs">
                          .{file.name.split(".")[1]}
                        </div>
                      </div>
                      <Checkbox
                        colorScheme={
                          selectedFiles.includes(file.id) ? "blue" : "gray"
                        }
                        isChecked={selectedFiles.includes(file.id)}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </DrawerBody>
          <DrawerFooter>
            <div className="flex w-full justify-end gap-3 items-center">
              <Button variant="outline">Upload File</Button>
              <Button
                colorScheme="blue"
                onClick={() => {
                  setFilteredFiles(
                    sampleFileNames.filter((file) =>
                      selectedFiles.includes(file.id)
                    )
                  );
                  onFilesViewClose();
                }}
              >
                Save
              </Button>
            </div>
          </DrawerFooter>
        </DrawerContent>
      </Drawer>
    </div>
  );
};

export default ChatSection;
