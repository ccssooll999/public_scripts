#!/usr/bin/env python
# -*- coding: utf-8 -*-


# script to open up a tab blast output and generate Alien index scores,
# this finds the kingdom that blast mtach has been assigned.
# script: Parse the NCBI taxonomic database node.dmp to get the
# taxonomic relationship

#author: Peter Thorpe September 2015. The James Hutton Insitute, Dundee, UK.


"""
What:
To determine Lateral gene transfer event (LGT). An alien index score needs to be generated. Score > 45
is a candidate LGT

Using a Blastp_Vs_NR tab output with taxonomic information included.

How:

Alien index:
taxonomic origin: Bacteria, Fungi, Plantae, Metazoa, and Other (including protists), and
the best expect value from each group was used to calculate an Alien Index (AI) as given
by the formula AI = log((Best E-value for Metazoa) + e-200) - log((Best E-value for Non-
Metazoa) + e-200). If no hits were found, the E-value was set to 1. Thus, AI is allowed to
vary in the interval between +460 and -460, being positive when top non-metazoan hits
yielded better E-values than the top metazoan ones. Entries with incomplete taxonomy,
such as X-ray structures, or hits belonging to the same phylum as the query sequence (
i.e Rotifera, filter_out_tax_id or Nematoda), were excluded from the analysis


    BLAST DATA should be formatted as:

qseqid = Query Seq-id (ID of your sequence)
sseqid = Subject Seq-id (ID of the database hit)
pident = Percentage of identical matches
length = Alignment length
mismatch = Number of mismatches
gapopen = Number of gap openings
qstart = Start of alignment in query
qend = End of alignment in query
sstart = Start of alignment in subject (database hit)
send = End of alignment in subject (database hit)
evalue = Expectation value (E-value)
bitscore = Bit score
salltitles = TOP description of the blast hit
staxids = tax_id
scientific_name
scomnames = common_name
sskingdoms = kingdom

"""
#need this for exponontial
import math
from math import exp, expm1
import os
import sys
from optparse import OptionParser
import datetime
###########################################################################################################################################################################################

def parse_NCBI_nodes_tab_file(folder):
    """this is a function to open nodes.dmp from the NCBI taxonomy
database and find the parent child relationship....returns a
disctionary for later use"""

    #open file - read.
    #nodes.dmp - this file is separated by \t|\t
    #tax_dmp_database = open(nodes_dmp, "r")
    #empty dictionary to add to parent and child (keys,vals) to
    tax_dictionary = {}

    #nodes.dmp files goes: child, parent, etc
    #merged.dmp file goes: old, new
    #In both cases, can take key as column 0 and value as column 1
    for filename in ["nodes.dmp", "merged.dmp"]:
        with open(os.path.join(folder, filename)) as handle:
            for line in handle:
                tax_info = line.replace("\n", "\t").split("\t|\t")
                #first element
                parent = tax_info[1]
                #second element
                child = tax_info[0]
                #add these to the dictionary {parent:child}
                tax_dictionary[child]= parent
    #print tax_dictionary
    #f_out = open("dictionary_test.out", "w")
    #print >> f_out, tax_dictionary
    #f_out.close()
    
    return tax_dictionary

###########################################################################################################################################################################################

def test_if_id_is_metazoan(tax_id_of_interst,final_tx_id_to_identify_up_to, tax_to_filter_out):
    """function to get a list of tax id of interest from the tax_dictionary
    which is produced in the parse_function (parse_NCBI_nodes_tab_file)
    nodes.dmp file. . The tax id
    are added to a list for later use
    """
    #print "filtering up to =", final_tx_id_to_identify_up_to
    #print "filtering out = ", tax_to_filter_out
    if tax_id_of_interst == "N/A":
        raise ValueError("N/A as taxonomy ID")
    if tax_id_of_interst == "0":
        tax_id_of_interst =="32644"#assign an unknown id
        return "In_filter_out_tax_id" 
    #call the function to parse nodes file and assign to variable
    #tax_dictionary = parse_NCBI_nodes_tab_file(nodes_dmp)
    #empty list to add tax id to
    #list_of_tx_id_identified_that_we_want = []
    #get the "master" parent id
    parent = tax_dictionary[tax_id_of_interst]
    #print parent

    #list_of_tx_id_identified_that_we_want.append(parent)
    while True:
    #for keys in tax_dictionary:
        #print "parent = ", parent, "\n"
        parent = tax_dictionary[parent]
        if tax_id_of_interst == "N/A":
            raise ValueError("N/A as taxonomy ID")
        #list_of_tx_id_identified_that_we_want.append(parent)
        #print list_of_tx_id_identified_that_we_want
        #print "new parent = ", parent
        #32630 is a synthetic organism
        if parent == "32630":#32630
            return "In_filter_out_tax_id"
            break            
        if parent == tax_to_filter_out:
            #print "filtering out"
            return "In_filter_out_tax_id"
            break
        if parent == final_tx_id_to_identify_up_to:
            #print "......................... im here"
            return True
        elif parent == "1":
            #print "Reached the root of the tree"
            return False
  
