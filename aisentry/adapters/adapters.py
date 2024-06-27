from enum import Enum
from httpx import Request
from adapters.SampleAdapter.sample_api_request_transformer import SampleApiRequestTransformer


class AdapterEnum(Enum):
    SampleApiRequestTransformer = 'SampleApiRequestTransformer'
    Adapter2 = 'Adapter2'
    Adapter3 = 'Adapter3'

def return_adapter(request: Request, adapter):
    adapter_enum = adapter
    if adapter_enum == AdapterEnum.SampleApiRequestTransformer.value:
        return SampleApiRequestTransformer(request)
    # elif adapter_enum == AdapterEnum.Adapter2.value:
    #     return Adapter2()
    # elif adapter_enum == AdapterEnum.Adapter3.value:
    #     return Adapter3()
    else:
        raise ValueError(f"Invalid adapter enum: {adapter_enum}")