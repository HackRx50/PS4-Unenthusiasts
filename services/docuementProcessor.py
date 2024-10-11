from services.messageQueue import MessageQueueService
from services.docuemntStorage import S3Storage
import uuid
import tempfile
from fastapi import HTTPException

class DocumentProcessor:
    def __init__(self,kb):
        self.messageQueue=MessageQueueService("DocuementProcessor","localhost");
        self.s3=S3Storage("hackrx")
        self.knowledgeBase=kb

    def start(self):
        self.messageQueue.consume_message(callback=self.process_message)

    def process_message(self, body,properties):
        try:
            docuemnt_id=body["document_id"]
            print(f"Received message: {body}")
            # retreive docuement from s3
            exists=self.s3.check_file_exists(docuemnt_id)
            if not exists:
                print(f"Docuement {docuemnt_id} does not exist")
                return

            metadata=self.s3.get_file_metadata(docuemnt_id)
            self.s3.download_file(docuemnt_id,docuemnt_id)
            filename=metadata["name"]
            self.knowledgeBase.upload_file_to_knowledge_base(filename,docuemnt_id)
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            return
        



        # process docuement
        
    def upload_document(self,file):
        try:
            docuemntId=str(uuid.uuid4())
            with tempfile.NamedTemporaryFile(delete=False) as temp:
                temp.write(file.read())
                temp.seek(0)
                self.s3.upload_file(temp.name,docuemntId)

            message={"document_id":docuemntId}
            self.messageQueue.publish_message(message,docuemntId)
            return {"message": "File uploaded successfully", "details": message}
        except Exception as e:
            raise HTTPException (status_code=400, detail=f"An error occurred: {str(e)}")
        








        