###########################################################################################################################################################################################
                
def test_id_of_interst(tax_id_of_interst,\
                        final_tx_id_to_identify_up_to,out_file):
    #test pea aphid is in metazoa, should be true
    assert test_if_id_is_metazoan(nodes_dmp,"7029","33208") is True
    #test Arthopoda is in metazoa. Should be true
    assert test_if_id_is_metazoan(nodes_dmp,"6656","33208") is True
    #test pea aphid is in Pythophthora, should be false
    assert test_if_id_is_metazoan(nodes_dmp,"7029","4783") is False


    if test_if_id_is_metazoan(tax_id_of_interst,\
                                     final_tx_id_to_identify_up_to) is True:

        #print "......it worked", tax_id_of_interst
        return True
    if test_if_id_is_metazoan(tax_id_of_interst,\
                                     final_tx_id_to_identify_up_to) is False:
        return False
    
#############################################################################################################################
#7029 = pea aphid
#6656 = filter_out_tax_id
#33208 = Metazoa   -  for me this is the tax id I want to go up to
###########################################################################################################################################################################################

def parse_blast_line(blast_line_as_list, tax_coloumn):
    """function to return the bits of info which we want from the blast line
    (passed to function as a list)"""
    if len(blast_line_as_list) == 1:
        blast_line_as_list = blast_line_as_list[0]
    blast_line = blast_line_as_list
    Evalue = float(blast_line[10])
    bit_score = float(blast_line[11])
    # tax id can have a whole load of value e.g.  5141;367110;510951;510952;771870. Thefore we split it and take the first one
    query_name = blast_line[0]
    percentage_identity = blast_line[2]
    description = blast_line[12]
    tax_id = blast_line[tax_coloumn].split(";")[0]
    species_sci = blast_line[-3]
    species_common = blast_line[-2]
    kingdom = blast_line[-1]
    return query_name, percentage_identity, Evalue, bit_score, description, tax_id, species_sci, species_common, kingdom

def meta_or_non_metazoan(tax_id,Metazoa_tax_id, filter_out_tax_id):
    "function to return metazoan or non-metazoan"
    # call the function to test if the id of interst falls in metazoa or not
    if tax_id =="N/A":
        return "N/A"
    elif test_if_id_is_metazoan(tax_id, Metazoa_tax_id, filter_out_tax_id) == "In_filter_out_tax_id":
        print "in filter out phylum\n"
        return "N/A" # skip the code below
    elif test_if_id_is_metazoan(tax_id, Metazoa_tax_id, filter_out_tax_id):
        return "metazoan"
    else:
        return "nonmetazoan"
        #assert test_if_id_is_metazoan(tax_id, Metazoa_tax_id, filter_out_tax_id) is False
    
def reset_list_add_info(list_in, info)  :
    "function to rest the list to empty, then add info to it"
    list_in = []
    if not info == None:
        list_in.append(info)
    return list_in


