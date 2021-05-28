"""
Tiny library to traveres json, and return the requested data.

The gosls is to have the code look more like declarations than procedural code
example:

gateways = Jgat(somejson).at("configuration").at("routes").all("gatewayId").get())

Note the implementatation of of the traversal methods "at" and "select" return
the object identifier. This is the mechanism that allow the chainingf the
method calls and he tight syntax.
 
"""

def error_check(f):
    def check(self, *args):
        if not self.error:
            try:
                f(self, *args)
            except:
                self.error = True
        return self
    return check


class Jget:
    """
    Very small and lightweight class for  extracting things from json.
    
    """
    def __init__ (self,json):

        # This variable is updated as the json is traversed
        # by successive function calls.
        # Once an array is traversed, it becomes an array of JSON
        
        self.json = json
        self.error = False

    def get(self):
        """
          return value(s) of query
          + Traversing to a terminal element returns a scalar,
            or list of scalars (if an array was invovled).
          * Travesals to nont termainal elements return json or
            a list of jsons if an array was traversed.
        """
        if self.error: return None
        return self.json

    @error_check
    def at(self, string):
        """ Traverse a single named element """
        self.json = self.json[string]

    @error_check
    def flatten(self):
        """
        Flatten an AWS list of dictionaries  to json. Store as self.json

        The use case is hwo AWS stores tags as a lisit of ....
        {"Key":"<tag name>", "Value":<value>} dictionaries.
        Flattening allows the get operator to pull out a tag value
        """
        if self.error : return self
        new_json = {}
        for d in self.json :
            new_json[d["Key"]] = d["Value"] 
        self.json = new_json
        return self
    
    @error_check
    def all(self,string):
        """ traverse an array, choosing array elements
            and then travere array elements beginning with string.
        """
        #choose array elements posessng staring.
        #return arra of what string pointss to
        self.json =[j[string] for j in self.json if string in j]
        return self
    


        


