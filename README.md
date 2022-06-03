# Pynteny: synteny hmm searches made easy in Python

1. Genome annotation provided via gbk/gff3 file, via text file with contig/gene info or via prokka if desired and prokaryotic organism

# Possible applications:

1. Detect operons in (assembled) environmental samples, MAGs for instance. These operons may be specific of certain taxa, which could lead to taxonomic identification/confirmation besides functional identification.


# TODO: 
1. If required, export text file with matched reference IDs across HMMs, i.e.,
    ID_a (HMM_a), ID_b (HMM_b), ID_c (HMM_c)