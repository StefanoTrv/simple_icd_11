from __future__ import annotations
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
            self._locationUrl = "http://id.who.int/icd/release/11/"
            self._clientId = clientId
            self.__authenticate()

    
    # Uses the credentials to create a new token
    def __authenticate(self):
        payload = {'client_id': self._clientId, 
	   	   'client_secret': self.clientSecret, 
           'scope': 'icdapi_access', 
           'grant_type': 'client_credentials'}
        r = requests.post("https://icdaccessmanagement.who.int/connect/token", data=payload).json()
        if "error" in r:
            raise ConnectionError("Authentication attempt with official API ended with an error. Error details: "+r["error"])
        self.__token = r['access_token']

    def lookupCode(self, code : str, release : str, language : str) -> dict:
        uri = self._locationUrl + release + "/mms/codeinfo/" + code
        headers = {'Authorization':  'Bearer '+ self.__token, 
           'Accept': 'application/json', 
           'Accept-Language': language,
	        'API-Version': 'v2',
            'linearizationname': 'mms',
            'releaseId': release,
            'code': code}
        r = requests.get(uri, headers=headers)
        if r.status_code == 401:
            self.__authenticate()
            headers["Authorization"] = "Bearer "+ self.__token
            r = requests.get(uri, headers=headers)
        if r.status_code == 404:
            raise LookupError("No ICD-11 entity with code " + code + " was found for release " + release + " in language " + language + ".")
        elif r.status_code == 200:
            j = json.loads(r.text)
            return self.lookupId(j["stemId"].split("/mms/")[1], release, language)
        else:
            raise ConnectionError("Error happened while finding entity for code " + code + ". Error code " + str(r.status_code) + " - details: \n\"" + r.text + "\"")
    
    def lookupId(self, id : str, release : str, language : str) -> dict:
        uri = self._locationUrl + release + "/mms/" + id
        headers = {'Authorization':  'Bearer '+self.__token, 
           'Accept': 'application/json', 
           'Accept-Language': language,
	        'API-Version': 'v2',
            'linearizationname': 'mms',
            'releaseId': release,
            'id': id}
        r = requests.get(uri, headers=headers)
        if r.status_code == 401:
            self.__authenticate()
            headers["Authorization"] = "Bearer "+ self.__token
            r = requests.get(uri, headers=headers)
        if r.status_code == 404:
            raise LookupError("No ICD-11 entity with id " + id + " was found for release " + release + " in language " + language + ".")
        elif r.status_code == 200:
            return json.loads(r.text)
        else:
            raise ConnectionError("Error happened while finding entity for id " + id + ". Error code " + str(r.status_code) + " - details: \n\"" + r.text + "\"")
    
    def getLatestRelease(self, language : str) -> str:
        uri = self._locationUrl + "mms"
        headers = {'Authorization':  'Bearer '+ self.__token, 
           'Accept': 'application/json', 
           'Accept-Language': language,
	        'API-Version': 'v2',
            'linearizationname': 'mms'}
        r = requests.get(uri, headers=headers)
        if r.status_code == 401:
            self.__authenticate()
            headers["Authorization"] = "Bearer "+ self.__token
            r = requests.get(uri, headers=headers)
        if r.status_code == 200:
            j = json.loads(r.text)
            return j["release"][0].split("/11/")[1].split("/")[0]
        elif r.status_code == 404:
            raise LookupError("Could not find any release for language " + language + ". More details: \"" + r.text + "\"")
        else:
            raise ConnectionError("Error happened while finding code of last release in language " + language + ". Error code " + str(r.status_code) + " - details: \n\"" + r.text + "\"")
    
    def checkRelease(self, release : str, language : str) -> bool:
        uri = self._locationUrl + release + "/mms"
        headers = {'Authorization':  'Bearer '+self.__token, 
           'Accept': 'application/json', 
           'Accept-Language': language,
	        'API-Version': 'v2',
            'linearizationname': 'mms',
            'releaseId': release}
        r = requests.get(uri, headers=headers)
        if r.status_code == 401:
            self.__authenticate()
            headers["Authorization"] = "Bearer "+ self.__token
            r = requests.get(uri, headers=headers)
        if r.status_code == 404:
            return False
        elif r.status_code == 200:
            return True
        else:
            raise ConnectionError("Error happened while checking if release " + release + " exists in language " + language +". Error code " + str(r.status_code) + " - details: \n\"" + r.text + "\"")
    

class ICDOtherAPIClient(ICDAPIClient):
    pass

class Entity(ABC):
    @abstractmethod
    def getId(self) -> str:
        raise NotImplementedError()
    
    @abstractmethod
    def getURI(self) -> str:
        raise NotImplementedError()
    
    @abstractmethod
    def getCode(self) -> str:
        raise NotImplementedError()
    
    @abstractmethod
    def getTitle(self) -> str:
        raise NotImplementedError()
    
    @abstractmethod
    def getDefinition(self) -> str:
        raise NotImplementedError()
    
    @abstractmethod
    def getLongDefinition(self) -> str:
        raise NotImplementedError()
    
    @abstractmethod
    def getFullySpecifiedName(self) -> str:
        raise NotImplementedError()
    
    @abstractmethod
    def getDiagnosticCriteria(self) -> str:
        raise NotImplementedError()
    
    @abstractmethod
    def getCodingNote(self) -> str:
        raise NotImplementedError()
    
    @abstractmethod
    def getBlockId(self) -> str:
        raise NotImplementedError()
    
    @abstractmethod
    def getBlockRange(self) -> str:
        raise NotImplementedError()
    
    @abstractmethod
    def getClassKind(self) -> str:
        raise NotImplementedError()
    
    @abstractmethod
    def isResidual(self) -> bool:
        raise NotImplementedError()
    
    @abstractmethod
    def getChildren(self) -> list[Entity]:
        raise NotImplementedError()
    
    @abstractmethod
    def getChildrenElsewhere(self) -> list[Entity]:
        raise NotImplementedError()
    
    @abstractmethod
    def getDescendants(self) -> str:
        raise NotImplementedError()
    
    @abstractmethod
    def getParent(self) -> Entity | None:
        raise NotImplementedError()
    
    @abstractmethod
    def getAncestors(self) -> list[Entity]:
        raise NotImplementedError()
    
    @abstractmethod
    def getIndexTerm(self) -> list[str]:
        raise NotImplementedError()
    
    @abstractmethod
    def getInclusion(self) -> list[str]:
        raise NotImplementedError()
    
    @abstractmethod
    def getExclusion(self) -> list[Entity]:
        raise NotImplementedError()
    
    @abstractmethod
    def getRelatedEntitiesInMaternalChapter(self) -> str:
        raise NotImplementedError()
    
    @abstractmethod
    def getRelatedEntitiesInPerinatalChapter(self) -> str:
        raise NotImplementedError()


