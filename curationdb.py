import pymongo
from pymongo import MongoClient
from ete3 import NCBITaxa
import pandas as pd
client = MongoClient()
db = client.COCONUT2020
ncbi = NCBITaxa()


def create_column(name_column, diccionary, dataframe):
    help_list = []
    for key in diccionary:
        x = diccionary[key]
        help_list.append(x)
    dataframe[name_column] = help_list


def dataCollection():
    collection = db.uniqueNaturalProduct

    if 'curatedDB' in db.list_collection_names():
        db.curatedDB.drop()

    '''  Data Collection and Curation'''
    data_from_uniqueNP = collection.find(
        {}, {'_id': 0, 'coconut_id': 1, 'textTaxa': 1, 'taxid': 1})
    tables = pd.DataFrame(list(data_from_uniqueNP))

    # Method to put upper and lower text_taxas in the database
    # text_taxa_upper is a diccionary with key: the index from the DataFrame
    # and the value a list with the text_taxas with the names corrected
    text_taxa_upper = {}
    nx = ['notax']
    length_data = len(tables.index)
    for a in range(0, length_data):
        current_row_textTaxa = tables.loc[a, 'textTaxa']
        if current_row_textTaxa == nx:
            text_taxa_upper[a] = current_row_textTaxa
        else:
            list_fixed_textTaxas = []
            for b in range(0, len(current_row_textTaxa)):
                lowered_current_textTaxa = current_row_textTaxa[b].lower()
                split_textTaxa = lowered_current_textTaxa.split(maxsplit=3)
                split_textTaxa[0] = split_textTaxa[0].lower().capitalize()
                fixed_textTaxa = ' '.join(split_textTaxa)
                list_fixed_textTaxas.append(fixed_textTaxa)
            text_taxa_upper[a] = list_fixed_textTaxas

    # Method to fix some names
    detected = ['Actinoplanes "sp. (ma 7066; atcc 55532)"', 'Plants', 'Plant', 'Animal', 'Animals', 'Unknown-fungus sp. mf 5638, a nalanthamala sp',
                'Unknown-fungus sterila', 'Unknown-fungus dothideales (fungus) mpuc 046', 'Unknown-fungus', 'Unknown-bacterium']
    replaced = ['Actinoplanes sp.', 'Viridiplantae', 'Viridiplantae', 'Metazoa', 'Metazoa', 'Nalanthamala', 'Sterila', 'Botryosphaeriaceae',
                'Dothideales', 'Fungi', 'Bacteria']

    for key in text_taxa_upper:
        x = text_taxa_upper[key]
        for w in range(0, len(x)):
            for i in range(0, len(detected)):
                if x[w] in detected[i]:
                    x[w] = replaced[i]

    # The column name is fixed_textTaxas and contains the names from the
    # uniqueNaturalProduct collection but fixed
    create_column('fixed_textTaxas', text_taxa_upper, tables)

    # Method to obtain the id's names of the taxid from database
    # ids_to_names is a diccionary where the key is the index and the value
    # is the names that can be translated from an id. If it can't be translated
    # or there isn' any id (empty row) the value will be notax
    ids_to_names = {}
    for n in range(0, length_data):
        current_row_id = tables.loc[n, 'taxid']
        # Boolean of a empty list is False
        if bool(current_row_id):
            dicc_translation = {}  # Only with the text taxas. Needed to mantain the order
            list_translation = []  # Only with the text taxas
            for m in range(0, len(current_row_id)):
                current_id_to_be_translated = [current_row_id[m]]
                translation = ncbi.get_taxid_translator(
                    current_id_to_be_translated)
                if translation == {}:
                    dicc_translation[m] = ['notax']
                else:
                    dicc_translation[m] = translation
            for key in dicc_translation:
                x = dicc_translation[key]
                list_translation.append(x)
            ids_to_names[n] = list_translation
        else:
            ids_to_names[n] = ['notax']

    # Method to create in tables a column with the translated id of the database
    create_column('translation_id-name_pair', ids_to_names, tables)

    # Method to obtain a list of names without the ids from de database
    # Pair is referred to the couple of id + name (translated id)
    # only names from pairs is a diccionary with the existing names from the translated ids
    only_namesfrompairs = {}
    k = 0
    for k in range(0, length_data):
        current_row_pairs = tables.loc[k, 'translation_id-name_pair']
        if current_row_pairs == nx:
            only_namesfrompairs[k] = current_row_pairs
        else:
            list_only_names = []
            for l in range(0, len(current_row_pairs)):
                current_pair = current_row_pairs[l]
                if current_pair == nx:
                    list_only_names.append(current_pair)
                else:
                    for key in current_pair:
                        # onlyname is the textTaxa from the pair name+id
                        onlyname = current_pair.get(key)
                        list_only_names.append(onlyname)
            only_namesfrompairs[k] = list_only_names

    # Create a new column in tables with only the names translated from taxids
    create_column('onlynames_fromids', only_namesfrompairs, tables)

    # Method to translate the curated_text_taxas to ids
    # textTaxas_to_ids is a diccionary with where the key is rhe index and
    # the value is the pair translated name + id
    textTaxas_to_ids = {}
    mr = ['Marine', '2-f"', '2-3"']
    for index, row in tables.iterrows():
        current_row_names = row['fixed_textTaxas']
        if current_row_names == nx:
            textTaxas_to_ids[index] = [0]
        else:
            pair_name_id = {}
            list_translation = []
            for e in range(0, len(current_row_names)):
                current_name = [current_row_names[e]]
                # We don't want to translate the textTaxas from mr. Fail
                if current_row_names[e] in mr:
                    pair_name_id[e] = [0]
                else:
                    translation = ncbi.get_name_translator(current_name)
                    if translation == {}:
                        pair_name_id[e] = [0]
                    else:
                        pair_name_id[e] = translation
            for key in pair_name_id:
                x = pair_name_id[key]
                list_translation.append(x)
            textTaxas_to_ids[index] = list_translation
    # textTaxas_to_ids contains {}, {}, {}, {'Brucea javanica': [210348]} ... exists empty ones but I change for id 0. Another possible change it could be to change into a negative number

    # Add a column in tables with the text_taxas_curated and the ids translated
    create_column('translation_name-id_pair', textTaxas_to_ids, tables)

    # Method to obtain a list of id from the translation_name-id_pair (only ids)
    only_idsfrompairs = {}
    for s in range(0, length_data):
        # In this case the pairs are name + id
        current_row_pairs = tables.loc[s, 'translation_name-id_pair']
        if current_row_pairs == [0]:
            only_idsfrompairs[s] = current_row_pairs
        elif current_row_pairs == []:
            only_idsfrompairs[s] = [0]
        else:
            list_only_ids = []
            for z in range(0, len(current_row_pairs)):
                current_pair = current_row_pairs[z]
                if current_pair == [0]:
                    list_only_ids.append(current_pair)
                else:
                    for key in current_pair:
                        number = current_pair.get(key)
                        list_only_ids.append(number)
            only_idsfrompairs[s] = list_only_ids

    # Create a column in tables only with the ids from the names in tax names curated
    list_onlyids = []
    for index in only_idsfrompairs:
        number = only_idsfrompairs[index]
        if number == [0]:
            list_onlyids.append(number)
        elif len(number) == 1:
            list_onlyids.append(number[0])
        else:
            list_middlestep = []
            for g in range(0, len(number)):
                y = number[g]
                list_middlestep.append(y[0])
            list_onlyids.append(list_middlestep)
    tables['onlyid_fromtextTaxas'] = list_onlyids

    # Get a list of the ids and ranks to build the database
    list_pair_idrank = []
    for index, row in tables.iterrows():
        current_row_ids = row['taxid']
        current_row_idsfromname = row['onlyid_fromtextTaxas']
        if current_row_ids != []:
            for number in current_row_ids:
                rank = ncbi.get_rank([number])
                if rank == {}:
                    list_pair_idrank.append({number: 'no_rank'})
                else:
                    list_pair_idrank.append(rank)

        if current_row_idsfromname != [0]:
            for number in current_row_idsfromname:
                if number != 0:
                    rank = ncbi.get_rank([number])
                    if rank == {}:
                        list_pair_idrank.append({number: 'no_rank'})
                    else:
                        list_pair_idrank.append(rank)

    idandrank = {}
    for pair in list_pair_idrank:
        current_rank = list(pair.values())
        for number in pair:
            idandrank[number] = current_rank[0]

    return tables


