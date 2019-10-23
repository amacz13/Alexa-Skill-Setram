from bs4 import BeautifulSoup
import requests
import re

def getStopsForLine(line):
        """ Récupére les informations sur tous les arrêts d'une même ligne dans
        un sens de circulation donné (A ou R, voir API SETRAM... ahem.).
        lignesens : ligne à parser et sens de circulation (ex: 8_R , T1_A, ...)
        """
        POST_params_liste = {
           'a': 'recherche_ligne',
           'ligne_sens': line
        }
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/29.0.1547.57 Safari/537.36',
            'Content-type': 'application/x-www-form-urlencoded'})
        result = session.post("https://dev.actigraph.fr/actipages/setram/pivkdev/relais.html.php", POST_params_liste)
        options = BeautifulSoup(result.text,features="html.parser").find_all('option')
        arret = dict()
        for p in options:
            #print(p.getText())
            #print(p.get("value"))
            arret[p.getText()] = p.get("value")
        return arret

def getNextBus(arret,refs,line):
        """ Récupère les prochains passages à un arret donné
        lignesens : code de ligne (ligne+sens, voir get_ligne())
        code : code timéo de l'arret
        """

        code_arret = arret.split('(')[1].split(')')[0]
        line_sens = line.split('_')

        POST_params = {
            'a':'recherche_arrets',
            'refs': refs
            #'code': code_arret,
            #'sens': line_sens[1],
            #'ligne':line_sens[0],
            #'list_refs' : refs+'_'+code_arret
        }

        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/29.0.1547.57 Safari/537.36',
            'Content-type': 'application/x-www-form-urlencoded'})

        # first, get the ran param
        res = session.post("https://dev.actigraph.fr/actipages/setram/pivkdev/relais.html.php", data=POST_params)
        print(res.text)
        ran = re.search("ran=(\d+)", BeautifulSoup(res.text,features="html.parser").find_all('script')[-1].text.splitlines()[-2]).group(1)
        '''
        print(re.search("ran=(\d+)", BeautifulSoup(res.text,features="html.parser").find_all('script')[0].text))

        POST_params2 = {
            'a' : 'refresh',
            'refs': POST_params['refs'],
            'ran' : ran
        }

        # then, get the page with real data
        res = session.post("https://dev.actigraph.fr/actipages/setram/pivkdev/relais.html.php", data=POST_params2)
        
        print(res.text)
        '''
        '''
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
        '''

stops = getStopsForLine('4_A')

#print(stops)

for k,v in stops.items():
    print(k)
    print(v)
    getNextBus(k,v,'4_A')
    break
    