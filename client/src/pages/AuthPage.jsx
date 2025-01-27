import React, { useState } from "react";
import {
  Card,
  CardBody,
  Image,
  Stack,
  Button,
  Tabs,
  TabList,
  Tab,
  TabPanels,
  TabPanel,
  InputGroup,
  InputLeftElement,
  Input,
  InputRightElement,
  CardFooter,
} from "@chakra-ui/react";
import { FaPhoneAlt, FaRegUser } from "react-icons/fa";
import { RiLockPasswordLine } from "react-icons/ri";
import { MdAlternateEmail } from "react-icons/md";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import { useUser } from "../context/UserContext";
import toast, { Toaster } from "react-hot-toast";

const AuthPage = ({ setLoading }) => {
  const { login } = useUser();
  const [showPassWord, setShowPassWord] = useState(false);
  const handleClickShowPassWord = () => setShowPassWord(!showPassWord);
  const [showRePassWord, setShowRePassWord] = useState(false);
  const handleClickShowRePassWord = () => setShowRePassWord(!showRePassWord);
  const navigate = useNavigate();
  const [activeTab, setactiveTab] = useState(1);

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [username, setUsername] = useState("");
  const [phone, setPhone] = useState("");

  const handleSubmit = async () => {
    setLoading(true);
    const baseURL = "http://127.0.0.1:8000";
    const url = `${baseURL}/${activeTab === 0 ? "login" : "register"}`;
    const data =
      activeTab === 0
        ? { email, password }
        : { username, email, password, phone };

    try {
      const response = await axios.post(url, data);
      toast("Success", {
        style: {
          border: "1px solid #10B981",
          padding: "16px",
          color: "#10B981",
        },
      });
      login(response.data);
      navigate("/home");
    } catch (error) {
      toast("Error", {
        style: {
          border: "1px solid #EF4444",
          padding: "16px",
          color: "#EF4444",
        },
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="w-full h-full flex flex-col items-center justify-center">
      <div className="py-3 transition-all duration-200 px-8 w-full flex justify-center items-center z-[5000] bg-white">
        <div className="transition-all duration-200 uppercase text-xl flex items-center justify-center text-[#1B2559]">
          <div className="font-bold">Vector</div>
          <div className="">AI</div>
        </div>
      </div>
      <div className="w-full px-10 bg-gray-200 h-full flex items-center justify-center">
        <Card
          direction={{ base: "column", sm: "row" }}
          overflow="hidden"
          variant="outline"
        >
          <Image
            objectFit="fit"
            h={"27rem"}
            src="https://static.vecteezy.com/system/resources/previews/022/729/745/original/smart-chat-bot-with-artificial-intelligence-technology-free-vector.jpg"
            alt="Caffe Latte"
          />
          <Stack w={"100%"}>
            <CardBody>
              <Tabs isFitted isLazy defaultIndex={1} w={"100%"}>
                <TabList>
                  <Tab onClick={() => setactiveTab(0)}>Login</Tab>
                  <Tab onClick={() => setactiveTab(1)}>Register</Tab>
                </TabList>
                <TabPanels>
                  <TabPanel>
                    <div className="w-full h-full flex flex-col gap-3 items-center justify-center">
                      <InputGroup>
                        <InputLeftElement pointerEvents="none">
                          <MdAlternateEmail className="text-gray-400" />
                        </InputLeftElement>
                        <Input
                          type="text"
                          placeholder="Enter email"
                          value={email}
                          onChange={(e) => setEmail(e.target.value)}
                        />
                      </InputGroup>
                      <InputGroup size="md">
                        <InputLeftElement pointerEvents="none">
                          <RiLockPasswordLine className="text-gray-400" />
                        </InputLeftElement>
                        <Input
                          pr="4.5rem"
                          type={showPassWord ? "text" : "password"}
                          placeholder="Enter password"
                          value={password}
                          onChange={(e) => setPassword(e.target.value)}
                        />
                        <InputRightElement width="4.5rem">
                          <Button
                            h="1.75rem"
                            size="sm"
                            onClick={handleClickShowPassWord}
                          >
                            {showPassWord ? "Hide" : "Show"}
                          </Button>
                        </InputRightElement>
                      </InputGroup>
                    </div>
                  </TabPanel>
                  <TabPanel>
                    <div className="w-full h-full flex flex-col gap-3 items-center justify-center">
                      <InputGroup>
                        <InputLeftElement pointerEvents="none">
                          <FaRegUser className="text-gray-400" />
                        </InputLeftElement>
                        <Input
                          type="text"
                          placeholder="Enter username"
                          value={username}
                          onChange={(e) => setUsername(e.target.value)}
                        />
                      </InputGroup>
                      <InputGroup>
                        <InputLeftElement pointerEvents="none">
                          <MdAlternateEmail className="text-gray-400" />
                        </InputLeftElement>
                        <Input
                          type="text"
                          placeholder="Enter email"
                          value={email}
                          onChange={(e) => setEmail(e.target.value)}
                        />
                      </InputGroup>
                      <InputGroup>
                        <InputLeftElement>
                          <FaPhoneAlt className="text-gray-400" />
                        </InputLeftElement>
                        <Input
                          type="tel"
                          placeholder="phone number"
                          value={phone}
                          onChange={(e) => setPhone(e.target.value)}
                        />
                      </InputGroup>
                      <InputGroup size="md">
                        <InputLeftElement pointerEvents="none">
                          <RiLockPasswordLine className="text-gray-400" />
                        </InputLeftElement>
                        <Input
                          pr="4.5rem"
                          type={showPassWord ? "text" : "password"}
                          placeholder="Enter password"
                          value={password}
                          onChange={(e) => setPassword(e.target.value)}
                        />
                        <InputRightElement width="4.5rem">
                          <Button
                            h="1.75rem"
                            size="sm"
                            onClick={handleClickShowPassWord}
                          >
                            {showPassWord ? "Hide" : "Show"}
                          </Button>
                        </InputRightElement>
                      </InputGroup>
                    </div>
                  </TabPanel>
                </TabPanels>
              </Tabs>
            </CardBody>
            <CardFooter className="flex justify-center">
              <Button w={"100%"} colorScheme="blue" onClick={handleSubmit}>
                Submit
              </Button>
            </CardFooter>
          </Stack>
        </Card>
      </div>
      <Toaster />
    </div>
  );
};

export default AuthPage;
