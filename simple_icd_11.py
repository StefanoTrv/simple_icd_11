import requests, json
from abc import ABC, abstractmethod

__all__ = ["ICDAPIClient"] #exports only the needed classes

# Abstract class that represents the code that actually interacts with the API
# All methods in this class and its subclasses can raise ConnectionError at any point if an unresolvable error occurs when trying to communicate with the API
class ICDAPIClient(ABC):

    # Abstract method that returns a dict containing the data of the entity with code code
    # Raises LookupError if it finds no entity with that code
    @abstractmethod
    def lookupCode(self, code : str, release : str, language : str) -> dict:
        raise NotImplementedError()

    # Abstract method that returns a dict containing the data of the entity with id id
    # Raises LookupError if it finds no entity with that id
    @abstractmethod
    def lookupId(self, id : str, release : str, language : str) -> dict:
        raise NotImplementedError()

    # Abstract method that returns the name of the latest available release in the given language
    @abstractmethod
    def getLatestRelease(self, language : str) -> str:
        raise NotImplementedError()

    # Abstract method that returns true if r is the name of a valid release in the given language, false otherwise
    @abstractmethod
    def checkRelease(self, release : str, language : str) -> bool:
        raise NotImplementedError()

# Class for interrogating the official ICD API
# Singleton for each clientId
class ICDOfficialAPIClient(ICDAPIClient):
    _instances = {}

    def __new__(cls, clientId : str, *args, **kwargs):
        if clientId not in cls._instances:
            cls._instances[clientId] = super(ICDOfficialAPIClient, cls).__new__(cls)
        return cls._instances[clientId]

    def __init__(self, clientId : str, clientSecret : str):
        self.clientSecret = clientSecret #allows corrections of the secret
        # Avoid re-initializing an existing instance
        if not hasattr(self, "clientId"):  # Check if the instance is being initialized for the first time
            self.locationUrl = "http://id.who.int/icd/release/11/"
            self.clientId = clientId
            self.__authenticate()

    
    # Uses the credentials to create a new token
    def __authenticate(self):
        payload = {'client_id': self.clientId, 
	   	   'client_secret': self.clientSecret, 
           'scope': 'icdapi_access', 
           'grant_type': 'client_credentials'}
        r = requests.post("https://icdaccessmanagement.who.int/connect/token", data=payload).json()
        if "error" in r:
            raise ConnectionError("Authentication attempt with official API ended with an error. Error details: "+r["error"])
        self.token = r['access_token']

    def lookupCode(self, code : str, release : str, language : str) -> dict:
        uri = self.locationUrl + release + "/mms/codeinfo/" + code
        headers = {'Authorization':  'Bearer '+ self.token, 
           'Accept': 'application/json', 
           'Accept-Language': language,
	        'API-Version': 'v2',
            'linearizationname': 'mms',
            'releaseId': release,
            'code': code}
        r = requests.get(uri, headers=headers)
        if r.status_code == 401:
            self.__authenticate()
            headers["Authorization"] = "Bearer "+ self.token
            r = requests.get(uri, headers=headers)
        if r.status_code == 404:
            raise LookupError("No ICD-11 entity with code " + code + " was found for release " + release + " in language " + language + ".")
        elif r.status_code == 200:
            j = json.loads(r.text)
            return self.lookupId(j["stemId"].split("/mms/")[1], release, language)
        else:
            raise ConnectionError("Error happened while finding entity for code " + code + ". Error code " + str(r.status_code) + " - details: \n\"" + r.text + "\"")
    
    def lookupId(self, id : str, release : str, language : str):
        uri = self.locationUrl + release + "/mms/" + id
        headers = {'Authorization':  'Bearer '+self.token, 
           'Accept': 'application/json', 
           'Accept-Language': language,
	        'API-Version': 'v2',
            'linearizationname': 'mms',
            'releaseId': release,
            'id': id}
        r = requests.get(uri, headers=headers)
        if r.status_code == 401:
            self.__authenticate()
            headers["Authorization"] = "Bearer "+ self.token
            r = requests.get(uri, headers=headers)
        if r.status_code == 404:
            raise LookupError("No ICD-11 entity with id " + id + " was found for release " + release + " in language " + language + ".")
        elif r.status_code == 200:
            return json.loads(r.text)
        else:
            raise ConnectionError("Error happened while finding entity for id " + id + ". Error code " + str(r.status_code) + " - details: \n\"" + r.text + "\"")
    
    def getLatestRelease(self, language : str) -> str:
        uri = self.locationUrl + "mms"
        headers = {'Authorization':  'Bearer '+ self.token, 
           'Accept': 'application/json', 
           'Accept-Language': language,
	        'API-Version': 'v2',
            'linearizationname': 'mms'}
        r = requests.get(uri, headers=headers)
        if r.status_code == 401:
            self.__authenticate()
            headers["Authorization"] = "Bearer "+ self.token
            r = requests.get(uri, headers=headers)
        if r.status_code == 200:
            j = json.loads(r.text)
            return j["release"][0].split("/11/")[1].split("/")[0]
        elif r.status_code == 404:
            raise LookupError("Could not find any release for language " + language + ". More details: \"" + r.text + "\"")
        else:
            raise ConnectionError("Error happened while finding code of last release in language " + language + ". Error code " + str(r.status_code) + " - details: \n\"" + r.text + "\"")
    
    def checkRelease(self, release : str, language : str) -> bool:
        uri = self.locationUrl + release + "/mms"
        headers = {'Authorization':  'Bearer '+self.token, 
           'Accept': 'application/json', 
           'Accept-Language': language,
	        'API-Version': 'v2',
            'linearizationname': 'mms',
            'releaseId': release}
        r = requests.get(uri, headers=headers)
        if r.status_code == 401:
            self.__authenticate()
            headers["Authorization"] = "Bearer "+ self.token
            r = requests.get(uri, headers=headers)
        if r.status_code == 404:
            return False
        elif r.status_code == 200:
            return True
        else:
            raise ConnectionError("Error happened while checking if release " + release + " exists in language " + language +". Error code " + str(r.status_code) + " - details: \n\"" + r.text + "\"")
    

class ICDOtherAPIClient(ICDAPIClient):
    pass

class Entity:
    pass