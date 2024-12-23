import unittest, time
from simple_icd_11 import ICDOfficialAPIClient

class TestICDOfficialAPIClient(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        f = open("api_credentials.txt", "r")
        cls.clientId = f.readline().strip()
        cls.clientSecret = f.readline().strip()
        f.close()
        cls.client_id = "7f9f1868-7838-4e15-822b-da2f377c7651_488d4d8d-92a2-4494-8c24-858fbd2e17c7"
        cls.client_secret = "MuE49egB0RUdOFV9cxWE0f2Mvn7XXagIuOY4fB/M67E="
        cls.client = ICDOfficialAPIClient(cls.clientId,cls.clientSecret)
    
    def compromiseToken(self):
        if(self.client.token[-1]=="A"):
            self.client.token = self.client.token[:-1]+"B"
        else:
            self.client.token = self.client.token[:-1]+"A"
        if(self.client.token[0]=="w"):
            self.client.token = "a"+self.client.token[1:]
        else:
            self.client.token = "w"+self.client.token[1:]
    
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