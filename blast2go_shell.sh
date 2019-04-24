#usage : bash ./blast2go_shell.sh query.fasta uniprot-reviewed%3Ayes+taxonomy%3A9606.fasta  query_988
#!/bin/bash
query=$1 #input query fasta file
file_list=(${query//\// })
query2=${file_list[-1]}


blast_db=$2 #blast database 
#diff_id=$3 #input project diff_id number
outfile_name=$3 #output name
interproscan="/home/lijuan.chen/blast2go_commandline/my_interproscan/interproscan-5.30-69.0"
blast="/home/lijuan.chen/blast2go_commandline/ncbi-blast-2.3.0+/bin/blastp"
output="/home/lijuan.chen/blast2go_commandline/blast2go_cli_v1.3.3"
outdir=$output/$outfile_name
#echo $outdir
mkdir -p $outdir
perl_cmd="/home/lijuan.chen/blast2go_commandline/blast2go_cli_v1.3.3/perl_command"

$blast -query $query -db  /home/lijuan.chen/blast2go_commandline/ncbi-blast-2.3.0+/bin/$blast_db -out $outdir/blast.xml -outfmt "5" -evalue 1e-3 -num_alignments 10 -show_gis

$interproscan/interproscan.sh -i $query -f XML -b  $outdir/interproscan

$output/blast2go_cli.run -properties $output/cli.prop -loadfasta $query -useobo /home/fdong/auto_protein_analysis/go_obo_data/go_lastest.obo -loadblast $outdir/blast.xml  -loadips50 $outdir/interproscan.xml  \
 -mapping -annotation -annex -saveb2g $outdir/$query2.b2g -protein -saveannot $outdir/$query2.annot  \
-exportgeneric $outdir/blast_top_hit.txt

#perl $perl_cmd/diff_twotext.pl $output/diff_id.txt $outdir/blast_top_hit.txt $outdir/top_blast.txt

#perl $perl_cmd/diff_twotext.pl $output/diff_id.txt $outdir/$query.annot $outdir/diff.annot

#perl $perl_cmd/protein2go_new.pl $outdir/diff.annot $outdir/protein2go.txt $outdir/protein2go.txt $outdir/go.annot

# tar cvf $query.tar $outdir
# mv $query.tar /project 
# rm $outdir