def createNewCollection(tables):
    ''' Creation of the new curated database 
    It will appear only the ids that can be translated to name and the name that has a id'''
    col = db.curatedDB
    for index, row in tables.iterrows():
        myid = row['coconut_id']
        list_ids = row['taxid']
        list_names = row['fixed_textTaxas']
        list_onlynames_id = row['onlynames_fromids']
        list_onlyid_names = row['onlyid_fromtextTaxas']

        nx = ['notax']
        total_NP_names = len(list_names)
        list_data = {'coconut_id': myid}
        list_data['tax_classification'] = []

        # First with the names
        if list_onlyid_names != [0]:
            t = 0
            while t < total_NP_names:
                if list_onlyid_names[t] == 0:
                    t += 1
                else:
                    try:
                        rank_id = ncbi.get_rank([list_onlyid_names[t]])
                        if rank_id == {}:
                            list_data['tax_classification'].append(
                                {'taxonomy': [{'name': list_names[t], 'taxid': list_onlyid_names[t], 'rank': 'no_rank'}]})
                        else:
                            for key in rank_id:
                                rank_name = rank_id[key]
                            list_data['tax_classification'].append(
                                {'taxonomy': [{'name': list_names[t], 'taxid': list_onlyid_names[t], 'rank': rank_name}]})
                        t += 1
                    except:
                        list_data['tax_classification'].append(
                            {'taxonomy': [{'name': list_names[t], 'taxid': list_onlyid_names[t], 'rank': 'no_rank'}]})
                        t += 1

        # Second with the ids
        total_NP_ids = len(list_ids)
        if list_onlynames_id != nx:
            c = 0
            while c < total_NP_ids:
                if list_onlynames_id[c] == nx:
                    c += 1
                else:
                    try:
                        rank_id = ncbi.get_rank([list_ids[c]])
                        if rank_id == {}:
                            list_data['tax_classification'].append(
                                {'taxonomy': [{'name': list_onlynames_id[c], 'taxid': list_ids[c], 'rank': 'no_rank'}]})
                        else:
                            for key in rank_id:
                                rank_name = rank_id[key]
                            list_data['tax_classification'].append(
                                {'taxonomy': [{'name': list_onlynames_id[c], 'taxid': list_ids[c], 'rank': rank_name}]})
                        c += 1
                    except:
                        list_data['tax_classification'].append(
                            {'taxonomy': [{'name': list_onlynames_id[c], 'taxid': list_ids[c], 'rank': 'no_rank'}]})
                        c += 1

        if list_data['tax_classification'] != []:
            col.insert_one(list_data)

    return col