class ProxyEntity(Entity):
    def __init__(self, explorer : ICDExplorer, id : str, uri : str, title : str | None = None, parent : Entity | None = None) -> None:
        self.__real = None
        self.__explorer = explorer
        self.__id = id
        self.__uri = uri
        self.__title = title
        self.__parent = parent

    def getId(self) -> str:
        return self.__id
    
    def getURI(self) -> str:
        return self.__uri
    
    def getCode(self) -> str:
        if self.__real is None:
            self.__explorer._getRealEntity(self.__id)
        return self.__real.getTitle() # type: ignore
    
    def getTitle(self) -> str:
        if self.__title is not None:
            return self.__title
        if self.__real is None:
            self.__explorer._getRealEntity(self.__id)
        self.__title = self.__real.getTitle() # type: ignore
        return self.__title
    
    def getDefinition(self) -> str:
        if self.__real is None:
            self.__explorer._getRealEntity(self.__id)
        return self.__real.getDefinition() # type: ignore
    
    def getLongDefinition(self) -> str:
        if self.__real is None:
            self.__explorer._getRealEntity(self.__id)
        return self.__real.getLongDefinition() # type: ignore
    
    def getFullySpecifiedName(self) -> str:
        if self.__real is None:
            self.__explorer._getRealEntity(self.__id)
        return self.__real.getFullySpecifiedName() # type: ignore
    
    def getDiagnosticCriteria(self) -> str:
        if self.__real is None:
            self.__explorer._getRealEntity(self.__id)
        return self.__real.getDiagnosticCriteria() # type: ignore
    
    def getCodingNote(self) -> str:
        if self.__real is None:
            self.__explorer._getRealEntity(self.__id)
        return self.__real.getCodingNote() # type: ignore
    
    def getBlockId(self) -> str:
        if self.__real is None:
            self.__explorer._getRealEntity(self.__id)
        return self.__real.getBlockId() # type: ignore
    
    def getBlockRange(self) -> str:
        if self.__real is None:
            self.__explorer._getRealEntity(self.__id)
        return self.__real.getBlockRange() # type: ignore
    
    def getClassKind(self) -> str:
        if self.__real is None:
            self.__explorer._getRealEntity(self.__id)
        return self.__real.getClassKind() # type: ignore
    
    def isResidual(self) -> bool:
        if self.__real is None:
            self.__explorer._getRealEntity(self.__id)
        return self.__real.isResidual() # type: ignore
    
    def getChildren(self) -> list[Entity]:
        if self.__real is None:
            self.__explorer._getRealEntity(self.__id)
        return self.__real.getChildren() # type: ignore
    
    def getChildrenElsewhere(self) -> list[Entity]:
        if self.__real is None:
            self.__explorer._getRealEntity(self.__id)
        return self.__real.getChildrenElsewhere() # type: ignore
    
    def getDescendants(self) -> str:
        if self.__real is None:
            self.__explorer._getRealEntity(self.__id)
        return self.__real.getDescendants() # type: ignore
    
    def getParent(self) -> Entity | None:
        if self.__parent is not None:
            return self.__parent
        if self.__real is None:
            self.__explorer._getRealEntity(self.__id)
        self.__parent = self.__real.getParent() # type: ignore
        return self.__parent
    
    def getAncestors(self) -> list[Entity]:
        if self.__real is None:
            self.__explorer._getRealEntity(self.__id)
        return self.__real.getAncestors() # type: ignore
    
    def getIndexTerm(self) -> list[str]:
        if self.__real is None:
            self.__explorer._getRealEntity(self.__id)
        return self.__real.getIndexTerm() # type: ignore
    
    def getInclusion(self) -> list[str]:
        if self.__real is None:
            self.__explorer._getRealEntity(self.__id)
        return self.__real.getInclusion() # type: ignore
    
    def getExclusion(self) -> list[Entity]:
        if self.__real is None:
            self.__explorer._getRealEntity(self.__id)
        return self.__real.getExclusion() # type: ignore
    
    def getRelatedEntitiesInMaternalChapter(self) -> str:
        if self.__real is None:
            self.__explorer._getRealEntity(self.__id)
        return self.__real.getRelatedEntitiesInMaternalChapter() # type: ignore
    
    def getRelatedEntitiesInPerinatalChapter(self) -> str:
        if self.__real is None:
            self.__explorer._getRealEntity(self.__id)
        return self.__real.getRelatedEntitiesInPerinatalChapter() # type: ignore


class ICDExplorer:
    def _getRealEntity(self, id : str) -> Entity:
        return Entity()