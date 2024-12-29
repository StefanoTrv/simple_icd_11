import unittest, time
from simple_icd_11 import ICDOfficialAPIClient, ICDExplorer, ProxyEntity

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
        self.assertEqual(self.client.getLatestRelease("en"),"2024-01")
    
    def testGetLatestReleaseWrongLanguage(self):
        with self.assertRaises(LookupError):
            self.client.getLatestRelease("onion")
    
    def testGetLatestReleaseOldToken(self): #needs to be updated when new release comes out
        self.compromiseToken()
        self.assertEqual(self.client.getLatestRelease("en"),"2024-01")
    
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