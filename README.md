# Pynteny: synteny hmm searches made easy in Python

1. Install environment

conda env create -f environment.yml

# Possible applications:

1. Detect operons in (assembled) environmental samples, MAGs for instance. These operons may be specific of certain taxa, which could lead to taxonomic identification/confirmation besides functional identification.

# Current limitations:
1. If using several, alternative HMMs (for the same gene), pynteny only retains matches


# TODO: 
1. Implement subcommand to download PGAP database and metadata. Also, make hmm databse optional if downloaded.
   PGAP database: https://ftp.ncbi.nlm.nih.gov/hmm/current/hmm_PGAP.HMM.tgz
   PGAP metadata: https://ftp.ncbi.nlm.nih.gov/hmm/current/hmm_PGAP.tsv
2. Double-check final output, some of the hmms in each hmm group may not have returned any hit yet they appear in results (HMM1 | HMM2)
3. Use python logger instead of print statements
