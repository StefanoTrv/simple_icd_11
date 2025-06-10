# simple_icd_11 is released under the MIT License
# Copyright (c) 2024-2025 Stefano Travasci
# Read the full LICENCES at https://github.com/StefanoTrv/simple_icd_11/blob/master/LICENSE

from __future__ import annotations
from typing import Dict
import requests, json
from abc import ABC, abstractmethod

__all__ = ["ICDExplorer", "Entity"]  # exports only the needed classes


# Abstract class that represents the code that actually interacts with the API
# All methods in this class and its subclasses can raise ConnectionError at any point if an unresolvable error occurs when trying to communicate with the API
class ICDAPIClient(ABC):

    # Abstract method that returns a dict containing the data of the entity with code code
    # Raises LookupError if it finds no entity with that code
    @abstractmethod
    def lookupCode(self, code: str, release: str, language: str) -> dict:
        raise NotImplementedError()

    # Abstract method that returns a dict containing the data of the entity with id id
    # Raises LookupError if it finds no entity with that id
    @abstractmethod
    def lookupId(self, id: str, release: str, language: str) -> dict:
        raise NotImplementedError()

    # Abstract method that returns the name of the latest available release in the given language
    @abstractmethod
    def getLatestRelease(self, language: str) -> str:
        raise NotImplementedError()

    # Abstract method that returns true if r is the name of a valid release in the given language, false otherwise
    @abstractmethod
    def checkRelease(self, release: str, language: str) -> bool:
        raise NotImplementedError()


# Class for interrogating the official ICD API
# Singleton for each clientId
class ICDOfficialAPIClient(ICDAPIClient):
    _instances: Dict[str, ICDOfficialAPIClient] = {}

    def __new__(cls, clientId: str, clientSecret: str):
        if clientId not in cls._instances:
            return super(ICDOfficialAPIClient, cls).__new__(cls)
        elif (
            cls._instances[clientId]._clientSecret != clientSecret
        ):  # Raises error if clientSecret is wrong
            raise ConnectionError(
                "Provided clientSecret is not consistent with previously provided correct secret."
            )
        return cls._instances[clientId]

    def __init__(self, clientId: str, clientSecret: str):
        # Avoid re-initializing an existing instance
        if not hasattr(
            self, "_clientId"
        ):  # Check if the instance is being initialized for the first time
            self._locationUrl = "http://id.who.int/icd/release/11/"
            self._clientId = clientId
            self._clientSecret = clientSecret
            self.__authenticate()
            type(self)._instances[
                clientId
            ] = self  # Adds only authenticated Clients to map

    # Uses the credentials to create a new token
    def __authenticate(self):
        payload = {
            "client_id": self._clientId,
            "client_secret": self._clientSecret,
            "scope": "icdapi_access",
            "grant_type": "client_credentials",
        }
        r = requests.post(
            "https://icdaccessmanagement.who.int/connect/token", data=payload
        ).json()
        if "error" in r:
            raise ConnectionError(
                "Authentication attempt with official API ended with an error. Error details: "
                + r["error"]
            )
        self.__token = r["access_token"]

    def lookupCode(self, code: str, release: str, language: str) -> dict:
        uri = self._locationUrl + release + "/mms/codeinfo/" + code
        headers = {
            "Authorization": "Bearer " + self.__token,
            "Accept": "application/json",
            "Accept-Language": language,
            "API-Version": "v2",
            "linearizationname": "mms",
            "releaseId": release,
            "code": code,
        }
        r = requests.get(uri, headers=headers)
        if r.status_code == 401:
            self.__authenticate()
            headers["Authorization"] = "Bearer " + self.__token
            r = requests.get(uri, headers=headers)
        if r.status_code == 404:
            raise LookupError(
                "No ICD-11 entity with code "
                + code
                + " was found for release "
                + release
                + " in language "
                + language
                + "."
            )
        elif r.status_code == 200:
            j = json.loads(r.text)
            return self.lookupId(j["stemId"].split("/mms/")[1], release, language)
        else:
            raise ConnectionError(
                "Error happened while finding entity for code "
                + code
                + ". Error code "
                + str(r.status_code)
                + ' - details: \n"'
                + r.text
                + '"'
            )

    def lookupId(self, id: str, release: str, language: str) -> dict:
        uri = self._locationUrl + release + "/mms/" + id + "?include=diagnosticCriteria"
        headers = {
            "Authorization": "Bearer " + self.__token,
            "Accept": "application/json",
            "Accept-Language": language,
            "API-Version": "v2",
            "linearizationname": "mms",
            "releaseId": release,
            "id": id,
            "include": "diagnosticCriteria",
        }
        r = requests.get(uri, headers=headers)
        if r.status_code == 401:
            self.__authenticate()
            headers["Authorization"] = "Bearer " + self.__token
            r = requests.get(uri, headers=headers)
        if r.status_code == 404:
            raise LookupError(
                "No ICD-11 entity with id "
                + id
                + " was found for release "
                + release
                + " in language "
                + language
                + "."
            )
        elif r.status_code == 200:
            return json.loads(r.text)
        else:
            raise ConnectionError(
                "Error happened while finding entity for id "
                + id
                + ". Error code "
                + str(r.status_code)
                + ' - details: \n"'
                + r.text
                + '"'
            )

    def getLatestRelease(self, language: str) -> str:
        uri = self._locationUrl + "mms"
        headers = {
            "Authorization": "Bearer " + self.__token,
            "Accept": "application/json",
            "Accept-Language": language,
            "API-Version": "v2",
            "linearizationname": "mms",
        }
        r = requests.get(uri, headers=headers)
        if r.status_code == 401:
            self.__authenticate()
            headers["Authorization"] = "Bearer " + self.__token
            r = requests.get(uri, headers=headers)
        if r.status_code == 200:
            j = json.loads(r.text)
            return j["release"][0].split("/11/")[1].split("/")[0]
        elif r.status_code == 404:
            raise LookupError(
                "Could not find any release for language "
                + language
                + '. More details: "'
                + r.text
                + '"'
            )
        else:
            raise ConnectionError(
                "Error happened while finding code of last release in language "
                + language
                + ". Error code "
                + str(r.status_code)
                + ' - details: \n"'
                + r.text
                + '"'
            )

    def checkRelease(self, release: str, language: str) -> bool:
        uri = self._locationUrl + release + "/mms"
        headers = {
            "Authorization": "Bearer " + self.__token,
            "Accept": "application/json",
            "Accept-Language": language,
            "API-Version": "v2",
            "linearizationname": "mms",
            "releaseId": release,
        }
        r = requests.get(uri, headers=headers)
        if r.status_code == 401:
            self.__authenticate()
            headers["Authorization"] = "Bearer " + self.__token
            r = requests.get(uri, headers=headers)
        if r.status_code == 404:
            return False
        elif r.status_code == 200:
            return True
        else:
            raise ConnectionError(
                "Error happened while checking if release "
                + release
                + " exists in language "
                + language
                + ". Error code "
                + str(r.status_code)
                + ' - details: \n"'
                + r.text
                + '"'
            )


