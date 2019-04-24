#!/usr/bin/perl

use strict;
use warnings;

use Excel::Writer::XLSX;
use Encode;
#use utf8;
#use Encode::CN;
#use utf8::all;
#use encoding "gbk";
#use encoding "utf-8";
####################################################################
my @infile = ();
my @inparam = ();
my @code = ();
my $outfile = "";
####################################################################

if(scalar @ARGV < 1){
	&help();
	exit;
}
####################################################################
#parse the argv
($outfile ,@infile) = @ARGV;

my $flag = 1;
my %code = (
	"utf8"=>1,
	"ascii"=>1,
	"gbk"=>1,
	"iso-8859-1"=>1,
	"unicode"=>1,
	"gb2312"=>1,
	"big5"=>1,
);
if($outfile =~ /\.txt$/){
	unshift @infile ,$outfile;
	$outfile =~ s/\.txt$/\.xlsx/;
}


for (my $i = 0;$i < scalar @infile ;$i ++) {
	if($infile[$i] =~ /:/){
		my ($file,$param,$code) = split ":",$infile[$i];
		$infile[$i] = $file;
		$inparam[$i] = &getparam($param);
		$code[$i] = $code?$code:"ascii";
		unless($code{$code[$i]}){
			print "encode $code[$i] is not wright ,and it is setted to ascii \n";
			$code[$i] = "ascii";
		}
		unless($inparam[$i]){
			$flag = 0;
			print "The param $param is wrong !";
		}
	}else{
		$inparam[$i] = &getparam();
		$code[$i] = "ascii";
	}
}

# for (my $i = 0;$i < scalar @infile ;$i ++) {
	# unless(-e $infile[$i]){
		# $flag = 0;
		# print "The ".($i+1)." file $infile[$i] is not existed !\n";
	# }
# }
# unless($outfile =~ /.xlsx$/i){
		# $flag = 0;
		# print "The outfile $outfile is not XLSX file !\n";
# }
# unless($flag){
	# exit;
# }
####################################################################
# my %tables = ();
# for (my $i = 0;$i < scalar @infile ;$i ++) {
	# my $name = $infile[$i];
	# $name =~ s/\.txt$//i;
	# $name =~ s/.*\\//g;
	# $name =~ s/.*\///g;
	# if($tables{$name}){
		# print "There are tables have same name !\n";
		# exit;
	# }
	# if(length $name > 20){
		# print "The name of table is bigger than 20 !\n";
		# exit;

	# }
