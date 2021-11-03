import requests
import pprint

class Wikidata:
    url: str = 'https://query.wikidata.org/sparql'
    
    def query(self, sparql: str):
        r = requests.get(self.url, params = {'format': 'json', 'query': sparql })
        data = r.json()
        pprint(data)

    def get_info(self, label: str, id: str):
        if label == "ORG":
            return self.get_organisation_info(id)
        elif label == "PER":
            return self.get_person_info(id)
        elif label == "LOC":
            return self.get_location_info(id)
        else:
            raise NotImplementedError

    def get_organisation_info(self, id: str):
        sparql = """
        
        """
        return self.query(sparql)

    def get_person_info(self, id: str):
        sparql = """
        
        """
        return self.query(sparql)

    
        
wiki = Wikidata()
wiki.query('''
SELECT ?item ?itemLabel ?linkcount WHERE {
    ?item wdt:P31/wdt:P279* wd:Q35666 .
    ?item wikibase:sitelinks ?linkcount .
    FILTER (?linkcount >= 1) .
        SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en" . }
    }
    GROUP BY ?item ?itemLabel ?linkcount
    ORDER BY DESC(?linkcount)
''')