def write_out_data(best_metazoan_hits, best_nonmetazoan_hits, tax_coloumn, out_file):
    """function to format and write out results of interest
    If there is no best non or metazoan hit the evalue is set to 1"""
    data_formatted_top_meta_no_hit = ""
    data_formatted_top_nonmeta_no_hit = ""
    data_formatted_top_nonmeta = ""
    data_formatted_top_meta = ""
    #print "best_metazoan_hits", best_metazoan_hits
    #print "best_nonmetazoan_hits", best_nonmetazoan_hits
    
    if best_metazoan_hits == []:
        if best_nonmetazoan_hits != []:
            results_list = parse_blast_line(best_nonmetazoan_hits, tax_coloumn)
            query_name = results_list[0]
            data_formatted_top_meta_no_hit= "%s\t\t1.0\t\t\t\tmetazoan\t\tno_hit\n" %(query_name)
    if best_nonmetazoan_hits == []:
        if best_metazoan_hits != []:
            results_list = parse_blast_line(best_metazoan_hits, tax_coloumn)
            query_name = results_list[0]
            data_formatted_top_nonmeta_no_hit= "%s\t\t1.0\t\t\t\tnonmetazoan\t\tno_hit\n" %(query_name)

    if best_metazoan_hits != []:
        catorgory = "metazoan"
        query_name, percentage_identity, Evalue, bit_score, description, tax_id, \
                species_sci, species_common, kingdom = parse_blast_line(best_metazoan_hits, tax_coloumn)
        
        data_formatted_top_meta= "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" %(query_name, percentage_identity,Evalue,
                                                                          bit_score, tax_id,
                                                                    kingdom, catorgory, species_sci,description)
    if best_nonmetazoan_hits != []:
        catorgory = "nonmetazoan"
        query_name, percentage_identity, Evalue, bit_score, description, tax_id, \
                species_sci, species_common, kingdom = parse_blast_line(best_nonmetazoan_hits, tax_coloumn)
        
        data_formatted_top_nonmeta= "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" %(query_name, percentage_identity, Evalue,
                                                                             bit_score, tax_id,
                                                                    kingdom, catorgory, species_sci,description)

    out_list = [data_formatted_top_meta_no_hit, data_formatted_top_meta,\
                data_formatted_top_nonmeta_no_hit, data_formatted_top_nonmeta]
    for i in out_list:
        print "i = ", i
        out_file.write(i)



