RDF to CKAN import
==================

Early version of script to import dataset metadata in RDF to CKAN, while using SPARQL all over the place. 

Tried with CKAN v1.7.4. Not ready for use.

Steps
-----

0. Edit `etc/config.json`:
    1. Use `sparql` and its attribute `endpoint` to set URL of SPARQL endpoint, from which data will be imported.
    2. If you don't have `JENA_HOME` environment variable set, then you can set here `JENA_HOME` to point to directory where [Apache Jena](http://jena.apache.org) is installed.
    3. Use `ckanInstances` to provide a list of configurations for CKAN instances, into which data should be imported. `api` is used to set URL of CKAN API, `group` may be set to group name if you want to associate imported datasets with it, `key` is your CKAN API key and `lang` sets the preferred language code for the imported data.
1. SPARQL SELECT query to filter relevant dataset URIs from the source dataset.
    1. Edit `queries/getDatasetURIs.tpl` if you want to filter datasets to be imported.
2. Retrieve dataset metadata using SPARQL CONSTRUCT.
3. Locally SPARQL CONSTRUCT to convert to CKAN-data-model-like RDF.
4. Walk the resulting RDF and transform it into dict.
    1. You can configure custom URI-to-label mappings in `etc/mappings.json`.
5. Import into CKAN instance.
6. Prosper. While prospering, you may also want to check the logs in `log/import.log`.

Dependencies
------------

- [Jena ARQ](http://jena.apache.org/documentation/query/): used as performant and standards-compliant transformation engine. I tried [rdflib](https://github.com/RDFLib/rdflib)'s support of SPARQL but, while getting better, it has still some quirks and can be very slow.

Questions
---------

- Use [ckanapi](https://github.com/wardi/ckanapi) instead of [ckanclient](https://github.com/okfn/ckanclient)?
- How to make the conversion resilient to the backwards-incompatible changes in the CKAN data model? E.g., representing `:extras` as a list of lists (`[[key1, value1], [key2: value2]]`) or as a list of dicts (`[{"key" : key1, "value" : value1}, {"key" : key2, "value" : value2}]`).
 
Reference
---------

- [CKAN dataset model](http://docs.ckan.org/en/ckan-1.8/domain-model-dataset.html)