# }
my $workbook = Excel::Writer::XLSX->new($outfile);
my %format = &getformat($workbook);
for (my $i = 0;$i < scalar @infile ;$i ++) {
	my $name = $infile[$i];
	$name =~ s/\.txt$//i;
	$name =~ s/.*\\//g;
	$name =~ s/.*\///g;
	$name =~ s/(.{1,30}).*/$1/;
	my $sheet = $workbook->add_worksheet($name);
	&writesheet($sheet,$infile[$i],$inparam[$i],$code[$i]);
	
}
$workbook->close;
####################################################################
####################################################################
####################################################################
####################################################################
# this method will give help information
sub help{
	print <<__END;
Usage:
	perl TXToXLSX.pl outfile.xlsx infile1.txt[:0,0,0,1,0,6,4:ascii] [infile2.txt[:0,0,0,1,0,6,4:ascii]

	This program will use TXT files to make excel file .the input file 
should be txt file ,and the out file should be xlsx file .
	the args can be given to set excel format.
0	the type fo format ,0 stands for the normal format ,1 stands for write
	with freeze format ,2 stands for write data in one cell merged
0	the first line to write data
0	the first column to write the data
1	counts of lines to be title
0	counts of columns to be freeze column
6	the all lines to be writen ,not include header,-1 stands for all lines
4	the all columns to be writen,-1 stands for all lines
ascii the encode of file ,the file all is ascii default .

#infile.txt
sample	label	sib	group
6481-1	6481-1	1	KD
6481-2	6481-2	2	KD
6481-3	6481-3	3	KD
6482-1	6482-1	1	NC
6482-2	6482-2	2	NC
6482-3	6482-3	3	NC

__END
}

sub getparam{
	my ($param) = @_;
	if($param){
		my @line = split ",",$param;
		my $flag = 1;
		for (my $i = 0;$i < scalar @line ;$i ++) {
			unless($line[$i] =~ /^\d+$/){
				$flag = 0;
			}
		}
		unless($flag){
			return;
		}
		my %res = ();
		$res{type} = $line[0]?$line[0]:0;
		$res{startrow} = $line[1]?$line[1]:0;
		$res{startcol} = $line[2]?$line[2]:0;
		$res{headercounts} = $line[3]?$line[3]:1;
		$res{freezecounts} = $line[4]?$line[4]:0;
		$res{row} = $line[5]?$line[5]:0;
		$res{col} = $line[6]?$line[6]:0;
		return \%res;

	}
	my %res = ();
	$res{type} = 0;
	$res{startrow} = 0;
	$res{startcol} = 0;
	$res{headercounts} = 1;
	$res{freezecounts} = 0;
	$res{row} = -1;
	$res{col} = -1;
	return \%res;
}
sub getdata{
	my ($file,$code) = @_;
	my %res = ();
	$res{row} = 0;
	$res{col} = 0;
	open IN ,$file;
	while (<IN>) {
		$_ = decode $code,$_;
		chomp;
		my @line = split "\t";
		next if(scalar @line < 1);
		if($res{col} == 0){
			$res{col} = scalar @line;
		}
		for (my $i = 0;$i < $res{col} ;$i++) {
			unless(exists $line[$i]){
				$line[$i] = "";
			}else{
				$line[$i] = $line[$i];
			}
		}
		my @ld = @line[0..($res{col}-1)];
		push @{$res{data}},\@ld;
		if(scalar @ld > scalar @line){
			print "The $res{row} row's counts of columns is big than header !\n";
		}
	}
	close IN;
	return \%res;
}



sub getformat{
	my ($workbook) = @_;
	my %format = ();

	my $head = $workbook->add_format(
		font=>'arial',
		text_wrap => 1,
		valign=>'top',
		align=>'center',
		bold =>1,
		bg_color=>"#4F81BD",
		color=>"white",
		border_color=>"white",
		border=>2

	);

	my $readme = $workbook->add_format(
		font=>'arial',
		text_wrap => 1,
		valign=>'top',
		bg_color=>"#DCE6F1" 
	);

	my $de = $workbook->add_format(
		font=>'arial',
		text_wrap => 1,
		valign=>'top',
		align=>'center',
	);
	my $left = $workbook->add_format(
		font=>'arial',
		text_wrap => 1,
		valign=>'top',
		align=>'left',
	);

	$format{'hd'}=$head;
	$format{'rm'}=$readme;
	$format{'c'}=$de;
	$format{'l'}=$left;

	return %format;
}
sub writesheet{
	my ($sheet,$infile,$inparam,$code) = @_;
	my $data = &getdata($infile,$code);
	if($inparam->{type} == 0){
		&writedata($sheet,$data,$inparam);
	}elsif($inparam->{type} == 1){
		&writedata($sheet,$data,$inparam);
		&freezesheet($sheet,$inparam);
	}elsif($inparam->{type} == 2){
		&writemerge($sheet,$data,$inparam);
	}
}
sub writedata{
	my ($sheet,$data,$inparam) = @_;
	my $rows = $inparam->{row}>0?$inparam->{row}:scalar(@{$data->{data}});
	my $cols = $inparam->{col}>0?$inparam->{col}:scalar(@{$data->{data}->[0]});
	my $startrow = $inparam->{startrow};
	my $startcol = $inparam->{startcol};
	my $row = $startrow;
	my $col = $startcol;
	if($rows < 1 || $cols < 1){
		print "The data is not big than 1 column and 1 row !\n";
		return 0;
	}
	if($rows < $inparam->{headercounts}){
		print "The rows data is smaller than header !\n";
		return 0;
	}
	my @data = @{$data->{data}};
	my $head = [];
	for (my $i = 0 ;$i < $inparam->{headercounts} ;$i ++) {
		my $head0 = shift @data;
		if($i == ($inparam->{headercounts} - 1)){
			$head = $head0;
			last;
		}
		#write the head0
		$sheet->write_row($row,$col,$head0,$format{hd});
		$row++;
	}
	#write the head
	$sheet->write_row($row,$col,$head,$format{hd}) if($head);
	$row++ if($head);
	#write the data
	my @collen = split "-","-" x ($rows - 1 );
	for (my $i = 0;$i < $rows;$i ++) {
		my $ld = $data[$i];
		next unless($ld);
		$sheet->write_row($row,$col,$ld);
		$sheet->set_row($row,16);
		$row++;
	}
	if($inparam->{headercounts} > 0){
		my @head;
		for(my $i = 0;$i < scalar @$head ;$i ++){
			$head[$i]={header=>$head->[$i],
						format=> $format{hd}
						};
		}
		my $rowlen = $rows + $startrow + $inparam->{headercounts} - 2;
		my $collen = $cols + $startcol - 1;
		$sheet->add_table($startrow + $inparam->{headercounts} - 1,$startcol,$rowlen,$collen,{ 
			autofilter =>0,
			header_row => 1,
			columns =>\@head,
		});
	}
	for (my $i = $startcol;$i < $cols ;$i++) {
		$sheet->set_column($i,$i,16,$format{c});
	}
	return 1;
}

sub writemerge{
	my ($sheet,$data,$inparam) = @_;
	my $fother = $format{'rm'};
	my $content = "";
	my $startrow = $inparam->{startrow};
	my $startcol = $inparam->{startcol};
	my $row = 0;
	my $col = $startcol+8;
	my @data = @{$data->{data}};
	for (my $i = 0;$i < scalar @data ;$i ++) {
		my $line = (join "    ",@{$data[$i]})."\n";
		my $len = ((length $line) /80);
		$row+= sprintf "%.0f", $len+0.5;
		$content .= $line;
	}
	if($row < 15){
		$row = 15;
	}
	$row = $row + 1;
	chomp $content;
	#$content = decode("gbk",$content); 
	$sheet->merge_range($startrow,$startcol,$row,$col,$content,$fother);
	return 1;
}

sub freezesheet{
	my($sheet,$inparam) = @_;
	my $row = $inparam->{headercounts}+$inparam->{startrow};
	my $col = $inparam->{freezecounts}+$inparam->{startcol};
	if($row + $col < 1){
		print "The freeze cell is not wright !\n";
		return 0;
	}
	$sheet->freeze_panes($row,$col);
	return 1;
}