def parse_blast_tab_file(filename1, outfile, filter_out_tax_id, Metazoa_tax_id, tax_coloumn):
    """this is a function to open up a tab file blast results, and
    produce alien index scores """
    blast_file = open (filename1, "r")
    out_file = open(outfile,"w")
    
    file_title_fields = "#query_name\tpercentage_identity\tEvalue\tbit_score\ttax_id\tkingdom\tcatorgory\tspecies,description\n"
    out_file.write(file_title_fields)
    tax_coloumn = int(tax_coloumn)-1 #for computer counting, default is 14 (human counting)
    #this is out list of so called top matches which we will append and remove as applicable
    best_metazoan_hits = []
    best_nonmetazoan_hits = []
    last_gene_name = ""
    last_blast_line = ""
    name_already_seen_set = set([])
    name_print_set = set([])

    for line in blast_file:
        if line.startswith("#"):
            continue
        if not line.strip():
            continue #if the last line is blank
        
        blast_line = line.rstrip("\n").split("\t")
        query_name, percentage_identity, Evalue, bit_score, description, tax_id,\
                    species_sci, species_common, kingdom = parse_blast_line(blast_line, tax_coloumn)
        print query_name
        #print blast_line
        
        if not query_name in name_already_seen_set:
            #this is the first time we have seen it. - write out the old results, if there are any
            if len(name_already_seen_set) > 0:
                if not last_gene_name in name_print_set:
                    name_print_set.add(last_gene_name)
                    #print " IIIAAAMMM HHEEERRE", query_name
                    write_out_data(best_metazoan_hits, best_nonmetazoan_hits, tax_coloumn, out_file)
                    best_metazoan_hits = reset_list_add_info(best_metazoan_hits, None)
                    best_nonmetazoan_hits = reset_list_add_info(best_nonmetazoan_hits, None)

                    #print "reset best to :", best_nonmetazoan_hits
                    
                    #print "do I want to write out old results here?"
            name_already_seen_set.add(query_name)
            key = meta_or_non_metazoan(tax_id,Metazoa_tax_id, filter_out_tax_id)
            #print "KEY = ", key, blast_line
            if key == "metazoan":
                best_metazoan_hits = reset_list_add_info(best_metazoan_hits, blast_line)
            if key == "nonmetazoan":
                best_nonmetazoan_hits = reset_list_add_info(best_nonmetazoan_hits, blast_line)
            last_gene_name = query_name
            #print "best_metazoan_hits == ", best_metazoan_hits, "\n"
            #print "best_nonmetazoan_hits == ", best_nonmetazoan_hits, "\n"
            # break the loop
            continue

        #if the query name is the same as the last one, we test the bit score to see which is the best hit ... depending on metazoan/ non assignment
        if query_name == last_gene_name:
            print "already seen", query_name
            key = meta_or_non_metazoan(tax_id,Metazoa_tax_id, filter_out_tax_id)
            #print "KEY = ", key, blast_line
            if key == "metazoan":
                if best_metazoan_hits == []:
                    best_metazoan_hits = reset_list_add_info(best_metazoan_hits, blast_line)                    

                if float(bit_score) > float(best_metazoan_hits[0][11]):
                        best_metazoan_hits = reset_list_add_info(best_metazoan_hits, blast_line)
            if key == "nonmetazoan":
                if best_nonmetazoan_hits == []:
                    best_nonmetazoan_hits = reset_list_add_info(best_nonmetazoan_hits, blast_line)
                old_bit_score = float(best_nonmetazoan_hits[0][11])
                #print "best_nonmetazoan_hits", best_nonmetazoan_hits
                #print "old bit score = ", old_bit_score, " new = ", float(bit_score)
                if float(bit_score) > float(best_nonmetazoan_hits[0][11]):
                    #print " you should see this"
                    
                    best_nonmetazoan_hits = reset_list_add_info(best_nonmetazoan_hits, blast_line)
            last_gene_name = query_name
        
        #if the names do not match, then we have a new hit. 
        if query_name != last_gene_name:
            #we have already seen it, but not printed it out. 
            if query_name in name_already_seen_set:
                # write out the old result. 
                write_out_data(best_metazoan_hits, best_nonmetazoan_hits,tax_coloumn, out_file)
                
                best_metazoan_hits = reset_list_add_info(best_metazoan_hits, None)
                best_nonmetazoan_hits = reset_list_add_info(best_nonmetazoan_hits, None)
                name_print_set.add(query_name)
                
        last_gene_name = query_name
        last_blast_line = blast_line
    #print "name_print_set = ", name_print_set    
    if not last_gene_name in name_print_set:
        write_out_data(best_metazoan_hits, best_nonmetazoan_hits, tax_coloumn, out_file)
        name_print_set.add(query_name)
            
    out_file.close()
    return True #for now until the function is sorted.



################################################################################################################################################

def parse_blast_tab_file_to_get_Alien_precursor_value(filtered_blast_results_file, outfile):
    """this is a function to open up a tab file blast results produced by parse_blast_tab_file, which works
    out if the blast hit is metazoan, nonmetazoan and excludes those in the phylum of interest,
    it also exclude a synthestic organism.... and  produce alien index scores based on the evalue of the hit"""
    #open files, read and write.
    blast_file = open (filtered_blast_results_file, "r")
    out_file = open(outfile,"w")
    title_file_fields = "#query_name\tpercentage_identity\tEvalue\tbit_score\ttax_id\tkingdom\tcatorgory\tprecursor_value\tspecies\tdescription\n"
    out_file.write(title_file_fields)
    for line in blast_file:
        if line.startswith("#"):
            continue
        if not line.strip():
            continue #if the last line is blank
        #print line.rstrip("\n").split("\t")
        query_name, percentage_identity,Evalue,bit_score,tax_id,kingdom,catorgory,\
                    species_sci,description = line.rstrip("\n").split("\t")
        Evalue = float(Evalue)
        precursor_value = precursor_score_calculator(Evalue)
        #print blast_line
        data_formatted1="%s\t%s\t%s\t%s\t%s\t%s\t%s\t%f\t%s\t%s\n" %(query_name, percentage_identity,\
                                                                 Evalue, bit_score,\
                                                                 tax_id, kingdom, catorgory,\
                                                                 precursor_value,\
                                                                 species_sci, description)
        out_file.write(data_formatted1)
    out_file.close()
    return True
#############################################################################################################################

