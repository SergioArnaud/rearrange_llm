import openai
import os
import hydra
from omegaconf import DictConfig
import copy

class OpenAI():
    def __init__(self, conf):
        self.llm_conf = conf.llm
        self.client = openai.Completion()
        self._validate_conf()

    def _validate_conf(self):
        try: 
            openai.api_key = os.getenv('OPENAI_API_KEY')
        except: 
            raise ValueError('No API keys provided')
        if self.llm_conf.stream:
            raise ValueError('Streaming not supported')
        if self.llm_conf.n > 1 and self.llm_conf.stream:
            raise ValueError('Cannot stream results with n > 1')
        if self.llm_conf.best_of > 1 and self.llm_conf.stream:
            raise ValueError('Cannot stream results with best_of > 1')
        
    def generate(self, prompt):
        params = copy.deepcopy(self.llm_conf)
        params['prompt'] = prompt
        return self.client.create(**params)

class RearrangeEasyChain():
    def __init__(self, conf):
        self.conf = conf
        self._build_prompt()
        self.llm = OpenAI(conf)
        self.input_variable = f'<{self.conf.prompt.input_variable}>'
    
    def _build_prompt(self):
        self.prompt = self.conf.prompt.main_prompt
        if 'examples' in self.conf.prompt:
            self.prompt += f'\n{self.conf.prompt.examples}'
        if 'suffix' in self.conf.prompt:
            self.prompt += f'\n{self.conf.prompt.suffix}'
    
    def generate(self, input):
        prompt = self.prompt.replace(self.input_variable, input)
        return self.llm.generate(prompt).choices[0].text


@hydra.main(version_base='1.1', config_name='config', config_path='conf')
def main(conf: DictConfig):
    chain = RearrangeEasyChain(conf)
    instruction = conf.instruction
    ans = chain.generate(instruction)
    print(ans)

if __name__ == '__main__':
    main()