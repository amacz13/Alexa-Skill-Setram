from bs4 import BeautifulSoup
import requests
import re

'''
url = "https://dev.actigraph.fr/actipages/setram/pivkdev/relais.html.php?"
headers = {'content-type': 'application/x-www-form-urlencoded'}
data = {"refs":"271647753|271648006|271649809|271650065|271651088|271653377|271653649|271658512|271658769|271659023|271659281|271659786|271660303|271660559", "ran":"528381604", "a":"refresh"}

r = requests.post(url, headers = headers, data = data)
#print(r.text)

soup = BeautifulSoup(r.text,features="html.parser")
print(soup.find("li", {"id": "h0"}).get_text())
'''

class Timeo:
    """ Interface entre Python et le service Timéo de la SETRAM """

    def __init__(self, URL="http://dev.actigraph.fr/actipages/setram/module/mobile/pivk/relais.html.php"):

        self.URL = URL

        self.session = requests.Session()

        # session init
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/29.0.1547.57 Safari/537.36',
            'Content-type': 'application/x-www-form-urlencoded'})
        self.session.get(URL)

        # regexs
        self.extr_name_code = re.compile("([^\(]+) \((\d+)\)")
        self.extr_code = re.compile("\((\d+)\)")


    def getall_arrets(self, lignesens, attr_to_extract="name"):
        """ Récupére les informations sur tous les arrêts d'une même ligne dans
        un sens de circulation donné (A ou R, voir API SETRAM... ahem.).
        lignesens : ligne à parser et sens de circulation (ex: 8_R , T1_A, ...)
        attr_to_extract : paramètre à extraire (par défaut : nom de l'arrêt)
        """

        POST_params_liste = {
           'a': 'recherche_ligne',
           'ligne_sens': '4_R'
        }

        result = self.session.post("https://dev.actigraph.fr/actipages/setram/pivkdev/relais.html.php?", POST_params_liste)
        options = BeautifulSoup(result.text,features="html.parser").find_all('option')

        arrets = dict()

        for p in options:
            print(p.getText())
            print(p.get("value"))

        if attr_to_extract == "name":
            return dict([self.extr_name_code.search(_.text).group(1,2)[::-1] for _ in options])
        else:
            return {self.extr_code.search(_.text).group(1):_.get(attr_to_extract) for _ in options}


    def get_lignes(self):
        """ Récupère une hashtable entre les lignes (et leur direction) et le code de ligne correspondant """

        return {
            _.text:_.get('value') for _ in
            BeautifulSoup(self.session.get(self.URL).text,features="html.parser").find_all('option')
            if _.text.find('>') > -1
        }

    def get_arret(self, lignesens, code):
        """ Récupère les prochains passages à un arret donné
        lignesens : code de ligne (ligne+sens, voir get_ligne())
        code : code timéo de l'arret
        """

        """ Récupère les prochains passage à l'arrêt demandé """

        ligne,sens = lignesens.split('_')
        code = str(code)

        # get references
        refs_all = self.getall_arrets(lignesens, attr_to_extract='value')

        POST_params = {
            'a':'recherche_arrets',
            'refs': refs_all[code].split('_')[0],
            'code': code,
            'sens': sens,
            'ligne':ligne,
            'list_refs' : refs_all[code]+'_'+code
        }

        # first, get the ran param
        res = self.session.post(self.URL, data=POST_params)
        ran = re.search("ran=(\d+)", BeautifulSoup(res.text).find_all('script')[-1].text.splitlines()[-2]).group(1)

        POST_params2 = {
            'a' : 'refresh',
            'refs': POST_params['refs'],
            'ran' : ran
        }

        # then, get the page with real data
        res = self.session.post(self.URL, data=POST_params2)
        stops = [_.text for _ in BeautifulSoup(res.text).find_all('li')[1:]]

        stoptimes = []

        for i in stops:
            if i.find('imminent') > -1 or i.find('en cours') > -1: stoptimes.append("maintenant")
            else:
                next = re.search("(\d+ minutes?)", i)
                if not next:
                    next = re.search("(\d+ H \d+)", i)

                stoptimes.append(next.group(1))

        return stoptimes

if __name__=='__main__':

    t = Timeo()

    print("Liste des lignes et des codes associés :")
    liste = t.get_lignes()
    for k,v in liste.items():
        print(k+' -> '+v)

    print("\n")
    print("Liste des arrêts et de leur code pour la ligne T1_R :")
    arrets = t.getall_arrets('4_R')
    for k,v in arrets.items():
        print(k+' -> '+v)

    print("\n")
    print("Temps avant l'arrivé du prochain tram pour les arrêts de T1_R :")
    for k,v in arrets.items():
        print("Arrivé à l'arret "+v+" : "+t.get_arret('T1_R', k)[0])