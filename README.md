# simple_icd_11
A simple python library for ICD-11 MMS codes

## Index
* [Release notes](#release-notes)
* [Introduction](#introduction)
* [Block codes](#block-codes)
* [Setup](#setup)
* [Documentation](#documentation)
* [ICDExplorer](#icdexplorer)
  * [isValidCode(code : str) -> bool](#isvalidcodecode--str---bool)
  * [isValidId(id : str) -> bool](#isvalididid--str---bool)
  * [getEntityFromCode(code : str) -> Entity](#getentityfromcodecode--str---entity)
  * [getEntityFromId(id : str) -> Entity](#getentityfromidid--str---entity)
  * [getLanguage() -> str](#getlanguage---str)
  * [getRelease() -> str](#getrelease---str)
* [Entity](#entity)
  * [getId() -> str](#getid---str)
  * [getURI() -> str](#geturi---str)
  * [getCode() -> str](#getcode---str)
  * [getTitle() -> str](#gettitle---str)
  * [getDefinition() -> str](#getdefinition---str)
  * [getLongDefinition() -> str](#getlongdefinition---str)
  * [getFullySpecifiedName() -> str](#getfullyspecifiedname---str)
  * [getDiagnosticCriteria() -> str](#getdiagnosticcriteria---str)
  * [getCodingNote(includeFromUpperLevels : bool = False) -> str](#getcodingnoteincludefromupperlevels--bool--false---str)
  * [getBlockId() -> str](#getblockid---str)
  * [getCodeRange() -> str](#getcoderange---str)
  * [getClassKind() -> str](#getclasskind---str)
  * [isResidual() -> bool](#isresidual---bool)
  * [getChildren(includeChildrenElsewhere : bool = False) -> list[Entity]](#getchildrenincludechildrenelsewhere--bool--false---listentity)
  * [getChildrenElsewhere() -> list[Entity]](#getchildrenelsewhere---listentity)
  * [getDescendants(includeChildrenElsewhere : bool = False) -> list[Entity]](#getdescendantsincludechildrenelsewhere--bool--false---listentity)
  * [getParent() -> Entity \| None](#getparent---entity--none)
  * [getAncestors() -> list[Entity]](#getancestors---listentity)
  * [getIndexTerm() -> list[str]](#getindexterm---liststr)
  * [getInclusion() -> list[str]](#getinclusion---liststr)
  * [getExclusion(includeFromUpperLevels : bool = True) -> list[Entity]](#getexclusionincludefromupperlevels--bool--true---listentity)
  * [getRelatedEntitiesInMaternalChapter() -> list[Entity]](#getrelatedentitiesinmaternalchapter---listentity)
  * [getRelatedEntitiesInPerinatalChapter() -> list[Entity]](#getrelatedentitiesinperinatalchapter---listentity)
  * [getPostcoordinationScale() -> list[PostcoordinationAxis]](#getpostcoordinationscale---listpostcoordinationaxis)
  * [getBrowserUrl() -> str](#getbrowserurl---str)
* [PostcoordinationAxis](#postcoordinationaxis)
  * [getAxisName() -> str](#getaxisname---str)
  * [getRequiredPostCoordination() -> bool](#getrequiredpostcoordination---bool)
  * [getAllowMultipleValues() -> str](#getallowmultiplevalues---str)
  * [getScaleEntity() -> list[Entity]](#getscaleentity---listentity)
* [Conclusion](#conclusion)

## Release notes
* **1.1.0:** Removed the useless and dangerous ability to modify a correct clientSecret (useless because the official API does not allow to change the clientSecret of a given clientId). Under some very specific circumstances, an "ICDExplorer" could have sent to the API two requests for the same code: this has now been fixed. Improved the performance of three methods of "Entity".
* **1.0.0:** Initial release

## Introduction
This library aims to offer an easier way to work with codes and entities from **ICD-11 MMS**, that is the Mortality and Morbidity Statistics linearization of ICD-11. For simplicity's sake, from now on I'll refer to this linearization as simply ICD-11. It allows users to connect to the official WHO API for ICD-11 or to unofficial deployments of the API, choose the preferred available language and release (or just use the latest release), check if a code exists and see most of the data associated with it, including its ancestors and descendants in the classification.  
The way this library achieves its purpose is by providing simplified access to some of the information provided by the [ICD-11 API](https://icd.who.int/icdapi) released by the WHO. The library also allows access to other deployments of the API, for example local deployments. It should be noted that using a local deployment of the API will always be faster than connecting to the official one. To learn more, read the [Setup](#setup) section.  
To reduce the overhead of getting the data of entities, each entity is looked up in the API only once and its value is then cached for subsequent calls. This is completely transparent to the user, with the only perceivable difference being the overhead time of the first method call compared to the following ones.  
Not all of the functionalities of the API are included in this library. First of all, this library only deals with the ICD-11 MMS linearization, while the API allows to also explore ICD-10 codes and foundation entities. Also, the API provides, for the ICD-11 entities, some data that is not made available in this library. For example: foundation entities are not supported, even when they appear in relation to ICD-11 MMS entities; and when in the data of an entity provided by the API there's a list of other labeled entities, this library lists the entities without their context-specific label. While the functionalities offered by this library should be sufficient for the needs of the great majority of the use-cases, if you find that something that you need is missing, including the functionalities I just mentioned, feel free to let me know. See the [Documentation](#documentation) for the details of the available functionalities.  
If you need to learn more about the meaning of the various fields of the ICD-11 entities, please see the [official ICD-11 reference guide](https://icdcdn.who.int/icd11referenceguide/en/html/index.html) and the [ICD schema](https://icd.who.int/icdapi/docs/ICD-schema.html). The paragraph on ICD-11 MMS in the [Wikipedia page for ICD-11](https://en.wikipedia.org/wiki/ICD-11#ICD-11_MMS) may be informative on the classification as a whole. Sadly, there's no place where to find a complete and exhaustive explanation of these fields, some other pieces of information can be found in the [Swagger documentation of the API](https://id.who.int/swagger/index.html) (scroll to the bottom and see LinearizationEntity).  
If you are looking for a library to manage ICD-10 or ICD-10 CM codes, you can check out, respectively, the [simple_icd_10](https://github.com/StefanoTrv/simple_icd_10) and the [simple_icd_10_CM](https://github.com/StefanoTrv/simple_icd_10_CM) libraries.
Please, feel free to contact me for suggestions, feature requests and, especially, bug reports. You can also contact me if you need any help with this library, especially if you find that something in this document is not clear enough. I will, however, probably be unable to help with issues strictly related to the classification or with the use or setup of the API. If you feel like supporting me, please check out the [Conclusion](#conclusion) section.  
simple_icd_11 is licensed under [the MIT License](https://github.com/StefanoTrv/simple_icd_11/blob/master/LICENSE).

## Block codes
There are four types of entities in the ICD-11 MMS classification: chapters, blocks, categories and windows (see [the Wikipedia page](https://en.wikipedia.org/wiki/ICD-11#ICD-11_MMS) for more information on these different types). In the API only chapters and categories have codes, while the codes for blocks and windows are empty strings. The API gives blocks a special field called `BlockId`, which provides unique codes for blocks. However, these IDs are unsearchable in the API, making them unusable in the context of the API (the only way to make them usable would require downloading the whole classification first). By default, in this library blocks do not have a code, but it's possible to set a parameter of an `ICDExplorer` object so that the code ranges are used as codes for the blocks: if this parameter is set to true, all the methods of that object will behave as if the codes of blocks were identical to their block ranges. See [ICDExplorer](#icdexplorer) to learn more about the parameters available when creating an explorer object. Code ranges remain accessible either way through the [getCodeRange()](#getcoderange---str) method. The codes for windows are always empty regardless.

## Setup
You can install the package with pip, using this command:
```bash
pip install simple-icd-11
```
Then you need to import it, just as with any other package:
```python
from simple_icd_11 import *
```
For maximum simplicity and flexibility of use, the whole library was written in a single file. You can thus, instead of installing the package through pip, use the file [simple_icd_11.py](https://github.com/StefanoTrv/simple_icd_11/blob/master/simple_icd_11.py).  
The distribution files are also available as [releases in the Github repository](https://github.com/StefanoTrv/simple_icd_11/releases).

To connect with an API, you'll have to create an `ICDExplorer` object. The parameters for initializing the explorer vary based on the API deployment you want to use. To learn more about all the parameters you can use when initializing an explorer, see [ICDExplorer](#icdexplorer). After being initialized, the explorer behaves the same way regardless of the API related parameters it was set to use.

To use the library with the **official API**, you'll first need to create some credentials by registering on the [ICD API website](https://icd.who.int/icdapi); your keys will be accessible [here](https://icd.who.int/icdapi/Account/AccessKey). You'll then have to pass the credentials to the constructor, as follows:
```python
clientId = "" #your client id
clientSecret = "" #your client secret
language = "en" #or any other supported language
explorer = ICDExplorer(language,clientId,clientSecret)
```
The client ID and the client secret will be stored to automatically re-authenticate when needed.

To use the library with **another deployment** of the API, you'll need to pass the URL location of the deployment to the constructor. If you want to learn how to create your own local deployment of the API, check out the [official guide](https://icd.who.int/docs/icd-api/ICDAPI-LocalDeployment/). As mentioned earlier, a local deployment of the API will always be faster than the official one. The optional parameter `customUrl` contains the location of the API deployment; it is set to `None` by default, but when given a string value the resulting explorer will connect to a non-official API instead of the official one. The parameters for the client id and client secret are still needed, but they will be ignored because non-official deployments of the API do not support any authentication: you can set them to empty strings or to any value you want.
```python
url = "" #location of your API
language = "en" #or any other supported language
explorer = ICDExplorer(language,"","",customUrl=url)
```
For example, initializing the explorer for an API installed as a Docker Container as described in the [official website](https://icd.who.int/docs/icd-api/ICDAPI-DockerContainer/) will look like this:

```python
language = "en" #or any other supported language
explorer = ICDExplorer(language,"","",customUrl="http://localhost/")
```

## Documentation
The library exposes three kinds of objects to the user: `ICDExplorer`, `Entity` and `PostcoordinationAxis`. Here follows the documentation for these three classes.

## ICDExplorer
The `ICDExplorer` class interacts with the API to retrieve, parse, and store the data of the ICD-11 entities. You can use it to look up codes and IDs, and it will return `Entity` objects containing the data of the entity that has such code or id.  
The constructor for an `ICDExplorer` object has three required arguments and three optional arguments. The required arguments are, in this order:
* **language : str** the language code representing the language you want the API to answer in. The code for English is `en`.
* **clientId : str** the client ID for accessing the official API. It can be an empty string if using another deployment of the API. See [Setup](#setup) for more details.
* **clientSecret : str** the client secret for accessing the official API. It can be an empty string if using another deployment of the API. See [Setup](#setup) for more details.

The optional arguments are the following:
* **release : str | None = None** the ICD-11 MMS release you want to use. By default, it uses the latest release made available by the API.
* **customUrl : str | None = None** the URL of the non-official deployment of the API. By default it's `None`: if left `None`, it will use the official API. See [Setup](#setup) for more details.
* **useCodeRangesAsCodes : bool = False** whether the code ranges of blocks will be used as their codes or not. By default, only the official codes are used. See [Block codes](#block-codes) for more details.

You can create as many explorers as you want, using the same or different deployments and the same or different credentials.
The constructor will raise a `ConnectionError` if an error happens while trying to establish a connection, and a `LookupError` if it can't find the specified version and language combination.

All the following methods will throw a `ConnectionError` if an error happens while trying to communicate with the API.

### isValidCode(code : str) -> bool
Returns `True` if the given string is a valid ICD-11 code for this explorer instance, otherwise it returns `False`. 
```python
explorer.isValidCode("8B25.4")
# True
explorer.isValidCode("cat")
# False
```

### isValidId(id : str) -> bool
Returns `True` if the given string is a valid ICD-11 ID for this explorer instance, otherwise it returns `False`. 
```python
explorer.isValidId("183230446")
# True
explorer.isValidId("cat")
# False
```

### getEntityFromCode(code : str) -> Entity
Returns an `Entity` object representing the entity corresponding to the given ICD-11 code. Raises a `LookupError` if the code is not valid for this explorer's parameters.
```python
entity = explorer.getEntityFromCode("6A41")
entity.getTitle()
# "Catatonia induced by substances or medications"
```

### getEntityFromId(id : str) -> Entity
Returns an `Entity` object representing the entity corresponding to the given ICD-11 ID. Raises a `LookupError` if the ID is not valid for this explorer's parameters.
```python
entity = explorer.getEntityFromId("289492002")
entity.getTitle()
# "Catatonia induced by substances or medications"
```

### getLanguage() -> str
Returns the language code of the language used by this explorer instance (e.g., `"en"` for English). 
```python
explorer.getLanguage()
# "en" # if the language is English
```

### getRelease() -> str
Returns the name of the release used by this explorer instance. 
```python
explorer.getRelease()
# "2024-01"
```

## Entity
`Entity` objects represent single entities in the classification. They have methods for accessing their various fields.  
The methods return empty strings or lists for fields that the entity does not have: for example, using the `getBlockId()` method on an `Entity` representing a category will return an empty string, even though such a field has no meaning for a category.  
You should never use the `is` operator to compare two `Entity` objects: because of the way they are implemented, they could be two different objects representing the same entity. You should instead compare their IDs. Also remember that `Entity` objects retrieved from explorers initialized with different parameters may have the same ID but contain different data.  
All the lists returned by these methods can be safely modified.

### getId() -> str
Returns a string containing the ID of the entity.

### getURI() -> str
Returns the URI of the entity. To be consistent with the [official documentation for local deployments](https://icd.who.int/docs/icd-api/ICDAPI-LocalDeployment/), the URIs of the entities always point to the official API, that is URIs always start with `http://id.who.int/icd/`.

### getCode() -> str
Returns the code of the entity.

### getTitle() -> str
Returns the title of the entity.

### getDefinition() -> str
Returns the definition of the entity.

### getLongDefinition() -> str
Returns the long definition of the entity.

### getFullySpecifiedName() -> str
Returns the fully specified name of the entity.

### getDiagnosticCriteria() -> str
Returns the diagnostic criteria of the entity. When present, this field usually consists of a very long string.

### getCodingNote(includeFromUpperLevels : bool = False) -> str
Returns the coding note of the entity. If the optional argument `includeFromUpperLevels` is set to `True`, the returned string will also contain the coding notes of the entity's ancestors. The coding notes of the farthest ancestors will appear first in the string, while the coding note of the entity itself will be at the end of the string. By default, `includeFromUpperLevels` is `False`.

### getBlockId() -> str
Returns the block ID of the entity.

### getCodeRange() -> str
Returns the code range of the entity.

### getClassKind() -> str
Returns the class kind of the entity. It can be `"chapter"`, `"block"`, `"category"` or `"window"`. See [the Wikipedia page](https://en.wikipedia.org/wiki/ICD-11#ICD-11_MMS) for more information on these different types.

### isResidual() -> bool
Returns `True` if the entity is a residual category, otherwise it returns `False`. See [the Wikipedia page](https://en.wikipedia.org/wiki/ICD-11#ICD-11_MMS) for more information on residual categories.

### getChildren(includeChildrenElsewhere : bool = False) -> list[Entity]
Returns a list of entities containing the children of this entity. By default, only the "real" children of the entity are included in the list; by setting the optional argument `includeChildrenElsewhere` to `True`, the list will also include windows and the children whose parent is another entity, the so called "gray nodes" described in [the Wikipedia page](https://en.wikipedia.org/wiki/ICD-11#ICD-11_MMS).

### getChildrenElsewhere() -> list[Entity]
Returns a list containing the children of this entity that are either windows or whose parent is another entity, the so called "gray nodes" described in [the Wikipedia page](https://en.wikipedia.org/wiki/ICD-11#ICD-11_MMS).

### getDescendants(includeChildrenElsewhere : bool = False) -> list[Entity]
Returns a list containing the descendants of this entity. For the meaning of the optional argument `includeChildrenElsewhere`, please see the documentation for [getChildren()](#getchildrenincludechildrenelsewhere--bool--false---listentity).

### getParent() -> Entity | None
Returns the parent entity of this entity. If this entity is a chapter, it returns `None`.

### getAncestors() -> list[Entity]
Returns a list of all the ancestors of this entity, ordered from the closest to the furthest.

### getIndexTerm() -> list[str]
Returns the list of index terms for this entity.

### getInclusion() -> list[str]
Returns the list of inclusion terms for this entity.

### getExclusion(includeFromUpperLevels : bool = True) -> list[Entity]
Returns the list of exclusion entities of this entity.

### getRelatedEntitiesInMaternalChapter() -> list[Entity]
Returns the list of related entities in the maternal chapter for this entity.

### getRelatedEntitiesInPerinatalChapter() -> list[Entity]
Returns the list of related entities in the perinatal chapter for this entity.

### getPostcoordinationScale() -> list[PostcoordinationAxis]
Returns a list of `PostcoordinationAxis` objects representing the post-coordination scale of the entity. For more information on the `PostcoordinationAxis` class, see [PostcoordinationAxis](#postcoordinationaxis).

### getBrowserUrl() -> str
Returns the browser URL of this entity. Unlike the URI, if another deployment is being used, the browser URL will point to that specific deployment.

## PostcoordinationAxis
`PostcoordinationAxis` is a simple class that represents individual postcoordination axes of `Entity` objects. The [`getPostcoordinationScale()`](#getpostcoordinationscale---listpostcoordinationaxis) method of the `Entity` class returns the list of `PostcoordinationAxis` objects for the given entity.

### getAxisName() -> str
Returns the name of the axis. While in the official API the name of an axis is its whole URI, here the name is only the final part of the URI. This is also different from the axis name that is displayed in the official ICD-11 MMS browser.  
For example, the postcoordination axis for the "6D70.0" code is named "*Has causing condition*" in the browser, "*http\://id.who.int/icd/schema/hasCausingCondition*" in the official API and "*hasCausingCondition*" in this package.

### getRequiredPostCoordination() -> bool
Returns `True` if this is a required postcoordination axis, `False` if it is optional.

### getAllowMultipleValues() -> str
Returns a string describing the behaviour of this postcoordination axis. As per the official [Swagger documentation](https://id.who.int/swagger/index.html):
>* `"AllowAlways"` means the user [can] post-coordinate multiple times using this axis;
>* `"NotAllowed"` means the user [can] only post-coordinate once using this axis;
>* `"AllowedExceptFromSameBlock"` means multiple values are allowed only if they are coming from different blocks within the value set.

### getScaleEntity() -> list[Entity]
Returns the list of allowed entities for postcoordination. This list can be safely modified. Keep in mind this note from the official [Swagger documentation](https://id.who.int/swagger/index.html):
> these are hierarchical starting points of the allowed value set. i.e. any descendant of the entities provided [here] can be used during postcoordination.

## Conclusion
This should be everything you need to know about the simple_icd_11 library. Please contact me if you find any mistake, bug, missing feature or anything else that could be improved or made easier to understand, both in this documentation and in the library itself.

If you find this library useful and are feeling generous, consider making a donation using one of the methods listed at the end of this document.

*Stefano Travasci*

---

Paypal: [![Donate](https://www.paypalobjects.com/en_US/i/btn/btn_donate_LG.gif)](https://www.paypal.com/donate?hosted_button_id=9HMMFAZE248VN)

Bitcoin: bc1qcmn4tp8e58zkzygjpwz3e630hjfpq8gk62h4nx

<sub>*let me know if your favorite donation method is not in this list*</sub>
