import unittest, time
from simple_icd_11 import ICDOtherAPIClient, ICDExplorer, ProxyEntity

url = "http://localhost/"

# Class for testing the API client for unofficial deployments
class TestICDOtherAPIClient(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = ICDOtherAPIClient(url)
    
    def testWrongUrl(self):
        with self.assertRaises(ConnectionError):
            ICDOtherAPIClient("website.invalid")
    
    def testLookupCodeOk(self):
        json_dict = self.client.lookupCode("1F0Y","2024-01","en")
        self.assertEqual(json_dict["code"],"1F0Y")
        self.assertEqual(json_dict["@id"],"http://id.who.int/icd/release/11/2024-01/mms/1646490591/other")
    
    def testLookupCodeNotExists(self):
        with self.assertRaises(LookupError):
            self.client.lookupCode("banana","2024-01","en")
    
    def testLookupIdOk(self):
        json_dict = self.client.lookupId("218513628","2024-01","en")
        self.assertEqual(json_dict["code"],"9B71.1")
        self.assertEqual(json_dict["@id"],"http://id.who.int/icd/release/11/2024-01/mms/218513628")
    
    def testLookupIdNotExists(self):
        with self.assertRaises(LookupError):
            self.client.lookupId("5","2024-01","en")

    def testGetLatestReleaseOk(self): #needs to be updated when new release comes out
        self.assertEqual(self.client.getLatestRelease("en"),"2024-01")
    
    def testGetLatestReleaseWrongLanguage(self):
        with self.assertRaises(LookupError):
            self.client.getLatestRelease("onion")
    
    def testCheckReleaseTrue(self):
        self.assertTrue(self.client.checkRelease("2024-01","en"))
    
    def testCheckReleaseFalse(self):
        self.assertFalse(self.client.checkRelease("3124-01","en"))

    def testNoDuplicateInstances(self):
        t = ICDOtherAPIClient(url)
        self.assertTrue(self.client is t)
    
    def testGetBrowserUrl(self):
        explorer = ICDExplorer("en","","",release="2024-01",customUrl=url)
        e = explorer.getEntityFromCode("V")
        self.assertEqual(e.getBrowserUrl(),"http://localhost/browse/2024-01/mms/en#231358748")
        e = explorer.getEntityFromId("2091156678")
        self.assertEqual(e.getBrowserUrl(),"http://localhost/browse/2024-01/mms/en#2091156678")



class TestProxyEntity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.explorer = ICDExplorer("en","","",release="2024-01",customUrl=url)
    
    def testNoLookup(self):
        fake_uri = "it.wikipedia.org/wiki/Convento_dei_Domenicani_(Pordenone)"
        prx = ProxyEntity(self.explorer,"557175275",fake_uri)
        self.assertEqual(prx.getURI(),fake_uri)
    
    def testDoesLookup(self):
        prx = ProxyEntity(self.explorer,"557175275","icd.who.int/browse/2024-01/mms/557175275")
        self.assertEqual(prx.getCode(),"8B25.4")