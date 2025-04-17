import unittest, time
from simple_icd_11 import ICDOfficialAPIClient, ICDExplorer, ProxyEntity, RealEntity

class TestICDOfficialAPIClient(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        f = open("api_credentials.txt", "r")
        cls.clientId = f.readline().strip()
        cls.clientSecret = f.readline().strip()
        f.close()
        cls.client = ICDOfficialAPIClient(cls.clientId,cls.clientSecret)
    
    def compromiseToken(self):
        if(self.client._ICDOfficialAPIClient__token[-1]=="A"): # type: ignore
            self.client._ICDOfficialAPIClient__token = self.client._ICDOfficialAPIClient__token[:-1]+"B" # type: ignore
        else:
            self.client._ICDOfficialAPIClient__token = self.client._ICDOfficialAPIClient__token[:-1]+"A" # type: ignore
        if(self.client._ICDOfficialAPIClient__token[0]=="w"): # type: ignore
            self.client._ICDOfficialAPIClient__token = "a"+self.client._ICDOfficialAPIClient__token[1:] # type: ignore
        else:
            self.client._ICDOfficialAPIClient__token = "w"+self.client._ICDOfficialAPIClient__token[1:] # type: ignore
    
    def testLookupCodeOk(self):
        json_dict = self.client.lookupCode("1F0Y","2024-01","en")
        self.assertEqual(json_dict["code"],"1F0Y")
        self.assertEqual(json_dict["@id"],"http://id.who.int/icd/release/11/2024-01/mms/1646490591/other")
    
    def testLookupCodeNotExists(self):
        with self.assertRaises(LookupError):
            self.client.lookupCode("banana","2024-01","en")
    
    def testLookupCodeOkOldToken(self):
        self.compromiseToken()
        json_dict = self.client.lookupCode("1F0Y","2024-01","en")
        self.assertEqual(json_dict["code"],"1F0Y")
        self.assertEqual(json_dict["@id"],"http://id.who.int/icd/release/11/2024-01/mms/1646490591/other")
    
    def testLookupIdOk(self):
        json_dict = self.client.lookupId("218513628","2024-01","en")
        self.assertEqual(json_dict["code"],"9B71.1")
        self.assertEqual(json_dict["@id"],"http://id.who.int/icd/release/11/2024-01/mms/218513628")
    
    def testLookupIdNotExists(self):
        with self.assertRaises(LookupError):
            self.client.lookupId("5","2024-01","en")
    
    def testLookupIdOkOldToken(self):
        self.compromiseToken()
        json_dict = self.client.lookupId("218513628","2024-01","en")
        self.assertEqual(json_dict["code"],"9B71.1")
        self.assertEqual(json_dict["@id"],"http://id.who.int/icd/release/11/2024-01/mms/218513628")

    def testGetLatestReleaseOk(self): #needs to be updated when new release comes out
        self.assertEqual(self.client.getLatestRelease("en"),"2025-01")
    
    def testGetLatestReleaseWrongLanguage(self):
        with self.assertRaises(LookupError):
            self.client.getLatestRelease("onion")
    
    def testGetLatestReleaseOldToken(self): #needs to be updated when new release comes out
        self.compromiseToken()
        self.assertEqual(self.client.getLatestRelease("en"),"2025-01")
    
    def testCheckReleaseTrue(self):
        self.assertTrue(self.client.checkRelease("2024-01","en"))
    
    def testCheckReleaseFalse(self):
        self.assertFalse(self.client.checkRelease("3124-01","en"))
    
    def testCheckReleaseOldToken(self):
        self.compromiseToken()
        self.assertTrue(self.client.checkRelease("2024-01","en"))

    def testNoDuplicateInstances(self):
        t = ICDOfficialAPIClient(self.clientId,self.clientSecret)
        self.assertTrue(self.client is t)



class TestProxyEntity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        f = open("api_credentials.txt", "r")
        clientId = f.readline().strip()
        clientSecret = f.readline().strip()
        f.close()
        cls.explorer = ICDExplorer("en",clientId,clientSecret,release="2024-01")
    
    def testNoLookup(self):
        fake_uri = "it.wikipedia.org/wiki/Convento_dei_Domenicani_(Pordenone)"
        prx = ProxyEntity(self.explorer,"557175275",fake_uri)
        self.assertEqual(prx.getURI(),fake_uri)
    
    def testDoesLookup(self):
        prx = ProxyEntity(self.explorer,"557175275","icd.who.int/browse/2024-01/mms/557175275")
        self.assertEqual(prx.getCode(),"8B25.4")



class TestICDExplorer(unittest.TestCase): #tests also RealEntity
    @classmethod
    def setUpClass(cls):
        f = open("api_credentials.txt", "r")
        cls.clientId = f.readline().strip()
        cls.clientSecret = f.readline().strip()
        f.close()
        cls.explorer = ICDExplorer("en",cls.clientId,cls.clientSecret,release="2024-01")
        cls.explorerCodeRanges = ICDExplorer("en",cls.clientId,cls.clientSecret,release="2024-01",useCodeRangesAsCodes=True)

    def testIsValidCode(self):
        self.assertFalse(self.explorer.isValidCode("8B10-8B1Z"))
        self.assertTrue(self.explorerCodeRanges.isValidCode("8B10-8B1Z"))
        self.assertTrue(self.explorerCodeRanges.isValidCode("5C90.2"))
        self.assertTrue(self.explorer.isValidCode("5C90.2"))
        self.assertTrue(self.explorerCodeRanges.isValidCode("02"))
        self.assertTrue(self.explorer.isValidCode("02"))
        self.assertFalse(self.explorerCodeRanges.isValidCode("banana"))
        self.assertFalse(self.explorer.isValidCode("banana"))
    
    def testIsValidId(self):
        self.assertTrue(self.explorer.isValidId("183230446"))
        self.assertTrue(self.explorer.isValidId("1042184245/unspecified"))
        self.assertFalse(self.explorer.isValidId("cipolla"))

    def testGetEntityFromCode(self):
        e = self.explorer.getEntityFromCode("5C90.0")
        self.assertEqual(e.getId(),"831518052")
        e = self.explorerCodeRanges.getEntityFromCode("5A00-5B3Z")
        self.assertEqual(e.getId(),"461716838")
        with self.assertRaises(LookupError):
            self.explorer.getEntityFromCode("5A00-5B3Z")

    def testGetEntityFromId(self):
        e = self.explorer.getEntityFromId("831518052")
        self.assertEqual(e.getCode(),"5C90.0")
        with self.assertRaises(LookupError):
            self.explorer.getEntityFromId("5A00-5B3Z")
    
    def testGetLanguage(self):
        self.assertEqual(self.explorer.getLanguage(),"en")
    
    def testGetRelease(self):
        self.assertEqual(self.explorer.getRelease(),"2024-01")
    
    def testWrongLanguage(self):
        with self.assertRaises(LookupError):
            ICDExplorer("klingon",self.clientId,self.clientSecret,release="2024-01")
    
    def testWrongRelease(self):
        with self.assertRaises(LookupError):
            ICDExplorer("en",self.clientId,self.clientSecret,release="3034-01")
    
    def testGetId(self):
        e = self.explorer.getEntityFromCode("2B30")
        self.assertEqual(e.getId(),"1528863768")
    
    def testGetURI(self):
        e = self.explorer.getEntityFromCode("2B30")
        self.assertEqual(e.getURI(),"http://id.who.int/icd/release/11/2024-01/mms/1528863768")
    
    def testGetCode(self):
        e = self.explorer.getEntityFromCode("2B30")
        self.assertEqual(e.getCode(),"2B30")
    
    def testGetTitle(self):
        e = self.explorer.getEntityFromCode("2B30")
        self.assertEqual(e.getTitle(),"Hodgkin lymphoma")
    
    def testGetDefinition(self):
        e = self.explorer.getEntityFromCode("2B30")
        self.assertEqual(e.getDefinition(),"Malignant lymphomas, previously known as Hodgkin's disease, characterised by the presence of large tumour cells in an abundant admixture of nonneoplastic cells. There are two distinct subtypes: nodular lymphocyte predominant Hodgkin lymphoma and classical Hodgkin lymphoma. Hodgkin lymphoma involves primarily lymph nodes.")
    
    def testGetLongDefinition(self):
        e = self.explorer.getEntityFromCode("2B30")
        self.assertEqual(e.getLongDefinition(),"")
        e = self.explorer.getEntityFromCode("3A50.2")
        self.assertEqual(e.getLongDefinition(),"Beta-thalassaemia (BT) is marked by deficiency (B+) or absence (B0) of synthesis of the beta globulin chain of the haemoglobin (Hb) protein. Prevalence is unknown but incidence at birth of the severe form is estimated at 100,000/year. The disease was initially described in the Mediterranean basin but severe forms of BT occur throughout the Middle East, South East Asia, India and China. Population migration has lead to global distribution of the disease. Three types of BT have been described. 1) Thalassaemia minor (BT-minor) is the heterozygous form and is usually asymptomatic. 2) Thalassaemia major (Cooley anaemia; BT-major) is the homozygous form and is associated with microcytic and hypochromic anaemia resulting from dyserythropoiesis and haemolysis. Splenomegaly is also present. Onset occurs from 6-24 months of age. The severe anaemia requires systematic transfusions to maintain Hb levels within the range of 90-100 g/L and allow normal activity. Transfusion of red cell concentrates results in iron overload which hampers the vital prognosis (due to cardiac involvement) and causes significant morbidity (due to endocrinal and hepatic manifestations). 3) Thalassaemia intermedia (BTI) groups together around 10% of homozygous disease forms with numerous compound heterozygous forms. The degree of anaemia in BTI is variable, but is less severe and is diagnosed later than that in BT-major. Patients with BTI may or may not require occasional transfusions. Hypersplenism, biliary lithiasis, extramedullary haematopoiesis, thrombotic complications and progressive iron overload may occur. Diagnosis of BT relies on analysis of Hb by electrophoresis or HPLC. In BT-major, HbA is absent or greatly reduced and HbF predominates. In BT-minor, the levels of Hb A2 are increased and the levels Hb are usually normal with microcytic and hypochromic pseudopolycythaemia. Transmission is autosomal recessive and around 200 mutations (B0 or B+) have been identified. Genetic counselling is recommended for characterising the mutation, preparing management for the affected child and, in some cases, for prenatal diagnosis. There are two lines of treatment for BT. 1) A combination of transfusions and chelators (early and regular parenteral deferoxamine has led to increased survival during the last 30 years). Oral administration of active iron chelators and surveillance of tissue iron overload by MRI will probably result in further improvements but long-term follow-up is needed to evaluate impact on morbidity and mortality. In 2006, deferasirox obtained EU marketing authorisation as an Orphan drug for treatment of BT. Despite its cardioprotective properties, the marketing authorisation for deferasirox is restricted to cases in which treatment with deferoxamine fails or is contraindicated. 2) Haematopoietic stem cell transplant is the only curative treatment for BT: results are very favourable for children with HLA-identical familial donors.")

    def testFullySpecifiedName(self):
        # couldn't find any example with a non-empty field!
        e = self.explorer.getEntityFromCode("2B30")
        self.assertEqual(e.getFullySpecifiedName(),"")
    
    def testDiagnosticCriteria(self):
        e = self.explorer.getEntityFromCode("6E40")
        self.assertIn("# 6E40 General Diagnostic Requirements for Psychological or Behavioural Factors Affecting Disorders or Diseases Classified Elsewhere \n\n## Essential",e.getDiagnosticCriteria())

    def testGetCodingNote(self):
        # could not find an example with a non-empty field!
        e = self.explorer.getEntityFromId("2019647878")
        self.assertEqual(e.getCodingNote(),"")
        self.assertEqual(e.getCodingNote(includeFromUpperLevels=True),"")
    
    def testGetBlockId(self):
        e = self.explorer.getEntityFromId("2019647878")
        self.assertEqual(e.getBlockId(),"")
        e = self.explorer.getEntityFromId("1147802348")
        self.assertEqual(e.getBlockId(),"BlockL2-2A3")
    
    def testGetCodeRange(self):
        e = self.explorer.getEntityFromId("2019647878")
        self.assertEqual(e.getCodeRange(),"")
        e = self.explorer.getEntityFromId("1147802348")
        self.assertEqual(e.getCodeRange(),"2A30-2A3Z")
    
    def testGetClassKind(self):
        e = self.explorer.getEntityFromCode("13")
        self.assertEqual(e.getClassKind(),"chapter")
        e = self.explorer.getEntityFromId("1594312948")
        self.assertEqual(e.getClassKind(),"block")
        e = self.explorer.getEntityFromCode("DA24")
        self.assertEqual(e.getClassKind(),"category")
        e = self.explorer.getEntityFromId("1503334455")
        self.assertEqual(e.getClassKind(),"window")
    
    def testIsResidual(self):
        e = self.explorer.getEntityFromCode("13")
        self.assertFalse(e.isResidual())
        e = self.explorer.getEntityFromCode("DA2Y")
        self.assertTrue(e.isResidual())
        e = self.explorer.getEntityFromCode("DA2Z")
        self.assertTrue(e.isResidual())
    
    def testGetChildren(self):
        # empty
        e = self.explorer.getEntityFromCode("DA24.00")
        self.assertEqual(len(e.getChildren()),0)
        # children
        e = self.explorer.getEntityFromId("1540965840")
        children = e.getChildren()
        self.assertEqual(len(children),5)
        correct_children = ["1917562684","21063503","524771725","1540965840/other","1540965840/unspecified"]
        for c in children:
            self.assertIn(c.getId(),correct_children)
            correct_children.remove(c.getId())
        # children with elsewhere
        children = e.getChildren(includeChildrenElsewhere=True)
        self.assertEqual(len(children),6)
        correct_children = ["1917562684","21063503","524771725","1540965840/other","1540965840/unspecified","2140459587"]
        for c in children:
            self.assertIn(c.getId(),correct_children)
            correct_children.remove(c.getId())
    
    def testGetChildrenElsewhere(self):
        # empty
        e = self.explorer.getEntityFromCode("DA24.00")
        self.assertEqual(len(e.getChildrenElsewhere()),0)
        # children elsewhere
        e = self.explorer.getEntityFromId("1540965840")
        children = e.getChildrenElsewhere()
        self.assertEqual(len(children),1)
        self.assertEqual(children[0].getId(),"2140459587")
    
    def testGetDescendants(self):
        # empty
        e = self.explorer.getEntityFromCode("DA24.00")
        self.assertEqual(len(e.getDescendants()),0)
        # descendants
        e = self.explorer.getEntityFromId("1189893025")
        descendants = e.getDescendants()
        self.assertEqual(len(descendants),1)
        self.assertEqual(descendants[0].getId(),"566170052")
        # descendants with elsewhere
        descendants = e.getDescendants(includeChildrenElsewhere=True)
        self.assertEqual(len(descendants),7)
        correct_descendants = ["566170052","1529247463","605819742","765928537","1822281676","1529247463/other","1529247463/unspecified"]
        for d in descendants:
            self.assertIn(d.getId(),correct_descendants)
            correct_descendants.remove(d.getId())

    def testGetParent(self):
        e = self.explorer.getEntityFromCode("X")
        self.assertTrue(e.getParent() is None)
        e = self.explorer.getEntityFromId("120848300")
        self.assertEqual(e.getParent().getCode(),"9C81") # type: ignore
    
    def testGetAncestors(self):
        e = self.explorer.getEntityFromCode("X")
        self.assertEqual(e.getAncestors(),[])
        e = self.explorer.getEntityFromId("120848300")
        ancestors = e.getAncestors()
        correct_ancestors = ["1979741228","1060046426","868865918"]
        self.assertEqual(len(ancestors),3)
        for a in ancestors:
            self.assertIn(a.getId(),correct_ancestors)
            correct_ancestors.remove(a.getId())

    def testGetIndexTerm(self):
        e = self.explorer.getEntityFromId("2003830496")
        correct_terms = ["Follicular lymphoma grade 2", "mixed nodular lymphoma", "follicular reticulolymphosarcoma", "nodular reticulolymphosarcoma", "small and large cleaved cell follicular lymphoma", "mixed lymphocytic histiocytic nodular lymphoma", "follicular malignant lymphoma of mixed cell type", "mixed small cleaved and large cell follicular malignant lymphoma", "malignant nodular lymphoma of mixed lymphocytic-histiocytic", "malignant nodular lymphoma of mixed cell type", "follicular non Hodgkin lymphoma of mixed small cleaved cell and large cell", "cleaved large cell follicular lymphoma", "follicular germinoblastoma", "follicular lymphosarcoma of mixed cell type", "nodular lymphoma of mixed cell type of lymphocytic-histiocytic"]
        terms = e.getIndexTerm()
        self.assertEqual(len(terms),len(correct_terms))
        for t in terms:
            self.assertIn(t,correct_terms)
            correct_terms.remove(t)

    def testGetInclusion(self):
        e = self.explorer.getEntityFromId("2055968951")
        correct_inclusions = ["moniliasis","candidiasis"]
        inclusions = e.getInclusion()
        self.assertEqual(len(inclusions),len(correct_inclusions))
        for i in inclusions:
            self.assertIn(i,correct_inclusions)
            correct_inclusions.remove(i)

    def testGetExclusion(self):
        e = self.explorer.getEntityFromId("1793762788")
        correct_exclusions = ["1C14","1C15","NE83.1"]
        exclusions = e.getExclusion()
        self.assertEqual(len(exclusions),len(correct_exclusions))
        for ex in exclusions:
            self.assertIn(ex.getCode(),correct_exclusions)
            correct_exclusions.remove(ex.getCode())
        # without including upper levels
        correct_exclusions = ["1C14","1C15"]
        exclusions = e.getExclusion(includeFromUpperLevels=False)
        self.assertEqual(len(exclusions),len(correct_exclusions))
        for ex in exclusions:
            self.assertIn(ex.getCode(),correct_exclusions)
            correct_exclusions.remove(ex.getCode())

    def testGetRelatedEntitiesInMaternalChapter(self):
        e = self.explorer.getEntityFromId("1994012056")
        rl = e.getRelatedEntitiesInMaternalChapter()
        self.assertEqual(len(rl),1)
        self.assertEqual(rl[0].getId(),"1320597992")

    def testGetRelatedEntitiesInPerinatalChapter(self):
        e = self.explorer.getEntityFromId("1994012056")
        rl = e.getRelatedEntitiesInPerinatalChapter()
        self.assertEqual(len(rl),1)
        self.assertEqual(rl[0].getId(),"1270001765")

    def testGetBrowserUrl(self):
        e = self.explorer.getEntityFromCode("V")
        self.assertEqual(e.getBrowserUrl(),"https://icd.who.int/browse/2024-01/mms/en#231358748")
        e = self.explorer.getEntityFromId("2091156678")
        self.assertEqual(e.getBrowserUrl(),"https://icd.who.int/browse/2024-01/mms/en#2091156678")

    def testGetRealEntityNoDuplicateRequests(self):
        explorer = ICDExplorer("en",self.clientId,self.clientSecret,release="2024-01")
        explorer.getEntityFromId("1345814274")
        proxy_entity = explorer.getEntityFromId("377572273")
        self.assertIsInstance(proxy_entity,ProxyEntity)
        entity1 = explorer._getRealEntity("377572273")
        self.assertIsInstance(entity1,RealEntity)
        entity2 = explorer._getRealEntity("377572273")
        self.assertIsInstance(entity2,RealEntity)
        self.assertEqual(id(entity1),id(entity2))