# Class for interrogating an unofficial ICD API
# Singleton for each locationUrl
class ICDOtherAPIClient(ICDAPIClient):
    _instances = {}

    def __new__(cls, locationUrl: str, *args, **kwargs):
        if locationUrl not in cls._instances:
            cls._instances[locationUrl] = super(ICDOtherAPIClient, cls).__new__(cls)
        return cls._instances[locationUrl]

    def __init__(self, locationUrl: str):
        # Avoid re-initializing an existing instance
        if not hasattr(
            self, "_locationUrl"
        ):  # Check if the instance is being initialized for the first time
            self._locationUrl = locationUrl + "icd/release/11/"
            # checks if destination url is responsive
            try:
                r = requests.head(locationUrl + "icd/entity")
                if r.status_code != 405:
                    raise ConnectionError(
                        'Error happened while trying to connect with url "'
                        + self._locationUrl
                        + '". Error code '
                        + str(r.status_code)
                        + ' - details:\n"'
                        + r.text
                        + '"'
                    )
            except Exception as e:
                raise ConnectionError(
                    'Error happened while trying to connect with url "'
                    + self._locationUrl
                    + '" - details:\n"'
                    + str(e)
                    + '"'
                )

    def lookupCode(self, code: str, release: str, language: str) -> dict:
        uri = self._locationUrl + release + "/mms/codeinfo/" + code
        headers = {
            "Authorization": "",
            "Accept": "application/json",
            "Accept-Language": language,
            "API-Version": "v2",
            "linearizationname": "mms",
            "releaseId": release,
            "code": code,
        }
        r = requests.get(uri, headers=headers)
        if r.status_code == 404:
            raise LookupError(
                "No ICD-11 entity with code "
                + code
                + " was found for release "
                + release
                + " in language "
                + language
                + "."
            )
        elif r.status_code == 200:
            j = json.loads(r.text)
            return self.lookupId(j["stemId"].split("/mms/")[1], release, language)
        else:
            raise ConnectionError(
                "Error happened while finding entity for code "
                + code
                + ". Error code "
                + str(r.status_code)
                + ' - details: \n"'
                + r.text
                + '"'
            )

    def lookupId(self, id: str, release: str, language: str) -> dict:
        uri = self._locationUrl + release + "/mms/" + id + "?include=diagnosticCriteria"
        headers = {
            "Authorization": "",
            "Accept": "application/json",
            "Accept-Language": language,
            "API-Version": "v2",
            "linearizationname": "mms",
            "releaseId": release,
            "id": id,
            "include": "diagnosticCriteria",
        }
        r = requests.get(uri, headers=headers)
        if r.status_code == 404:
            raise LookupError(
                "No ICD-11 entity with id "
                + id
                + " was found for release "
                + release
                + " in language "
                + language
                + "."
            )
        elif r.status_code == 200:
            result = json.loads(r.text)
            if "browserUrl" in result:
                result["browserUrl"] = result["browserUrl"].replace(
                    "https://icd.who.int/", "http://localhost/"
                )
            return result
        else:
            raise ConnectionError(
                "Error happened while finding entity for id "
                + id
                + ". Error code "
                + str(r.status_code)
                + ' - details: \n"'
                + r.text
                + '"'
            )

    def getLatestRelease(self, language: str) -> str:
        uri = self._locationUrl + "mms"
        headers = {
            "Authorization": "",
            "Accept": "application/json",
            "Accept-Language": language,
            "API-Version": "v2",
            "linearizationname": "mms",
        }
        r = requests.get(uri, headers=headers)
        if r.status_code == 200:
            j = json.loads(r.text)
            return j["release"][0].split("/11/")[1].split("/")[0]
        elif r.status_code == 404:
            raise LookupError(
                "Could not find any release for language "
                + language
                + '. More details: "'
                + r.text
                + '"'
            )
        else:
            raise ConnectionError(
                "Error happened while finding code of last release in language "
                + language
                + ". Error code "
                + str(r.status_code)
                + ' - details: \n"'
                + r.text
                + '"'
            )

    def checkRelease(self, release: str, language: str) -> bool:
        uri = self._locationUrl + release + "/mms"
        headers = {
            "Authorization": "",
            "Accept": "application/json",
            "Accept-Language": language,
            "API-Version": "v2",
            "linearizationname": "mms",
            "releaseId": release,
        }
        r = requests.get(uri, headers=headers)
        if r.status_code == 404:
            return False
        elif r.status_code == 200:
            return True
        else:
            raise ConnectionError(
                "Error happened while checking if release "
                + release
                + " exists in language "
                + language
                + ". Error code "
                + str(r.status_code)
                + ' - details: \n"'
                + r.text
                + '"'
            )


