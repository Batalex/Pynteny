#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tools to create peptide-specific sequence databases

1. Implement hmmr
2. Filter fasta files based on query sequences
"""

from __future__ import annotations
import os
from collections import defaultdict

import pandas as pd
from Bio import SearchIO
import pyfastx

import pynteny.wrappers as wrappers
from pynteny.utils import setDefaultOutputPath



class LabelParser():
    """
    Parse entry label to extract coded info
    """
    @staticmethod
    def parse(label: str) -> dict:
        """
        Parse sequence labels to obtain contig and locus info
        """
        parsed_dict = {
            'full': label,
            'gene_id': '',
            'contig': '',
            'gene_pos': None,
            'locus_pos': None,
            'strand': ''
            } 
        try: 
            entry = label.split('__')[0]
            meta = label.split('__')[1]
            strand = meta.split('_')[-1]
            locus_pos = tuple([int(pos) for pos in meta.split('_')[-3:-1]])
            gene_pos = int(meta.split('_')[-4])
            contig = '_'.join(meta.split('_')[:-4])

            parsed_dict['gene_id'] = entry
            parsed_dict['contig'] = contig
            parsed_dict['gene_pos'] = gene_pos 
            parsed_dict['locus_pos'] = locus_pos
            parsed_dict['strand'] = strand
        except Exception:
            pass
        return parsed_dict
    
    @staticmethod
    def parse_from_list(labels=list) -> pd.DataFrame: 
        """
        Parse labels in list of labels and return DataFrame
        """
        return pd.DataFrame(
            [LabelParser.parse(label) for label in labels]
        )


class SyntenyParser():
    """
    Tools to parse synteny structure strings
    """
    @staticmethod
    def splitStrandFromLocus(locus_str: str) -> tuple[str]:
        locus_str = locus_str.strip()
        if locus_str[0] == '<' or locus_str[0] == '>':
            sense = locus_str[0]
            locus_str = locus_str[1:]
            strand = 'pos' if sense == '>' else 'neg'
        else:
            strand = None
        return (strand, locus_str)

    @staticmethod
    def getHMMsInStructure(synteny_structure: str) -> list[str]:
        """
        Get hmm names employed in synteny structure
        """
        links = synteny_structure.strip().split()
        if not links:
            raise ValueError("Invalid format for synteny structure")
        return [
            SyntenyParser.splitStrandFromLocus(h)[1] 
            for h in links if not h.isdigit()
            ]

    @staticmethod
    def getStrandsInStructure(synteny_structure: str) -> list[str]:
        """
        Get strand sense list in structure
        """
        links = synteny_structure.strip().split()
        if not links:
            raise ValueError("Invalid format for synteny structure")
        return [
            SyntenyParser.splitStrandFromLocus(h)[0] 
            for h in links if not h.isdigit()
            ]

    @staticmethod
    def getMaximumDistancesInStructure(synteny_structure: str) -> list[int]:
        """
        Get maximum gene distances in structure
        """
        links = synteny_structure.strip().split()
        return [int(dist) for dist in links if dist.isdigit()]

    @staticmethod
    def parseSyntenyStructure(synteny_structure: str) -> dict:
        """
        Parse synteny structure string. A synteny structure
        is a string like the following:

        >hmm_a n_ab <hmm_b n_bc hmm_c

        where '>' indicates a hmm target located on the positive strand,
        '<' a target located on the negative strand, and n_ab cooresponds 
        to the maximum number of genes separating matched gene a and b. 
        Multiple hmms may be employed (limited by computational capabilities).
        No order symbol in a hmm indicates that results should be independent
        of strand location.
        """
        max_dists = SyntenyParser.getMaximumDistancesInStructure(synteny_structure)
        hmms = SyntenyParser.getHMMsInStructure(synteny_structure)
        strands = SyntenyParser.getStrandsInStructure(synteny_structure)
        return {"hmms": hmms, "strands": strands, "distances": max_dists}


class SyntenyPatternFilters():
    def __init__(self, synteny_structure: str) -> None:
        parsed_structure = SyntenyParser.parseSyntenyStructure(synteny_structure)
        hmm_order_dict = dict(
            zip(parsed_structure["hmms"], range(len(parsed_structure["hmms"])))
            )
        hmm_codes = list(hmm_order_dict.values())
        self.hmm_code_order_pattern = hmm_codes
        parsed_distances = [float("inf")] + parsed_structure["distances"]
        self.distance_order_pattern = [dist + 1 for dist in parsed_distances]
        self.strand_order_pattern = list(map(
            lambda strand : -1 if strand == "neg" else (1 if strand ==  "pos" else 0),
            parsed_structure["strands"]
            ))

    def contains_hmm_pattern(self, data: pd.Series) -> int:
        return 1 if data.values.tolist() == self.hmm_code_order_pattern else 0

    def contains_distance_pattern(self, data: pd.Series) -> int:
        return 1 if all(
            [
                (data_dist <= pattern_dist) and (data_dist > 0)
                for data_dist, pattern_dist in zip(data.values.tolist(), self.distance_order_pattern)
            ]
            ) else 0

    def contains_strand_pattern(self, data: pd.Series) -> int:
        strand_comparisons = []
        for data_strand, pattern_strand in zip(data.values, self.strand_order_pattern):
            if pattern_strand != 0:
                strand_comparisons.append(data_strand == pattern_strand)
            else:
                strand_comparisons.append(True)
        return 1 if all(strand_comparisons) == True else 0   


class SyntenyHMMfilter():
    """
    Tools to search for synteny structures among sets of hmm models
    """
    def __init__(self, hmm_hits: dict, synteny_structure: str) -> None:
        """
        Search for contigs that satisfy the given gene synteny structure

        @param: hmm_hits, a dict of pandas DataFrames, as output by
                parseHMMsearchOutput with keys corresponding to hmm names
        """
        self._hmm_hits = hmm_hits
        self._n_hmms = len(hmm_hits)
        self._hmms = list(hmm_hits.keys())
        self._synteny_structure = synteny_structure
        self._parsed_structure = SyntenyParser.parseSyntenyStructure(self._synteny_structure)
        self._hmm_order_dict = dict(
            zip(self._parsed_structure["hmms"], range(len(self._parsed_structure["hmms"])))
            )

    def getAllHMMhits(self) -> pd.DataFrame:
        """
        Group and preprocess all hit labels into a single dataframe
        """
        hit_labels = {}
        labelparser = LabelParser()
        for hmm, hits in self._hmm_hits.items():
            labels = hits.id.values.tolist()
            if not labels:
                raise ValueError(
                    f'No records found in database matching HMM: {hmm}'
                    )
            hit_labels[hmm] = labelparser.parse_from_list(labels)
            hit_labels[hmm]["hmm"] = hmm

        # Create single dataframe with new column corresponding to HMM and all hits
        # Remove contigs with less hits than the number of hmms in synteny structure
        all_hit_labels = pd.concat(
            hit_labels.values()
            ).groupby("contig").filter(
                lambda x : len(x) >= self._n_hmms
                ).sort_values(["contig", "gene_pos"])
        # Drop sequences hit by more than one hmm
        all_hit_labels = all_hit_labels.drop_duplicates(
            subset=all_hit_labels.columns.difference(["hmm"]), keep=False)
        all_hit_labels.reset_index(drop=True, inplace=True)
        return self._addMetaInfoToHMMhits(all_hit_labels)
    
    def _addMetaInfoToHMMhits(self, all_hit_labels: pd.Dataframe) -> pd.Dataframe:
        """
        Add numeric codes for each hmm and strand, compute distance between genes
        """
        all_hit_labels["gene_pos_diff"] = all_hit_labels.gene_pos.diff()
        all_hit_labels.loc[0, "gene_pos_diff"] = 1 # required for rolling (skips first nan)
        all_hit_labels["hmm_code"] = all_hit_labels.hmm.apply(
            lambda hmm: self._hmm_order_dict[hmm]
            )
        all_hit_labels["strand"] = all_hit_labels.strand.apply(
            lambda strand: -1 if strand == "neg" else 1
            )
        return all_hit_labels

    def _writeAllHitsToTSV(self, all_matched_hits: dict, output_file: str) -> None:
        """
        Write hits matching synteny structure to TSV file
        """
        output_lines = []
        for contig, matched_hits in all_matched_hits.items():
            for hmm, labels in matched_hits.items():
                for label in labels:
                    parsed_label = LabelParser.parse(label)
                    output_lines.append(
                        (
                            f"{parsed_label['contig']}\t{parsed_label['gene_id']}\t"
                            f"{parsed_label['gene_pos']}\t{parsed_label['locus_pos']}\t"
                            f"{parsed_label['strand']}\t{hmm}\t{parsed_label['full']}\n"
                            )
                    )
        with open(output_file, "w") as outfile:
            outfile.write("contig\tgene_id\tgene_number\tlocus\tstrand\tHMM\tfull_label\n")
            outfile.writelines(output_lines)
        return None

    def filterHitsBySyntenyStructure(self, output_tsv: str = None) -> pd.DataFrame:
        """
        Search for contigs that satisfy the given gene synteny structure
        @param: synteny_structure, a str describing the desired synteny structure,
                structured as follows:

                'hmm_a N_ab hmm_b'

                where N_ab corresponds to the maximum number of genes separating 
                gene found by hmm_a and gene found by hmm_b, and hmm_ corresponds 
                to the name of the hmm as provided in the keys of hmm_hits.
                More than two hmms can be concatenated.
        """
        all_matched_hits = {}
        filters = SyntenyPatternFilters(self._synteny_structure)
        all_hit_labels = self.getAllHMMhits()
        contig_names = all_hit_labels.contig.unique()

        for contig in contig_names:

            matched_hit_labels = {hmm: [] for hmm in self._hmms}
            contig_hits = all_hit_labels[all_hit_labels.contig == contig].reset_index(drop=True)

            if len(contig_hits.hmm.unique()) == self._n_hmms:
                
                hmm_match = contig_hits.hmm_code.rolling(window=self._n_hmms).apply(
                    filters.contains_hmm_pattern
                    )
                strand_match = contig_hits.strand.rolling(window=self._n_hmms).apply(
                    filters.contains_strand_pattern
                    )
                if self._n_hmms > 1:
                    distance_match = contig_hits.gene_pos_diff.rolling(
                        window=self._n_hmms).apply(filters.contains_distance_pattern)
                    matched_rows = contig_hits[
                        (hmm_match == 1) &
                        (strand_match == 1) &
                        (distance_match == 1)
                    ]
                else:
                    matched_rows = contig_hits[
                        (hmm_match == 1) &
                        (strand_match == 1)
                    ]

                for i, row in matched_rows.iterrows():
                    matched_hits = contig_hits.iloc[i - (self._n_hmms - 1): i + 1, :]
                    for label, hmm in zip(matched_hits.full.values, matched_hits.hmm):
                        matched_hit_labels[hmm].append(label)

                all_matched_hits[contig] = matched_hit_labels
        if output_tsv is not None:
            self._writeAllHitsToTSV(all_matched_hits, output_file=output_tsv)
        return all_matched_hits


def parseHMMsearchOutput(hmmer_output: str) -> pd.DataFrame:
    """
    Parse hmmsearch or hmmscan summary table output file
    """
    attribs = ['id', 'bias', 'bitscore', 'description']
    hits = defaultdict(list)
    with open(hmmer_output) as handle:
        for queryresult in SearchIO.parse(handle, 'hmmer3-tab'):
            for hit in queryresult.hits:
                for attrib in attribs:
                    hits[attrib].append(getattr(hit, attrib))
    return pd.DataFrame.from_dict(hits)

def filterFASTAbyIDs(input_fasta: str, record_ids: list,
                     output_fasta: str = None) -> None:
    """
    Filter records in fasta file matching provided IDs
    """
    if output_fasta is None:
       output_fasta = setDefaultOutputPath(input_fasta, '_fitered')
    record_ids = set(record_ids)
    fa = pyfastx.Fasta(input_fasta)
    with open(output_fasta, 'w') as fp:
        for record_id in record_ids:
            try:
                record_obj = fa[record_id]
                fp.write(record_obj.raw)
            except:
                pass
    os.remove(input_fasta + ".fxi")

def filterFASTABySyntenyStructure(synteny_structure: str,
                                  input_fasta: str,
                                  input_hmms: list[str],
                                  output_dir: str = None,
                                  output_prefix: str = None,
                                  hmmer_output_dir: str = None,
                                  reuse_hmmer_results: bool = True,
                                  method: str = 'hmmsearch',
                                  additional_args: list[str] = None) -> None:
    """
    Generate protein-specific database by filtering sequence database
    to only contain sequences which satisfy the provided (gene/hmm)
    structure
    
    @Arguments:
    additional_args: additional arguments to hmmsearch or hmmscan. Each
    element in the list is a string with additional arguments for each 
    input hmm (arranged in the same order), an element can also take a 
    value of None to avoid passing additional arguments for a specific 
    input hmm. A single string may also be passed, in which case the 
    same additional argument is passed to hmmsearch for all input hmms
    """
    if hmmer_output_dir is None:
        hmmer_output_dir = os.path.join(
            setDefaultOutputPath(input_fasta, only_dirname=True), 'hmmer_outputs')
    
    if output_prefix is None:
        output_prefix = ""
        
    if additional_args is None:
        additional_args = [None for _ in input_hmms]
    
    if type(additional_args) == str:
        additional_args = [additional_args for _ in input_hmms]

    elif type(additional_args) == list:
        if len(additional_args) == 1:
            additional_args = [additional_args[0] for _ in input_hmms]

        if (len(additional_args) > 1) and (len(additional_args) < len(input_hmms)):
            raise ValueError("Provided additional argument strings are less than the number of input hmms.")
    else:
        raise ValueError('Additional arguments must be: 1) a list[str], 2) a str, or 3) None')
    if not os.path.isdir(hmmer_output_dir):
        os.mkdir(hmmer_output_dir)
    
    if output_dir is None:
        output_dir = setDefaultOutputPath(input_fasta, only_dirname=True)
    else:
        output_dir = output_dir

    results_table = os.path.join(output_dir, f"{output_prefix}synteny_matched.tsv")

    print('Running Hmmer...')
    hmm_names, hmm_hits = [], {}
    for hmm_model, add_args in zip(input_hmms, additional_args):
        hmm_name, _ = os.path.splitext(os.path.basename(hmm_model))
        hmmer_output = os.path.join(hmmer_output_dir, f'hmmer_output_{hmm_name}.txt')
        hmm_names.append(hmm_name)

        if not (reuse_hmmer_results and os.path.isfile(hmmer_output)):
            wrappers.runHMMsearch(
                hmm_model=hmm_model,
                input_fasta=input_fasta,
                output_file=hmmer_output,
                method=method,
                additional_args=add_args
                )
        elif reuse_hmmer_results and os.path.isfile(hmmer_output):
            print(f"Reusing Hmmer results for HMM: {hmm_name}")

        hmm_hits[hmm_name] = parseHMMsearchOutput(hmmer_output)

    print('Filtering results by synteny structure...')
    syntenyfilter = SyntenyHMMfilter(hmm_hits, synteny_structure)
    matches = syntenyfilter.filterHitsBySyntenyStructure(
        output_tsv=results_table
        )
    print("Writing matching sequences to FASTA files...")
    df = pd.read_csv(results_table, sep="\t")
    for hmm_name in hmm_names:
        record_ids = df[df.HMM == hmm_name].full_label.values.tolist()
        if record_ids:
            filterFASTAbyIDs(
                input_fasta=input_fasta,
                record_ids=record_ids,
                output_fasta=os.path.join(output_dir, f"{output_prefix}{hmm_name}_hits.fasta")
            )
        else:
            print(f"No record matches found in synteny structure for HMM: {hmm_name}")