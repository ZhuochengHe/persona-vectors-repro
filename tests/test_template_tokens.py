"""Chat-template return type regression, no model weights or network."""
import pytest
from persona_repro.model import ModelRuntime,template_token_ids
from persona_repro.model import generation_stop_ids, response_content_ids
from types import SimpleNamespace

@pytest.mark.parametrize('value',[[10,11],{'input_ids':[10,11],'attention_mask':[1,1]}, {'input_ids':[[10,11]]}])
def test_template_result_normalization(value):
    assert template_token_ids(value)==[10,11]

@pytest.mark.parametrize('value',[['input_ids','attention_mask'],[[1,2],[3,4]],[],{'input_ids':[]}])
def test_bad_template_result_is_rejected(value):
    with pytest.raises(ValueError):template_token_ids(value)

def test_new_mapping_return_is_normalized_for_prompt_and_answer():
    class Tokenizer:
        def apply_chat_template(self,messages,**kwargs):
            assert kwargs['return_dict'] is False
            ids=[10,11] if kwargs['add_generation_prompt'] else [10,11,20,21]
            return {'input_ids':ids,'attention_mask':[1]*len(ids)}
    runtime=ModelRuntime('fake');runtime.tokenizer=Tokenizer()
    encoded=runtime.encode_conversation([{'role':'user','content':'q'}],answer='a')
    assert encoded=={'input_ids':[10,11,20,21],'attention_mask':[1,1,1,1],'response_start':2}


def test_turn_end_and_model_eos_are_both_stops():
    tokenizer=SimpleNamespace(eos_token_id=66)
    model=SimpleNamespace(generation_config=SimpleNamespace(eos_token_id=99),
                          config=SimpleNamespace(text_config=SimpleNamespace(eos_token_id=[99,100])))
    assert generation_stop_ids(tokenizer,model)==[66,99,100]


@pytest.mark.parametrize('tokens,expected',[
    ([3,4,66,198,99],[3,4]), ([3,99,4],[3]), ([3,4],[3,4]), ([66,198],[]), ([],[])])
def test_response_stops_before_first_terminator_even_with_newline(tokens,expected):
    assert response_content_ids(tokens,[66,99])==expected


def test_actual_activation_mask_excludes_end_marker_and_continuation():
    import torch
    class Model(torch.nn.Module):
        device='cpu'
        generation_config=SimpleNamespace(eos_token_id=99)
        def __init__(self):
            super().__init__();self.layers=torch.nn.ModuleList([torch.nn.Identity() for _ in range(32)])
        def forward(self,input_ids,**kwargs):
            values=input_ids.float().unsqueeze(-1).expand(-1,-1,4)
            for block in self.layers:values=block(values)
    runtime=ModelRuntime('fake');runtime.model=Model();runtime.layers=runtime.model.layers
    runtime.tokenizer=SimpleNamespace(eos_token_id=66)
    captured=runtime.activations([],prompt_token_ids=[1,2],answer_token_ids=[3,4,66,198,99,500])
    assert torch.equal(captured[19]['response_avg'],torch.full((4,),3.5))
    runtime.encode_conversation=lambda *args:{'input_ids':[1,2,3,4,66,198],'response_start':2}
    assert torch.equal(runtime.activations([],answer='a')[19]['response_avg'],torch.full((4,),3.5))
    with pytest.raises(ValueError,match='Empty prompt or response'):
        runtime.activations([],prompt_token_ids=[1,2],answer_token_ids=[66,198])
