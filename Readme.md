A spider, which collects authors' cooprative organization from webofscience.

Input: _data/authors_

* line structure: id;author-name;author-organization

Output: 

* _valid_ directory
	* each file in _valid_ corresponds to one author; the file name is the author id.
	* line structure: author-name;author-organization;cooperative-organization;organization-frequency
* _non_found_ directory
	* each file corresponds to one author.
* _non_organ_ directory
	* each file corresponds to one author.

Usage:

* python crawl.py data/authors