def precursor_score_calculator (Evalue):
    """Alien index:  (http://www.sciencemag.org/content/suppl/2008/05/29/320.5880.1210.DC1/Gladyshev.SOM.pdf)
    taxonomic origin: Bacteria, Fungi, Plantae, Metazoa, and Other (including protists), and
    the best expect value from each group was used to calculate an Alien Index (AI) as given
    by the formula AI = log((Best E-value for Metazoa) + e-200) - log((Best E-value for Non-
    Metazoa) + e-200). If no hits were found, the E-value was set to 1. Thus, AI is allowed to
    vary in the interval between +460 and -460,being positive when top non-metazoan hits
    yielded better E-values than the top metazoan ones. Entries with incomplete taxonomy,
    such as X-ray structures, or hits belonging to the same phylum as the query sequence (
    i.e Rotifera, filter_out_tax_id or Nematoda), were excluded from the analysis

    Based on AI, genes were classified as foreign (AI>45), indeterminate (0<AI<45), or metazoan (AI<0)
    """
    #needed imports - do outside of function so it isnt called 100 000 times.
    #need this for exponontial
    #import math
    #from math import exp, expm1
    
    # AI = log((Best E-value for Metazoa) + e-200) - log((Best E-value for Non-Metazoa) + e-200)
    Evalue = float(Evalue)
    e_minus_200 = float(exp(-200))
    precursor_score_calculator_value = math.log((Evalue)+e_minus_200)
    #print Alien_index_precursor_score_calculator_value
    #Alien_index_precursor_score_calculator_value is basically log((Best E-value for INPUT kingdom) + e-200)
    return precursor_score_calculator_value


################################################################################################################################################

def find_true_alien_score(filename_with_precursor_values, outfile):
    """ This function opens up the output of the function above (parse_blast_tab_file_to_get_Alien_precursor_value)
    and works out the Alien index score based on sequence name identify. It check that the name above is metazoan,
    by testing if this is nonmetazoan

    ased on AI, genes were classified as foreign (AI≥45), indeterminate (0<AI<45), or metazoan (AI≤0)
    """

    # AI = log((Best E-value for Metazoa) + e-200) - log((Best E-value for Non-Metazoa) + e-200)
    blast_file = open (filename_with_precursor_values, "r")
    LGT_out = open(filename_with_precursor_values+"_LGT_candifates.out", "w")
    out_file = open(outfile,"w")
    tile_file_fields_all = "#query_name\tpercentage_identity\tevalue\tbit_score\ttax_id\tkingdom\tcatorgory\talien_index\t"+\
                       "species\tdescription\tcomments\t\t\tMeta_query_name\tMeta_percentage_identity\tMeta_evalue\tMeta_bit_score\tMeta_tax_id\t"+\
                       "Meta_kingdom\tMeta_catorgory\tMeta_alien_index\t"+\
                       "Meta_species\tMeta_description\n"
    
    tile_file_fields = "#query_name\tpercentage_identity\tevalue\tbit_score\ttax_id\tkingdom\tcatorgory\talien_index\t"+\
                       "species\tdescription\tcomments\n"
    
    LGT_out.write(tile_file_fields)

    out_file.write(tile_file_fields_all)
    last_query_name = ""
    last_blast_line = ""
    last_precursor_value = float(0.0)

    for line in blast_file:
        if line.startswith("#"):
            continue
        if not line.strip():
            continue #if the last line is blank
        blast_line = line.rstrip("\n").split("\t")
        
        query_name, percentage_identity,Evalue, bit_score,tax_id, kingdom,\
                    catorgory,precursor_value,species_sci, description = line.rstrip("\n").split("\t")
        #precursor value has already been worked out : log((Best E-value for Metazoa) + e-200) - function precursor_score_calculator
        precursor_value = float(precursor_value)

        if query_name == last_query_name:
            if catorgory == "nonmetazoan":
                alien_index = last_precursor_value - precursor_value

                meta_query_name, meta_percentage_identity,meta_Evalue, meta_bit_score,meta_tax_id, meta_kingdom,\
                    meta_catorgory,meta_precursor_value,meta_species_sci, meta_description = last_blast_line.rstrip("\n").split("\t")

                data_formatted = "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%f\t%s\t%s\n" %(query_name, percentage_identity, \
                                                                          Evalue, bit_score, tax_id, kingdom,\
                                                                          catorgory, alien_index, species_sci, description)
                data_formatted = data_formatted.replace("\n", "")+"\t\t\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%f\t%s\t%s\n" %(meta_query_name, \
                                                            meta_percentage_identity, meta_Evalue, meta_bit_score, meta_tax_id,\
                                                            meta_kingdom,meta_catorgory, alien_index, meta_species_sci, \
                                                            meta_description)    
                out_file.write(data_formatted)
                if alien_index > 0:
                    if float(percentage_identity) > 70:
                        comment = "potential_CONTAMINATION"
                    else:
                        comment = "potantial_HGT"
                    data_formatted = "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%f\t%s\t%s\t%s\n" %(query_name, percentage_identity, \
                                                                          Evalue, bit_score, tax_id, kingdom,\
                                                                          catorgory, alien_index, species_sci, \
                                                                          description, comment)
                    LGT_out.write(data_formatted)
        else:
            last_query_name = query_name
            last_blast_line = line
            last_precursor_value = precursor_value
    LGT_out.close()
    out_file.close()
    return True
            

