import sys
from xml.dom import minidom

# suit our needs

class XML2Dict(object):
    """ Converts an XML object to Python Dictionary
        Based on http://stackoverflow.com/questions/3292973/xml-to-from-a-python-dictionary
        with additional updates done
    """
    def __init__(self, filename, pubType, pubStatus):
        # By default it creates a list only if there is more than one item for a given key
        # But if you want some keys to be always list, specify in keys_always_list
        self.keys_always_list = ["action", "test", "command", "condition", "match_intent", "app"]

        # Merge keys like this
        # If { "actions" : { "action": [... ] } }
        # Change to { "actions" : [ ... ] }
        # Note here "actions" have the singular "action"
        self.merge_keys = ["action", "test", "match_intent", "app" ]
	self.pubType = pubType
	self.pubStatus = pubStatus
	self._data = minidom.parse(filename)

    def __dappend(self, dictionary, key, item):
        """Append item to dictionary at key.  Only create a list if there is more than one item for the given key.
        dictionary[key]=item if key doesn't exist.
        dictionary[key].append(item) if key exists."""

        if key == "#attributes":
            for k,v in item.iteritems():
                dictionary.setdefault(k, v)
            return

        if key in dictionary.keys() or key in self.keys_always_list:
            if key not in dictionary.keys():
                dictionary[key] = []
            if not isinstance(dictionary[key], list):
                lst=[]
                lst.append(dictionary[key])
                lst.append(item)
                dictionary[key]=lst
            else:
                dictionary[key].append(item)
        else:
            dictionary.setdefault(key, item)

    def __getValue(self, val):
        try:
	   return str(val) 
	except:
	   return val

    def __node_attributes(self, node):
        """Return an attribute dictionary """
        if node.hasAttributes():
            return dict([(str(attr), self.__getValue(node.attributes[attr].value)) for attr in node.attributes.keys()])
            #return dict([(str(attr), str(node.attributes[attr].value)) for attr in node.attributes.keys()])
        else:
            return None

    def __attr_str(self, node):
        return "%s-attrs" % str(node.nodeName)

    def __hasAttributes(self, node):
        if node.nodeType == node.ELEMENT_NODE:
            if node.hasAttributes():
                return True
        return False

    def __with_attributes(self, node, values):
        if self.__hasAttributes(node):
            if isinstance(values, dict):
                self.__dappend(values, '#attributes', self.__node_attributes(node))
                return { str(node.nodeName): values }
            elif isinstance(values, str):
                return { str(node.nodeName): values,
                         self.__attr_str(node): self.__node_attributes(node)}
        else:
            return { str(node.nodeName): values }

    def xml2dict(self, node):
        """Given an xml dom node tree,
        return a python dictionary corresponding to the tree structure of the XML.
        This parser does not make lists unless they are needed.  For example:

        '<list><item>1</item><item>2</item></list>' becomes:
        { 'list' : { 'item' : ['1', '2'] } }
        BUT
        '<list><item>1</item></list>' would be:
        { 'list' : { 'item' : '1' } }

        By default it creates a list only if there is more than one item for a given key.
        But if you want some keys to be always list, specify in keys_always_list

        This is a shortcut for a particular problem and probably not a good long-term design.
        """
        if not node.hasChildNodes():
	    arr = []
            if node.nodeType == node.TEXT_NODE:
                if node.data.strip() != '':
                    return str(node.data.strip())
                else:
                    return None
	    elif node.nodeType == node.ELEMENT_NODE:
		ldict = {}
		ldict[str(node.tagName)] = self.__node_attributes(node)
		ret = ldict
                return ret
            else:
                ret =  self.__with_attributes(node, None)
                return ret
        else:
            #recursively create the list of child nodes
            childlist = []
            for child in node.childNodes:
                xc = self.xml2dict(child)
                if xc != None and child.nodeType != child.COMMENT_NODE:
                    childlist.append(xc)
            if len(childlist)==1 and isinstance(childlist[0], str):
                return self.__with_attributes(node, childlist[0])
            else:
                #if False not in [isinstance(child, dict) for child in childlist]:
                new_dict={}
                for child in childlist:
                    if isinstance(child, dict):
                        for k in child:
                            self.__dappend(new_dict, k, child[k])
                    elif isinstance(child, str):
                        self.__dappend(new_dict, '#text', child)
                    else:
                        print "ERROR"
                ret =  self.__with_attributes(node, new_dict)

                # Merge keys like this
                # If { "actions" : { "action": [... ] } }
                # Change to { "actions" : [ ... ] }
                # Note here "actions" have the singular "action"
                # Also: the singular "action" should be the only element within the dict and should
                #       be a list
                if len(ret) == 1 and isinstance(ret.values()[0], dict):
                    k,v = ret.items()[0]
                    if isinstance(v, dict):
                        k1,v1 = v.items()[0]
                        if isinstance(v1, list) and k1 in self.merge_keys and k1 + "s" == node.nodeName:
                            ret = { str(node.nodeName): v1 }
                return ret

    def load(fname):
        return xmldom2dict(minidom.parse(fname))


    def adapt(self):

        d = self.xml2dict(self._data)
        rows = d['#document']['datei']['row']
	if not isinstance(rows, list):
		tmp_list = []
		tmp_list.append(rows)
		rows = tmp_list
	
        for row in rows:
            for key in row.keys():
	        if key == 'Author':
	           authors = row[key]
		   # we have only one author
                   if isinstance(authors, dict):
                       if authors['IsDKFZ'] == '0': 
                           authors['IsDKFZ'] = False
                       else:
		           authors['IsDKFZ'] = True

		       authors['pos'] = authors['Pos']
		       del authors['Pos']

		   elif isinstance(authors, list): 
	               for auth in authors:
                           if auth['IsDKFZ'] == '0': 
                               auth['IsDKFZ'] = False
                           else:
		               auth['IsDKFZ'] = True

		           auth['pos'] = auth['Pos']
		           del auth['Pos']
                if not isinstance(row[key], list):
                    lst=[]
                    lst.append(row[key])
                    row[key]=lst
	        row['PubType'] = []
	        row['PubType'].append(self.pubType)
	        row['PubStatus'] = []
	        row['PubStatus'].append(self.pubStatus)
        return rows

