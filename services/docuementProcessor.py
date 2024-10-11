from services.messageQueue import MessageQueueService
from services.docuemntStorage import S3Storage
import uuid
import tempfile
from fastapi import HTTPException
from services.knowledgeBase import KnowledgeBaseService
from fastapi import UploadFile

class DocumentProcessor:
    def __init__(self):
        self.messageQueue=MessageQueueService("DocuementProcessor","localhost");
        self.s3=S3Storage("hackrx")
        self.knowledgeBase=KnowledgeBaseService("knowledgebase")

    def start_consuming(self):
        self.messageQueue.consume_message(callback=self.process_message)

    def process_message(self, ch, method, properties, body):
        try:
            
            docuemnt_id=properties.message_id
            filename=body
            print(f"Received message: {body}")
            # retreive docuement from s3
            exists=self.s3.check_file_exists(docuemnt_id)
            if not exists:
                print(f"Docuement {docuemnt_id} does not exist")
                return

            metadata=self.s3.get_file_metadata(docuemnt_id)
            name=metadata.get("name")
            fileext=name.split('.')[-1]

            currFilename=docuemnt_id+"."+fileext
            self.s3.download_file(docuemnt_id,currFilename)
            result=self.knowledgeBase.upload_file_to_knowledge_base(filename=currFilename,document_id=docuemnt_id,actual_filename=name)
            print("RESULT",result)
            ch.basic_ack(delivery_tag=method.delivery_tag) 

        except Exception as e:
            print(f"An error occurred: {str(e)}")
            return
        



        # process docuement
        
    async def upload_document(self,file:UploadFile):
        try:
            docuemntId=str(uuid.uuid4())
            # print(message,"DONE")
            file_extension = f".{file.filename.split('.')[-1]}"
            temp_file_path=None
            content = await file.read()
            with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
                temp_file.write(content)
                temp_file_path = temp_file.name
                self.s3.upload_file(temp_file_path,docuemntId,{
                    "name":file.filename,
                    "documnetId":docuemntId,
                    "documnet_id":docuemntId

                })
            

            

            message=file.filename
            
            self.messageQueue.publish_message(message,docuemntId)
            return {"message": "File uploaded successfully", "details": message}
        except Exception as e:
            # print(e.with_traceback())
            raise HTTPException (status_code=400, detail=f"An error occurred: {str(e)}")
        








        