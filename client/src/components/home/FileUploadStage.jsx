import React from "react";
import { IoCloudUploadOutline } from "react-icons/io5";
import { FaFileCsv } from "react-icons/fa";
import { RxCross1 } from "react-icons/rx";

const FileUploadStage = ({ file, setFile }) => {
  const handleFileDrop = (e) => {
    e.preventDefault();
    setFile(e.dataTransfer.files[0]);
  };

  const handleFileSelection = (e) => setFile(e.target.files[0]);

  return (
    <div className="w-full h-64 bg-[#38bdf820] rounded-2xl flex flex-col items-center justify-between gap-5">
      {!file ? (
        <div
          className="w-full h-full rounded-2xl cursor-pointer flex flex-col items-center justify-center gap-3"
          style={{ border: "2px dashed #38bdf8" }}
          onDragOver={(e) => e.preventDefault()}
          onDrop={handleFileDrop}
          onClick={() => document.getElementById("file").click()}
        >
          <IoCloudUploadOutline className="text-5xl text-[#38bdf8]" />
          <div className="flex flex-col  text-xs items-center">
            <div className="text-black font-semibold">
              Drag and drop file here
            </div>
            <div>or</div>
            <div className="font-bold hover:underline">Browse files</div>
          </div>
        </div>
      ) : (
        <div
          className="h-full w-full relative rounded-2xl cursor-pointer flex flex-col items-center justify-center gap-3"
          style={{ border: "2px dashed #38bdf8" }}
        >
          <div className="h-full w-full flex gap-2 flex-col items-center justify-center">
            <FaFileCsv className="text-5xl text-[#38bdf8]" />
            <div className="font-bold text-[#38bdf8]">{file.name}</div>
          </div>
          <div
            className="bg-[#38bdf830] absolute top-5 right-5 flex items-center justify-center rounded-2xl p-2"
            onClick={() => setFile(null)}
          >
            <RxCross1 />
          </div>
        </div>
      )}
      <input
        id="file"
        type="file"
        onChange={handleFileSelection}
        className="hidden"
      />
    </div>
  );
};

export default FileUploadStage;
