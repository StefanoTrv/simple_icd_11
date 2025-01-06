The following is the UML class diagram of this library's classes:
![UML class diagram](https://github.com/StefanoTrv/simple_icd_11/blob/master/technical_report/simple_icd_11_UML.svg "UML class diagram")

The `ICDExplorer` class provides the user an interface to the classification, allowing them to search codes and IDs. When created, it ensures that the chosen API can be reached. The `Entity` objects created by the explorer are kept in a map, so that they can be immediately returned if the same entity is needed again.  
The "package-private" method `_getRealEntity()` allows the `ProxyEntity` objects to retrieve a `RealEntity` when needed. Because there is no such thing as a "package-private" visibility in Python, the method is still accessible by the user, but Python's conventions discourage the user from using it; the same applies to the `_setParent()` method of `ProxyEntity`.  
The explorer could be using the official API or another deployment: to manage this, a **strategy pattern** was used. `ICDOfficialAPIClient` is the concrete strategy for communicating with the official API, and `ICDOtherAPIClient` is the concrete strategy for communicating with other deployments of the API. The abstract class `ICDAPIClient` contains no implemented or partially-implemented methods. While there's quite a lot of common code in the two concrete classes, it was decided to keep their implementations separate, since the benefit of not having some duplicate code would not be worth the work of abstracting a common process. The responsibility of creating and initializing the `locationUrl` attribute is left to the subclasses.

Both `ICDOfficialAPIClient` and `ICDOtherAPIClient` implement modified versions of the **singleton pattern**: for `ICDOfficialAPIClient`, only one object is created for each `clientId`; for `ICDOtherAPIClient`, only one object is created for each `locationUrl`.

To represent ICD-11 entities, a **proxy pattern** was used. This allows the user to access seamlessly the parent and the children of any entity, without having to look them up in the API at the moment of the entity's creation. When an entity is first created, each entity related to it (parent and children) that has not already been created is created as a `ProxyEntity` and added to the map of the explorer. When a field the proxy entity doesn't have is accessed, a `RealEntity` is created, if it doesn't already exist, and then accessed. `ProxyEntity` objects may be replaced by their `RealEntity` in some of the data structures where they were stored: the user is warned not to use the `is` operator to compare `Entity` objects, since one of them could be a `ProxyEntity` and the other could be the `RealEntity` for the same code.  
The `Entity` interface is implemented as an abstract class, since Python does not support interfaces. A possibility could have been to use a third party package to implement interfaces, but it would have meant adding an external dependency for little to no advantage.  
The "package-private" method `_setParent()` is used to set the parent of the `ProxyEntity` after the parent itself has been created.

For the maximum flexibility of use for all kinds of users, it was decided to keep all the code in a single file. The code is small enough to be manageable even if contained within a single file.

The only classes exported by the package, and thus visible to the user, are `ICDExplorer` and `Entity`.

The package has a single external dependency: the `requests` library.

The file `test_simple_icd_11.py` contains unit tests for the whole library, using the official API. The file `test_other_API.py` contains a reduced set of unit tests for testing connections with other API deployments.
