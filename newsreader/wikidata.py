from typing import Dict, Any
import requests
from string import Template

def map_entry(x):
    mapings = [
        ("id", "wiki"), 
        ("idLabel", "name"), 
        ("country", "country_wiki"), 
        ("countryLabel", "country"), 
        ("industry", "industry_wiki"), 
        ("industryLabel", "industry"), 
    ]
    for old, new in mapings:
        if x.get(old):
            x[new] = x[old]
            del x[old]
    return x

class Wikidata:
    """
    A collection of SQARQL queries over wikidata for key NER categories.
    """
    url: str = 'https://query.wikidata.org/sparql'
    
    def query(self, sparql: str, values: Dict[str, Any] = {}):
        sparql = Template(sparql).substitute(**values)
        r = requests.get(self.url, params = {'format': 'json', 'query': sparql })
        data = r.json()["results"]["bindings"]
        data = list(map(lambda x: { k: v["value"] for k,v in x.items() }, data))
        return list(map(map_entry, data))

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
        SELECT 
            ?id ?idLabel 
            ?industry ?industryLabel 
            ?country ?countryLabel 
            ?inception 
            ?abn 
            ?acn 
            ?ticker 
            ?website
            ?twiter
            ?employees
            ?total_debt
            ?totql_equity
            ?total_revenue
        WHERE {
        
            VALUES ?id {  wd:$id }

            OPTIONAL { ?id wdt:P856 ?website. }
            OPTIONAL { ?id wdt:P571 ?inception. }
            OPTIONAL { ?id wdt:P17 ?country. }
            OPTIONAL { ?id wdt:P3548 ?abn. }
            OPTIONAL { ?id wdt:P3549 ?acn. }
            OPTIONAL { ?id wdt:P249 ?ticker. }
            OPTIONAL { ?id wdt:P1128 ?employees. }
            OPTIONAL { ?id wdt:P452 ?industry. }
            OPTIONAL { ?id wdt:P2002 ?twiter. }
            OPTIONAL { ?id wdt:P2133 ?total_debt. }
            OPTIONAL { ?id wdt:P2137 ?total_equity. }
            OPTIONAL { ?id wdt:P2139 ?total_revenue. }
        
            SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }  
        }
        """
        return self.query(sparql, { "id": id })

    def get_person_info(self, id: str):
        sparql = """
        
        """
        return self.query(sparql)
    
    def get_location_info(self, id:str):
        sparql = """
        
        """
        return self.query(sparql, { "id": id })

