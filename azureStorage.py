from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
import os
from dotenv import load_dotenv
from deepface import DeepFace
from io import BytesIO
from PIL import Image
from pathlib import Path

#each account needs to have a specific ID --> this will reference they're own contain on Azure
# where own images are stored
#create new container on new account!!

#idea --> store as key value pair mapping embedding to azure blob URL
#this way first do vector similarity search --> then do detect faces search out of those results -_> save time???
#also test how well/fast operations take using the testingSet file
load_dotenv()

conn_str = os.environ["AZURE_BLOB_CONN_STR"]
blob_service_client = BlobServiceClient.from_connection_string(conn_str)

def createContainer(container_name):
    try:
        # Create a new BlobContainerClient
        container_client = blob_service_client.get_container_client(container_name)

        # Create the container
        container_client.create_container()
    except:
        print("name is taken or error in createContainer function")       
        
    

#upload an image to blob storage account taking in container and image
def uploadImage(container_name, path):
    try:
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=os.path.basename(path))
        with open(path, "rb") as data:
                blob_client.upload_blob(data)
    except:
        print("error in uploadImage function")

#compare face with every face in container until we get a true result
def compareFaces(container_name, img_path):
    try:
        output = False
        container_client = blob_service_client.get_container_client(container_name)
        #iterate through every blob
        for blob in container_client.list_blobs():
            blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob.name)
            #make new directory
            if not os.path.exists("temp"):
                os.makedirs("temp")
            # Download blob to a local directory
            local_file_path = f"temp/{blob.name}"
            with open(local_file_path, "wb") as file:
                blob_client.download_blob().readinto(file)
            #do comparison
            result = DeepFace.verify(img1_path = img_path, img2_path = local_file_path, model_name= "Facenet512")
            os.remove(local_file_path)
            if result["verified"] == True:
                output = True
                break
    except:
        print("error in compareFaces function") 
    return output

directory = Path('pictures')

# Loop through each file in the directory
# for filepath in directory.iterdir():
#     try:
#         uploadImage("test", filepath)
#     except:
#         continue
#print(compareFaces("test", "pictures/jack2.png"))
#createContainer("pct")