# Abstract class representing an ICD-11 MMS entity
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
    def getCodingNote(self, includeFromUpperLevels: bool = False) -> str:
        raise NotImplementedError()

    @abstractmethod
    def getBlockId(self) -> str:
        raise NotImplementedError()

    @abstractmethod
    def getCodeRange(self) -> str:
        raise NotImplementedError()

    @abstractmethod
    def getClassKind(self) -> str:
        raise NotImplementedError()

    @abstractmethod
    def getPostcoordinationScale(self) -> dict[str, list[Entity]]:
        raise NotImplementedError()

    @abstractmethod
    def isResidual(self) -> bool:
        raise NotImplementedError()

    @abstractmethod
    def getChildren(self, includeChildrenElsewhere: bool = False) -> list[Entity]:
        raise NotImplementedError()

    @abstractmethod
    def getChildrenElsewhere(self) -> list[Entity]:
        raise NotImplementedError()

    @abstractmethod
    def getDescendants(self, includeChildrenElsewhere: bool = False) -> list[Entity]:
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
    def getExclusion(self, includeFromUpperLevels: bool = True) -> list[Entity]:
        raise NotImplementedError()

    @abstractmethod
    def getRelatedEntitiesInMaternalChapter(self) -> list[Entity]:
        raise NotImplementedError()

    @abstractmethod
    def getRelatedEntitiesInPerinatalChapter(self) -> list[Entity]:
        raise NotImplementedError()

    @abstractmethod
    def getBrowserUrl(self) -> str:
        raise NotImplementedError()

    @abstractmethod
    def _appendDescendants(
        self, includeChildrenElsewhere: bool, lst: list[Entity]
    ) -> None:
        raise NotImplementedError()

    @abstractmethod
    def _appendAncestors(self, lst: list[Entity]) -> None:
        raise NotImplementedError()

    @abstractmethod
    def _appendExclusion(
        self, lst: list[Entity]
    ) -> (
        None
    ):  # includeFromUpperLevels is omitted from the parameters: it must be true!
        raise NotImplementedError()


