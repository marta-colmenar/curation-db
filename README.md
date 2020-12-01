# curation-db
Natural products (NPs) are small molecules produced by living organisms with potential applications in pharmacology. The aim of this code is to curate the current database for NP and the living organisms that produce this chemicals. With the curation of the database I mean to have a organized and visual structure and a place which keeps complete data about the names, ids, taxonomy and lineages of the organisms. All the data comes from the NCBI Taxonomy.

The *curationdb.py* is a code divided in four blocks: dataCollection, createNewCollection, lineageCollection and treeCollection. The objetive of the program is to get a 'curated' collection. In this database we will find only the ids that can be translated to a name, and the names (correctly spelled) that can be translated into an identifier. In order to achieve this:

- Data is first collected (dataCollection): a DataFrame named tables is created to save the ids, names and ranks that will be used in the following steps.
- Creation of the collection (createNewCollection): the structure of the introduced documents will have an id (Mongo id), a coconut_id and a tax_classification. The tax_classification is a list of embed documents with diferent taxonomies (for each taxonomy the name, the id and the rank, it refers to an organism).
- Lineage insertion (lineageCollection): the ranks of interests are superkingdom, kingdom, phylum, class, order, family, genus and species. So, for each organism a list will appear with the identifiers of each of the ranges that belong to its lineage.
- Newick trees (treeCollection): string with the trees in format 8 (newick). One for all the organisms.

Some explanations to run the code:
- The name of the new collection that is going to be created is *curatedDB*. If you want you can change it: 1) Go to the method to create the new database named createNewCollection(tables); 2) Change the name of the variable col (for example to col = db.NEWNAME)
- To run the code you will need write *python curationdb.py* at the command window of your computer.
- The database that is being curated is COCONUT2020 (in my computer). You can modify this at the 5th line of the code changing the variable db. The collection it is being used is uniqueNaturalProduct, and it is possible to change it at the dataCollection() method (variable collection).

Finally, the new database will have this form (example for one document, in other words, a natural product).

                                      {'_id': ObjectId('5fc654b218fab063817b7863'),
                                       'coconut_id': 'CNP0221451',
                                       'tax_classification': [{'taxonomy': [{'name': 'Bacteria',
                                           'taxid': 2,
                                           'rank': 'superkingdom'}]},
                                        {'taxonomy': [{'name': 'Lysobacter sp.',
                                           'taxid': 72226,
                                           'rank': 'species'}]}],
                                       'lineage': [{'superkingdom': 2},
                                        {'superkingdom': 2,
                                         'kingdom': 1224,
                                         'phylum': 1236,
                                         'class': 135614,
                                         'order': 32033,
                                         'family': 68,
                                         'genus': 72226}],
                                       'newick_tree': '(72226);'}

There are also two jupyter notebooks similar to the final code. They were used to see outputs and chech the proper code functioning. Also, there is a file with the state of the collection.
