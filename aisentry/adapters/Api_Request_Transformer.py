from abc import ABC, abstractmethod

class ApiRequestTransformer(ABC):
    @abstractmethod
    def transform_path(self, path):
        pass

    @abstractmethod
    def transform_method(self, method):
        pass

    @abstractmethod
    def transform_body(self, body):
        pass

    @abstractmethod
    def transform_query_string(self, query_string):
        pass

    @abstractmethod
    def transform_headers(self, headers):
        pass

    # @abstractmethod
    # def perform_transformations(self, path, method, body, query_string, headers):
    #     pass