# Proxy class for entities that were found in the description of other entities, so that for now we have limited information about them
class ProxyEntity(Entity):
    def __init__(
        self, explorer: ICDExplorer, id: str, uri: str, parent: Entity | None = None
    ) -> None:
        self.__real = None
        self.__explorer = explorer
        self.__id = id
        self.__uri = uri
        self.__parent = parent

    def getId(self) -> str:
        return self.__id

    def getURI(self) -> str:
        return self.__uri

    def getCode(self) -> str:
        if self.__real is None:
            self.__real = self.__explorer._getRealEntity(self.__id)
        return self.__real.getCode()  # type: ignore

    def getTitle(self) -> str:
        if self.__real is None:
            self.__real = self.__explorer._getRealEntity(self.__id)
        return self.__real.getTitle()  # type: ignore

    def getDefinition(self) -> str:
        if self.__real is None:
            self.__real = self.__explorer._getRealEntity(self.__id)
        return self.__real.getDefinition()  # type: ignore

    def getLongDefinition(self) -> str:
        if self.__real is None:
            self.__real = self.__explorer._getRealEntity(self.__id)
        return self.__real.getLongDefinition()  # type: ignore

    def getFullySpecifiedName(self) -> str:
        if self.__real is None:
            self.__real = self.__explorer._getRealEntity(self.__id)
        return self.__real.getFullySpecifiedName()  # type: ignore

    def getDiagnosticCriteria(self) -> str:
        if self.__real is None:
            self.__real = self.__explorer._getRealEntity(self.__id)
        return self.__real.getDiagnosticCriteria()  # type: ignore

    def getCodingNote(self, includeFromUpperLevels: bool = False) -> str:
        if self.__real is None:
            self.__real = self.__explorer._getRealEntity(self.__id)
        return self.__real.getCodingNote(includeFromUpperLevels=includeFromUpperLevels)  # type: ignore

    def getBlockId(self) -> str:
        if self.__real is None:
            self.__real = self.__explorer._getRealEntity(self.__id)
        return self.__real.getBlockId()  # type: ignore

    def getCodeRange(self) -> str:
        if self.__real is None:
            self.__real = self.__explorer._getRealEntity(self.__id)
        return self.__real.getCodeRange()  # type: ignore

    def getClassKind(self) -> str:
        if self.__real is None:
            self.__real = self.__explorer._getRealEntity(self.__id)
        return self.__real.getClassKind()  # type: ignore

    def getPostcoordinationScale(self) -> dict[str, list[Entity]]:
        if self.__real is None:
            self.__real = self.__explorer._getRealEntity(self.__id)
        return self.__real.getPostcoordinationScale()  # type: ignore

    def isResidual(self) -> bool:
        return "unspecified" in self.__id or "other" in self.__id

    def getChildren(self, includeChildrenElsewhere: bool = False) -> list[Entity]:
        if self.__real is None:
            self.__real = self.__explorer._getRealEntity(self.__id)
        return self.__real.getChildren(includeChildrenElsewhere=includeChildrenElsewhere)  # type: ignore

    def getChildrenElsewhere(self) -> list[Entity]:
        if self.__real is None:
            self.__real = self.__explorer._getRealEntity(self.__id)
        return self.__real.getChildrenElsewhere()  # type: ignore

    def getDescendants(self, includeChildrenElsewhere: bool = False) -> list[Entity]:
        if self.__real is None:
            self.__real = self.__explorer._getRealEntity(self.__id)
        return self.__real.getDescendants(includeChildrenElsewhere=includeChildrenElsewhere)  # type: ignore

    def getParent(self) -> Entity | None:
        if self.__parent is not None:
            return self.__parent
        if self.__real is None:
            self.__real = self.__explorer._getRealEntity(self.__id)
        self.__parent = self.__real.getParent()  # type: ignore
        return self.__parent

    def getAncestors(self) -> list[Entity]:
        if self.__real is None:
            self.__real = self.__explorer._getRealEntity(self.__id)
        return self.__real.getAncestors()  # type: ignore

    def getIndexTerm(self) -> list[str]:
        if self.__real is None:
            self.__real = self.__explorer._getRealEntity(self.__id)
        return self.__real.getIndexTerm()  # type: ignore

    def getInclusion(self) -> list[str]:
        if self.__real is None:
            self.__real = self.__explorer._getRealEntity(self.__id)
        return self.__real.getInclusion()  # type: ignore

    def getExclusion(self, includeFromUpperLevels: bool = True) -> list[Entity]:
        if self.__real is None:
            self.__real = self.__explorer._getRealEntity(self.__id)
        return self.__real.getExclusion(includeFromUpperLevels=includeFromUpperLevels)  # type: ignore

    def getRelatedEntitiesInMaternalChapter(self) -> list[Entity]:
        if self.__real is None:
            self.__real = self.__explorer._getRealEntity(self.__id)
        return self.__real.getRelatedEntitiesInMaternalChapter()  # type: ignore

    def getRelatedEntitiesInPerinatalChapter(self) -> list[Entity]:
        if self.__real is None:
            self.__real = self.__explorer._getRealEntity(self.__id)
        return self.__real.getRelatedEntitiesInPerinatalChapter()  # type: ignore

    def getBrowserUrl(self) -> str:
        if self.__real is None:
            self.__real = self.__explorer._getRealEntity(self.__id)
        return self.__real.getBrowserUrl()  # type: ignore

    def _setParent(self, p: Entity) -> None:
        self.__parent = p

    def _appendDescendants(
        self, includeChildrenElsewhere: bool, lst: list[Entity]
    ) -> None:
        if self.__real is None:
            self.__real = self.__explorer._getRealEntity(self.__id)
        self.__real._appendDescendants(includeChildrenElsewhere, lst)  # type: ignore

    def _appendAncestors(self, lst: list[Entity]) -> None:
        if self.__real is None:
            self.__real = self.__explorer._getRealEntity(self.__id)
        self.__real._appendAncestors(lst)  # type: ignore

    def _appendExclusion(self, lst: list[Entity]) -> None:
        if self.__real is None:
            self.__real = self.__explorer._getRealEntity(self.__id)
        self.__real._appendExclusion(lst)  # type: ignore


