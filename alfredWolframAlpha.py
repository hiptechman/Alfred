import wolframalpha

class WolframAlpha(object):
    def __init__(self):
        apiKeyFile = open('WolframAlphaKey.txt', 'r')
        apiKey = apiKeyFile.read()
        self.client = wolframalpha.Client('apiKey')

    # Function adapted from baljeetsinghipu in Rasberry Pi forums http://goo.gl/pSmNMW
    def wolframAlphaQuery(self, query): 
        answer = self.client.query(query)
        if len(answer.pods) > 0:
            texts = ""
            pod = answer.pods[1]
            if pod.text:
                texts = pod.text
            else:
                texts = pronounce("I have no answer for that")
            # Skip ascii character in case of error
            answer = texts.encode('ascii', 'ignore')
            return str(answer)
        else:
            return "Sorry, I am not sure."