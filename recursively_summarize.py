import openai
import textwrap
import re
import time

def set_openai_api_key(api_key):
    openai.api_key = api_key

def open_file(filepath):
    with open(filepath, 'r', encoding='latin-1') as infile:
        return infile.read().strip()

def save_file(content, filepath):
    with open(filepath, 'w', encoding='latin-1') as outfile:
        outfile.write(content)

def gpt3_completion(prompt, engine='gpt-3.5-turbo-instruct', temp=0.6, top_p=1.0, tokens=2000, freq_pen=0.25, pres_pen=0.0, stop=['<<END>>']):
    max_retry = 1
    retry = 0
    while True:
        try:
            response = openai.Completion.create(
                engine=engine,
                prompt=prompt,
                temperature=temp,
                max_tokens=tokens,
                top_p=top_p,
                frequency_penalty=freq_pen,
                presence_penalty=pres_pen,
                stop=stop)
            text = response['choices'][0]['text'].strip()
            text = re.sub('\s+', ' ', text)
            filename = '%s_gpt3.txt'
            with open('gpt3_logs/%s' % filename, 'w') as outfile:
                outfile.write('PROMPT:\n\n' + prompt + '\n\n==========\n\nRESPONSE:\n\n' + text)
            return text
        except Exception as oops:
            retry += 1
            if retry >= max_retry:
                return "GPT3 error: %s" % oops
            # print('Error communicating with OpenAI:', oops)
            time.sleep(20)

if __name__ == '__main__':
    # Set your API key
    api_key = open_file('openaiapikey.txt')
    set_openai_api_key(api_key)

    alltext = open_file('research2.txt')
    chunks = textwrap.wrap(alltext, 2000)
    result = list()
    count = 0
    for chunk in chunks:
        count = count + 1
        prompt = open_file('prompt.txt').replace('<<SUMMARY>>', chunk)
        prompt = prompt.encode(encoding='ASCII',errors='ignore').decode()
        summary = gpt3_completion(prompt)
        print('\n\n\n', count, 'of', len(chunks), ' - ', summary)
        result.append(summary)
    save_file('\n\n'.join(result), 'output1.txt')