# Concrete class containing all the data (that we are interested in) of single ICD-11 MMS entities
# String values for fields missing from this entity are empty strings, not None values
class RealEntity(Entity):
    def __init__(
        self,
        id: str,
        uri: str,
        code: str,
        title: str,
        definition: str,
        longDefinition: str,
        fullySpecifiedName: str,
        diagnosticCriteria: str,
        codingNote: str,
        blockId: str,
        codeRange: str,
        classKind: str,
        postcoordinationScale: dict[str, list[Entity]],
        children: list[Entity],
        childrenElsewhere: list[Entity],
        parent: Entity | None,
        indexTerm: list[str],
        inclusion: list[str],
        exclusion: list[Entity],
        relatedEntitiesInMaternalChapter: list[Entity],
        relatedEntitiesInPerinatalChapter: list[Entity],
        browserUrl: str,
    ) -> None:
        self.__id = id
        self.__uri = uri
        self.__code = code
        self.__title = title
        self.__definition = definition
        self.__longDefinition = longDefinition
        self.__fullySpecifiedName = fullySpecifiedName
        self.__diagnosticCriteria = diagnosticCriteria
        self.__codingNote = codingNote
        self.__blockId = blockId
        self.__codeRange = codeRange
        self.__classKind = classKind
        self.__postcoordinationScale = postcoordinationScale
        self.__children = children
        self.__childrenElsewhere = childrenElsewhere
        self.__parent = parent
        self.__indexTerm = indexTerm
        self.__inclusion = inclusion
        self.__exclusion = exclusion
        self.__relatedEntitiesInMaternalChapter = relatedEntitiesInMaternalChapter
        self.__relatedEntitiesInPerinatalChapter = relatedEntitiesInPerinatalChapter
        self.__browserUrl = browserUrl

    def getId(self) -> str:
        return self.__id

    def getURI(self) -> str:
        return self.__uri

    def getCode(self) -> str:
        return self.__code

    def getTitle(self) -> str:
        return self.__title

    def getDefinition(self) -> str:
        return self.__definition

    def getLongDefinition(self) -> str:
        return self.__longDefinition

    def getFullySpecifiedName(self) -> str:
        return self.__fullySpecifiedName

    def getDiagnosticCriteria(self) -> str:
        return self.__diagnosticCriteria

    def getCodingNote(
        self, includeFromUpperLevels: bool = False
    ) -> str:  # implementation could be made more efficient
        if includeFromUpperLevels and self.__parent is not None:
            if self.__codingNote == "":  # avoids merging with empty strings
                return self.__parent.getCodingNote(includeFromUpperLevels=True)
            else:
                return (
                    self.__parent.getCodingNote(includeFromUpperLevels=True)
                    + "\n"
                    + self.__codingNote
                )
        else:
            return self.__codingNote

    def getBlockId(self) -> str:
        return self.__blockId

    def getCodeRange(self) -> str:
        return self.__codeRange

    def getClassKind(self) -> str:
        return self.__classKind

    def getPostcoordinationScale(self) -> dict[str, list[Entity]]:
        return self.__postcoordinationScale.copy()

    def isResidual(self) -> bool:
        return "unspecified" in self.__id or "other" in self.__id

    def getChildren(self, includeChildrenElsewhere: bool = False) -> list[Entity]:
        if includeChildrenElsewhere:
            return self.__children + self.__childrenElsewhere
        else:
            return self.__children.copy()

    def getChildrenElsewhere(self) -> list[Entity]:
        return self.__childrenElsewhere.copy()

    def getDescendants(self, includeChildrenElsewhere: bool = False) -> list[Entity]:
        lst: list[Entity] = []
        self._appendDescendants(includeChildrenElsewhere, lst)
        return lst

    def getParent(self) -> Entity | None:
        return self.__parent

    def getAncestors(self) -> list[Entity]:
        lst: list[Entity] = []
        self._appendAncestors(lst)
        return lst

    def getIndexTerm(self) -> list[str]:
        return self.__indexTerm.copy()

    def getInclusion(self) -> list[str]:
        return self.__inclusion.copy()

    def getExclusion(self, includeFromUpperLevels: bool = True) -> list[Entity]:
        lst: list[Entity] = self.__exclusion.copy()
        if includeFromUpperLevels and self.__parent is not None:
            self.__parent._appendExclusion(lst)
        return lst

    def getRelatedEntitiesInMaternalChapter(self) -> list[Entity]:
        return self.__relatedEntitiesInMaternalChapter.copy()

    def getRelatedEntitiesInPerinatalChapter(self) -> list[Entity]:
        return self.__relatedEntitiesInPerinatalChapter.copy()

    def getBrowserUrl(self) -> str:
        return self.__browserUrl

    def _appendDescendants(
        self, includeChildrenElsewhere: bool, lst: list[Entity]
    ) -> None:
        for child in self.__children:
            lst.append(child)
            child._appendDescendants(includeChildrenElsewhere, lst)
        if not includeChildrenElsewhere:
            return
        for child in self.__childrenElsewhere:
            lst.append(child)
            child._appendDescendants(True, lst)

    def _appendAncestors(self, lst: list[Entity]) -> None:
        if self.__parent is not None:
            lst.append(self.__parent)
            self.__parent._appendAncestors(lst)

    def _appendExclusion(self, lst: list[Entity]) -> None:
        for ex in self.__exclusion:
            lst.append(ex)
        if self.__parent is not None:
            self.__parent._appendExclusion(lst)