######below is the command that call the function, that within itself calls all the other functions
#to run the script

if "-v" in sys.argv or "--version" in sys.argv:
    print "v0.0.3"
    sys.exit(0)




usage = """Use as follows:

$ python Lateral_gene_transfer_predictor.py -i blast_w_tax_id.tab --tax_filter_out 6656 (e.g.arthropoda) --tax_filter_up_to 33208 (e.g. metazoan) -o LTG_results.out


taxid - 6231 (nematoda)

Tax databse from NCBI is require. Download, unzip, and use -p /PATH/TO/   scripts will find them from here. 

    wget ftp://ftp.ncbi.nih.gov/pub/taxonomy/taxdump.tar.gz
    tar -zxvf taxdump.tar.gz


#6656 = filter_out_tax_id --tax_filter_out
#33208 = Metazoa   -  for me this is the tax id I want to go up to --tax_filter_up_to

What:
To determine Lateral gene transfer event (LGT). An alien index score needs to be generated. Score > 45
is a candidate LGT - however, it could be contamination. The user will have to decide.


How:

Alien index: (plagerised from Seb Eves Van Den Akker et al, Naccubus paper....)
taxonomic origin: Bacteria, Fungi, Plantae, Metazoa, and Other (including protists), and
the best expect value from each group was used to calculate an Alien Index (AI) as given
by the formula AI = log((Best E-value for Metazoa) + e-200) - log((Best E-value for Non-
Metazoa) + e-200). If no hits were found, the E-value was set to 1. Thus, AI is allowed to
vary in the interval between +460 and -460, being positive when top non-metazoan hits
yielded better E-values than the top metazoan ones. Entries with incomplete taxonomy,
such as X-ray structures, or hits belonging to the same phylum as the query sequence (
i.e Rotifera, filter_out_tax_id or Nematoda), were excluded from the analysis


    BLAST DATA should be formatted as:

qseqid = Query Seq-id (ID of your sequence)
sseqid = Subject Seq-id (ID of the database hit)
pident = Percentage of identical matches
length = Alignment length
mismatch = Number of mismatches
gapopen = Number of gap openings
qstart = Start of alignment in query
qend = End of alignment in query
sstart = Start of alignment in subject (database hit)
send = End of alignment in subject (database hit)
evalue = Expectation value (E-value)
bitscore = Bit score
salltitles = TOP description of the blast hit
staxids = tax_id
scientific_name
scomnames = common_name
sskingdoms = kingdom



MORE INFO:

Alien index:  (http://www.sciencemag.org/content/suppl/2008/05/29/320.5880.1210.DC1/Gladyshev.SOM.pdf)
    Massive Horizontal Gene Transfer in Bdelloid Rotifers :
    taxonomic origin: Bacteria, Fungi, Plantae, Metazoa, and Other (including protists), and
    the best expect value from each group was used to calculate an Alien Index (AI) as given
    by the formula AI = log((Best E-value for Metazoa) + e-200) - log((Best E-value for Non-
    Metazoa) + e-200). If no hits were found, the E-value was set to 1. Thus, AI is allowed to
    vary in the interval between +460 and -460,being positive when top non-metazoan hits
    yielded better E-values than the top metazoan ones. Entries with incomplete taxonomy,
    such as X-ray structures, or hits belonging to the same phylum as the query sequence (
    i.e Rotifera, filter_out_tax_id or Nematoda), were excluded from the analysis

    Based on AI, genes were classified as foreign (AI>45), indeterminate (0<AI<45), or metazoan (AI<0)

"""

