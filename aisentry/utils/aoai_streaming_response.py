class AOAI_Streaming_Response:
    def __init__(self, response):
        self.choices = response['choices']
        self.created = response['created']
        self.id = response['id']
        self.model = response['model']
        self.object = response['object']
        self.system_fingerprint = response['system_fingerprint']