def lineageCollection(collection_new):
    ''' Lineage Collection. Add a new attribute to each document of the new database (curated NP) named 
    lineage (one complete lineage for each organism) '''

    data_from_curatedNP = collection_new.find({})
    tables = pd.DataFrame(list(data_from_curatedNP))

    # Obtain a diccionary with the coconut_id as key and the ranks of interest as value
    coconut_id_ranks = {}
    for i in range(0, len(tables)):
        row = tables.loc[i, 'tax_classification']
        coconutid = tables.loc[i, 'coconut_id']
        dicc_lineage = {}
        for n in range(0, len(row)):
            for elem in row:
                value = list(elem.values())
                value1 = value[0]
                for j in value1:
                    x = j['taxid']
                    lineage = ncbi.get_lineage(x)
                    add = []
                    for m in lineage:
                        rank = ncbi.get_rank([m])
                        values = list(rank.values())
                        if 'superkingdom' in values:
                            add.append(i)
                        if 'kingdom' in values:
                            add.append(i)
                        if 'phylum' in values:
                            add.append(i)
                        if 'class' in values:
                            add.append(i)
                        if 'order' in values:
                            add.append(i)
                        if 'family' in values:
                            add.append(i)
                        if 'genus' in values:
                            add.append(i)
                        if 'species' in values:
                            add.append(i)
                    dicc_lineage[n] = add
        coconut_id_ranks[coconutid] = dicc_lineage

    column_names = ['superkingdom', 'kingdom', 'phylum', 'class', 'order', 'family', 'genus', 'species']
    dicc_lin = {}
    for key in coconut_id_ranks:
        list_data = {}
        list_data['lineage'] = []
        lineages = coconut_id_ranks[key]
        for k in lineages:
            x = lineages[k]
            data = {}
            for n in range(0, len(x)):
                data[column_names[n]] = x[n]
            list_data['lineage'].append(data)
        dicc_lin[key] = list_data

    for key in dicc_lin:
        x = dicc_lin[key]
        collection_new.update_one({'coconut_id': key}, {'$set': x})

    return coconut_id_ranks


def treeCollection(collection_new, diccionary_interesting_ranks):
    ''' Tree Collection. Add a new attribute to each document of the new database (curated NP) named
    tree. It is a newick string one for all the organisms '''
    data_to_create_tree = {}
    for identifier in diccionary_interesting_ranks:
        data1 = []
        lineages = diccionary_interesting_ranks[identifier]
        for key in lineages:
            x = lineages[key]
            # The trees are going to be created with the last rank of the lineages for each organism
            data1.append(x[-1])
        data_to_create_tree[key] = data1
    for key in data_to_create_tree:
        x = data_to_create_tree[key]
        try:
            tree_fromncbi = ncbi.get_topology(x)
            tree_string = tree_fromncbi.write(format=8)
            collection_new.update_one(
                {'coconut_id': key}, {'$set': {'newick_tree': tree_string}})
        except:
            print(str(key) + ' ' + str(len(x)))


def main():
    tables = dataCollection()
    col = createNewCollction(tables)
    # dic_interesting_ranks = lineageCollection(col)
    # treeCollection(col, dic_interesting_ranks)



main()
