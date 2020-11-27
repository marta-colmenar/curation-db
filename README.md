# curation-db
The curationdb.py is a code divided in four blocks: dataCollection, createNewDatabase, lineageCollection and treeCollection. The objetive of the program 
is to get a 'curated' database. In this database we will find only the ids that can be translated to a name, and the names (correctly spelled) that can
be translated into an identifier. In order to achieve this:

- Data is first collected (dataCollection): a DataFrame named tables is created to save the ids, names and ranks that will be used in the following steps.
- Creation of the database (createNewDatabase): the structure of the introduced documents will have an id (Mongo id), a coconut_id and a tax_classification.
  The tax_classification is a list of embed documents with diferent taxonomies (for each taxonomy the name, the id and the rank, it refers to an organism).
- Lineage insertion (lineageCollection): the ranks of interests are superkingdom, kingdom, phylum, class, order, family, genus and species. So, for each 
  organism a list will appear with the identifiers of each of the ranges that belong to its lineage.
- Newick trees (treeCollection): string with the trees in format 8 (newick). One for all the organisms.

Finally, the new database will have this form (example for one document, in other words, a natural product).