parser = OptionParser(usage=usage)


parser.add_option("-i", "--in", dest="blast_tab_output", default=None,
                  help="the tab output from blast/diamond. This must have tax_id info in this!!"
                  "If you use diamond, please get this info using 'add_taxonomic_info_to_tab_output.py'",
                  metavar="FILE")

parser.add_option("-p", "--path", dest="path", default=os.getcwd(),
                  help="Directory containing relevant taxonomy/database files "
                       "Default is the current working "
                       "directory. This is not used with the main input and output "
                       "filenames.")

parser.add_option("--tax_filter_out", dest="tax_filter_out", default="6656",
                  help="The tax ID to filter out: for this analysis the Phylum which your BEAST"
                  "of interest if found. e.g. Aphids are from Arthropoda, therefore this would be "
                  "6656, whihc is the dwefault value. This will filter out all blast hit which are "
                  "from this phylum. It is possible to put a species/kingdom tax_id in here ... what"
                  "ever floats your boat.")


parser.add_option("--tax_filter_up_to", dest="tax_filter_up_to", default="33208",
                  help=" The tax_id to 'walk up to', to determine assignment. By default this is metazoa."
                  "The script work out the best metazoan to non-metazoan hit. But this can be altered if "
                  "you wish to alter this")


parser.add_option("--tax_coloumn", dest="tax_coloumn", default="14",
                  help="the coloumn with the tax_id info. Defulat is 14"
                  "(as counted by a human/ not a computer")
parser.add_option("-o", "--out", dest="outfile", default="_tab_blast_LGT_results.tab",
                  help="Output filename - default= infile__tab_blast_LGT_results",
                  metavar="FILE")


(options, args) = parser.parse_args()



def apply_path(folder, filename):
    """If filename is not absolute, assumed relative to given folder.

    Here filename is a relative path (does not start with slash):

    >>> apply_path("/mnt/shared/taxonomy", "names.dmp")
    '/mnt/shared/taxonomy/names.dmp'

    Here filename is already an absolute path, so no changes:

    >>> apply_path("/mnt/shared/taxonomy", "/tmp/ncbi/taxonomy/names.dmp")
    '/tmp/ncbi/taxonomy/names.dmp'
    
    """
    if os.path.isabs(filename):
        return filename
    else:
        return os.path.join(folder, filename)


###############################################
blast_tab_output = options.blast_tab_output
path = options.path
#names = apply_path(options.path, options.names)
tax_filter_out = options.tax_filter_out
tax_filter_up_to = options.tax_filter_up_to
tax_coloumn = options.tax_coloumn
outfile = options.outfile

taxonomy_filename = os.path.join(path, "nodes.dmp")
if not os.path.isfile(taxonomy_filename):
    sys.stderr.write("Missing %s\n" % taxonomy_filename)
    sys.exit(1)


##################

if not os.path.isfile(blast_tab_output):
    sys.sterr.write("Missing %s input file\n" % blast_tab_output)
    sys.exit(1)

tax_filename = os.path.join(path, "nodes.dmp")
if not os.path.isfile(tax_filename):
    sys.stderr.write("Missing %s\n" % tax_filename)
    sys.exit(1)
    
#TODO - check merged?

#call_function load the tax database info
tax_dictionary = parse_NCBI_nodes_tab_file(path)
#call_function - parse the tab file to get the best non and metazoan hit,
#if defined as such in the tax to use - by default yes
parse_blast_tab_file(blast_tab_output, outfile, tax_filter_out, tax_filter_up_to, tax_coloumn)
#call_function - get precursor vaules to alien score
parse_blast_tab_file_to_get_Alien_precursor_value(outfile, outfile+"_precursor_value.temp")
#call_function - finally get the alien scores
find_true_alien_score(outfile+"_precursor_value.temp", outfile+"_Alien_index.out")

print 'done'
