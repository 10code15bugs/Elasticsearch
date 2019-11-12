import requests

PROXY_POOL_URL = 'http://127.0.0.1:5555/random'
class GetIPP(object):

    def get_random_ip(self):
        try:
            response = requests.get(PROXY_POOL_URL)
            if response.status_code == 200:
                proxy = response.text
                print("HPPT://"+proxy)
                return "HPPT://"+proxy
                
        except ConnectionError:
            print('错误')
            return self.get_random_ip()





if __name__ == "__main__":

    get_ip = GetIPP()
    get_ip.get_random_ip()