# Main class of the library
# Interacts with an API client to create Entity objects
class ICDExplorer:
    def __init__(
        self,
        language: str,
        clientId: str,
        clientSecret: str,
        release: str | None = None,
        customUrl: str | None = None,
        useCodeRangesAsCodes: bool = False,
    ) -> None:
        if customUrl is None:  # creates correct API client
            self.__clientAPI = ICDOfficialAPIClient(clientId, clientSecret)
        else:
            self.__clientAPI = ICDOtherAPIClient(customUrl)

        if release is None:  # finds or sets release
            self.__release = self.__clientAPI.getLatestRelease(language)
        else:
            if self.__clientAPI.checkRelease(release, language):
                self.__release = release
            else:
                raise LookupError(
                    'Release "'
                    + release
                    + '" was not found for language "'
                    + language
                    + '"'
                )

        self.__language = language
        self.__useCodeRangesAsCodes = useCodeRangesAsCodes
        self.__idMap = {}
        self.__codeToIdMap = {}

    # Given a code, returns true if its a valid code for the parameters of this Explorer
    def isValidCode(self, code: str) -> bool:
        if code in self.__codeToIdMap:
            return True
        if self.__useCodeRangesAsCodes and "-" in code:  # code ranges as codes
            if self.isValidCode(code.split("-")[0]):
                e = self.getEntityFromCode(code.split("-")[0])
                e = e.getParent()
                while (
                    e is not None
                ):  # controls the ancestors until it find the code or it reaches a chapter
                    if e.getCode() == code:
                        return True
                    e = e.getParent()
                return False
            else:
                return False
        try:
            dict = self.__clientAPI.lookupCode(code, self.__release, self.__language)
            self.__createAndAddNewEntity(dict)
            return True
        except LookupError:
            return False

    # Given an id, returns true if its a valid id for the parameters of this Explorer
    def isValidId(self, id: str) -> bool:
        if id in self.__idMap:
            return True
        try:
            dict = self.__clientAPI.lookupId(id, self.__release, self.__language)
            self.__createAndAddNewEntity(dict)
            return True
        except LookupError:
            return False

    # Given a code, returns its corresponding entity
    # Raises LookupError if code is not a valid code for the parameters of this Explorer
    def getEntityFromCode(self, code: str) -> Entity:
        if code in self.__codeToIdMap:
            return self.__idMap[self.__codeToIdMap[code]]
        if self.__useCodeRangesAsCodes and "-" in code:  # code ranges as codes
            if self.isValidCode(code.split("-")[0]):
                e = self.getEntityFromCode(code.split("-")[0])
                e = e.getParent()
                while (
                    e is not None
                ):  # controls the ancestors until it find the code or it reaches a chapter
                    if e.getCode() == code:
                        return e
                    e = e.getParent()
            raise LookupError(
                'Code range "'
                + code
                + '" was not found for release "'
                + self.__release
                + '" in language "'
                + self.__language
                + '".'
            )
        dict = self.__clientAPI.lookupCode(code, self.__release, self.__language)
        return self.__createAndAddNewEntity(dict)

    # Given an id, returns its corresponding entity
    # Raises LookupError if id is not a valid id for the parameters of this Explorer
    def getEntityFromId(self, id: str) -> Entity:
        if id in self.__idMap:
            return self.__idMap[id]
        dict = self.__clientAPI.lookupId(id, self.__release, self.__language)
        return self.__createAndAddNewEntity(dict)

    def getLanguage(self) -> str:
        return self.__language

    def getRelease(self) -> str:
        return self.__release

    def _getRealEntity(self, id: str) -> Entity:
        if id in self.__idMap and isinstance(self.__idMap[id], RealEntity):
            return self.__idMap[id]
        return self.__createAndAddNewEntity(
            self.__clientAPI.lookupId(id, self.__release, self.__language)
        )

    # Creates a new entity from its data and updates both dictionaries
    # If new proxy entities are created in the process, they too are added to __idMap
    def __createAndAddNewEntity(self, data: dict) -> Entity:
        id = data["@id"].split("/mms/")[1]
        uri = data["@id"]
        code = data["code"]
        title = data["title"]["@value"]
        definition = ""
        if "definition" in data:
            definition = data["definition"]["@value"]
        longDefinition = ""
        if "longDefinition" in data:
            longDefinition = data["longDefinition"]["@value"]
        fullySpecifiedName = ""
        if "fullySpecifiedName" in data:
            fullySpecifiedName = data["fullySpecifiedName"]["@value"]
        diagnosticCriteria = ""
        if "diagnosticCriteria" in data:
            diagnosticCriteria = data["diagnosticCriteria"]["@value"]
        codingNote = ""
        if "codingNote" in data:
            codingNote = data["codingNote"]["@value"]
        blockId = ""
        if "blockId" in data:
            blockId = data["blockId"]
        codeRange = ""
        if "codeRange" in data:
            codeRange = data["codeRange"]
        classKind = data["classKind"]
        postcoordinationScale: dict[str, list[Entity]] = {}
        if "postcoordinationScale" in data:
            for c in data["postcoordinationScale"]:
                axisName = c["axisName"].split("/schema/")[1]
                postcoordinationScale[axisName] = []
                for e in c["scaleEntity"]:
                    e_id = e.split("/mms/")[1]
                    if e_id in self.__idMap:
                        postcoordinationScale[axisName].append(self.__idMap[e_id])
                    else:
                        new_e = ProxyEntity(self, e_id, c)
                        postcoordinationScale[axisName].append(new_e)
                        self.__idMap[new_e.getId()] = new_e
        children: list[Entity] = []
        newChildren: list[ProxyEntity] = []
        if "child" in data:
            for c in data["child"]:
                c_id = c.split("/mms/")[1]
                if c_id in self.__idMap:
                    children.append(self.__idMap[c_id])
                else:
                    new_e = ProxyEntity(self, c_id, c)
                    newChildren.append(new_e)  # their parent will be updated later
                    children.append(new_e)
                    self.__idMap[new_e.getId()] = new_e
        childrenElsewhere: list[Entity] = []
        if "foundationChildElsewhere" in data:
            for c in data["foundationChildElsewhere"]:
                c_id = c["linearizationReference"].split("/mms/")[1]
                if c_id in self.__idMap:
                    childrenElsewhere.append(self.__idMap[c_id])
                else:
                    new_e = ProxyEntity(self, c_id, c)
                    childrenElsewhere.append(new_e)
                    self.__idMap[new_e.getId()] = new_e
        if classKind == "chapter":
            parent = None
        else:
            p_id = data["parent"][0].split("/mms/")[1]
            if p_id in self.__idMap:
                parent = self.__idMap[p_id]
            else:
                parent = ProxyEntity(self, p_id, data["parent"][0])
                self.__idMap[parent.getId()] = parent
        indexTerm = []
        if "indexTerm" in data:
            for i in data["indexTerm"]:
                indexTerm.append(i["label"]["@value"])
        inclusion = []
        if "inclusion" in data:
            for i in data["inclusion"]:
                inclusion.append(i["label"]["@value"])
        exclusion = []
        if "exclusion" in data:
            for e in data["exclusion"]:
                e_id = e["linearizationReference"].split("/mms/")[1]
                if e_id in self.__idMap:
                    exclusion.append(self.__idMap[e_id])
                else:
                    new_e = ProxyEntity(self, e_id, e["linearizationReference"])
                    exclusion.append(new_e)
                    self.__idMap[new_e.getId()] = new_e
        relatedEntitiesInMaternalChapter = []
        if "relatedEntitiesInMaternalChapter" in data:
            for e in data["relatedEntitiesInMaternalChapter"]:
                e_id = e.split("/entity/")[1]
                if e_id in self.__idMap:
                    relatedEntitiesInMaternalChapter.append(self.__idMap[e_id])
                else:
                    new_e = ProxyEntity(self, e_id, e)
                    relatedEntitiesInMaternalChapter.append(new_e)
                    self.__idMap[new_e.getId()] = new_e
        relatedEntitiesInPerinatalChapter = []
        if "relatedEntitiesInPerinatalChapter" in data:
            for e in data["relatedEntitiesInPerinatalChapter"]:
                e_id = e.split("/entity/")[1]
                if e_id in self.__idMap:
                    relatedEntitiesInPerinatalChapter.append(self.__idMap[e_id])
                else:
                    new_e = ProxyEntity(self, e_id, e)
                    relatedEntitiesInPerinatalChapter.append(new_e)
                    self.__idMap[new_e.getId()] = new_e
        browserUrl = data["browserUrl"]

        if self.__useCodeRangesAsCodes and classKind == "block":
            code = codeRange

        new_e = RealEntity(
            id,
            uri,
            code,
            title,
            definition,
            longDefinition,
            fullySpecifiedName,
            diagnosticCriteria,
            codingNote,
            blockId,
            codeRange,
            classKind,
            postcoordinationScale,
            children,
            childrenElsewhere,
            parent,
            indexTerm,
            inclusion,
            exclusion,
            relatedEntitiesInMaternalChapter,
            relatedEntitiesInPerinatalChapter,
            browserUrl,
        )
        self.__idMap[id] = new_e
        if code != "":
            self.__codeToIdMap[code] = id

        for c in newChildren:
            c._setParent(new_e)

        return new_e
