from google.cloud import storage

class CloudStorageBucket:
    def __init__(self, project_id, bucket_name):
        self.storage_client = storage.Client(project=project_id)
        self.bucket = self.storage_client.bucket(bucket_name)

    def check_bucket_contents(self):
        """
        Retrieves the contents of a bucket by returning a list of names

        Returns:
            List(str): A list of file names
        """

        blobs = self.bucket.list_blobs()
        blob_names = []
        for blob in blobs:
            # Only use the files in the prompts folder and need to be .txt
            if not "prompts/" in blob.name or not ".txt" in blob.name:
                continue

            name = blob.name.replace("prompts/", "").replace(".txt", "")
            blob_names.append(name)
        
        return blob_names

        

    def retrieve_file_as_string(self, blob_name):
        """
        Retrieves file from bucket using Blob name

        Args:
            blob_name (str): Name of the blob to retrieve

        Returns:
            Str: String contents of the blob
        """
        blob = self.bucket.blob(blob_name)
        return blob.download_as_string().decode("utf-8")

    def upload_file_from_string(self, input_bytes, content_type, destination_blob_name):
        """
        Uploads a file to the bucket as a string.

        Args:
            input_bytes (Bytes): Bytes that can be translated to the file.
            content_type (Str): The content type of the file
            destination_blob_name (Str): The name of the destination blob
        
        Returns:
            str: URL of the created Blob
            
        """
        blob = self.bucket.blob(destination_blob_name)
        blob.upload_from_string(input_bytes, content_type=content_type)
        print("Uploaded data to Cloud Storage bucket.")

        blob.make_public()
        return blob.public_url

