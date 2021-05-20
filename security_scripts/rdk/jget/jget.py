"""
Tiny library to traveres json, and return the requested data.

The gosls is to have the code look more like declarations than procedural code
example:

gateways = Jgat(somejson).at("configuration").at("routes").select("gatewayId").get())

Note the implementatation of of the traversal methods "at" and "select" return
the object identifier. This is the mechanism that allow the chainingf the
method calls and he tight syntax.
 
"""


class Jget:
    """
    Very small and lightweight class for  extracting things from json.
    
    """
    def __init__ (self,json):

        # This variable is updated as the json is traversed
        # by successive function calls.
        # Once an array is traversed, it becomes an array of JSON
        
        self.json = json  

    def get(self):
        """
          return value(s) of query
          + Traversing to a terminal element returns a scalar,
            or list of scalars (if an array was invovled).
          * Travesals to nont termainal elements return json or
            a list of jsons if an array was traversed.
        """ 
        return self.json
    
    def at(self, string):
        """ Traverse a single named element"""
        self.json = self.json[string]
        return self
    
    def select(self,string):
        """ traverse an array, choosing array elements
            and then travere array elements beginning with string.
        """
        #choose array elements posessng staring.
        #return arra of what string pointss to
        self.json =[j[string] for j in self.json if string in j]
        return self
    


        


