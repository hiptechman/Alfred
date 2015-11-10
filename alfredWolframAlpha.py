import wolframalpha

class WolframAlpha(object):
    def __init__(self):
        self.client = wolframalpha.Client('EWXH7L-THV8PX7UQG')

    def wolframAlphaQuery(self, query): # Function adapted from baljeetsinghipu in Rasberry Pi forums http://goo.gl/pSmNMW
        res = self.client.query(query)
        if len(res.pods) > 0:
            texts = ""
            pod = res.pods[1]
            if pod.text:
                texts = pod.text
            else:
                texts = pronounce("I have no answer for that")
            # to skip ascii character in case of error
            result = texts.encode('ascii', 'ignore')
            return str(result)
        else:
            return "Sorry, I am not sure."
    