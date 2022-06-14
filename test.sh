# Example with E. coli MG1655
# https://biocyc.org/ECOLI/NEW-IMAGE?type=LOCUS-POSITION&object=NIL&chromosome=COLI-K12&orgids=ECOLI&bp-range=70001/120000
#
# leuA -> TIGR00973.1
# leuB > TIGR00169.1
# leuC -> TIGR00170.1
# leuD -> TIGR00171.1
# setA-> TIGR00899.1
#
# > setA 1 < leuD < leuC < leuB < leuA 



# python synteny_search.py \
#  --hmm_dir /home/robaina/Databases/hmm_PGAP/ \
#  --in /home/robaina/Documents/Pynteny/tests/MG1655.fasta \
#  --outdir /home/robaina/Documents/Pynteny/tests/MG1655_results \
#  --synteny_struc "TIGR00899.1 0 TIGR00171.1 0 TIGR00170.1 1 TIGR00973.1"



python translate_assembly.py \
 --assembly_fasta /home/robaina/Databases/MAR_database/marref_assembly_V6.fa \
 --outdir /home/robaina/Databases/MAR_database/ \
 --prefix "marref_V6_" \
 --processes 7 \
 --split_contigs

# python synteny_search.py \
#  --hmm_dir /home/robaina/Databases/hmm_PGAP/ \
#  --in /home/robaina/Databases/MarRef_1.7/marref_prodigal_longlabels.faa \
#  --outdir /home/robaina/Documents/Pynteny/tests/test_results \
#  --prefix "test_" \
#  --synteny_struc "<TIGR00899.1" # 0 <TIGR00171.1 0 <TIGR00170.1 1 <TIGR00973.1"