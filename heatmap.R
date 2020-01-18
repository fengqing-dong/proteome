
##############################################################
options(warn=-1)
# functions 
############################################################
############################################################
############################################################
#help info
help.info = "
\tA heat map is a false color image (basically image(t(x))) with a dendrogram added to the left side and/or to the top. Typically, reordering of the rows and columns according to some set of values (row or column means) within the restrictions imposed by the dendrogram is carried out.

This heatmap provides a number of extensions to the standard R heatmap function.
"
help.end = "2017 Genechem"
############################################################
############################################################
############################################################
# you should change this part to change the command arguments
#parse args
parseargs = function()
{
    if(!suppressPackageStartupMessages(require("optparse", quietly=TRUE))) {
        stop("the 'optparse' package is needed in order to run this script")
    }
    option_list <-
        list(
            # input file
            make_option(c("-i","--input"), type = "character",default = NULL,help="a character string giving the name of the input table data [default: NULL]"),
            
            # out zscore file
            # make_option(c("-z", "--zscore"), type = "character",default = NULL,help="a character string giving the name of the zscore. [default: NULL]"),
            
            # out picture file
            make_option(c("-o", "--outpath"), type = "character",default = ".",help="a character string giving the name of the output folder [default: NULL]"),
            
            # color used in the heatmap
            make_option(c("-c", "--col"), type = "character",default = "normalcol",help="colors used for the image. Defaults to heat colors (greenred)."),
            
            # the breaks used in draw picture
            make_option(c("--breaks"), type = "integer",default = 100,help="(optional) Either a numeric vector indicating the splitting points for binning x into colors, or a integer number of break points to be used, in which case the break points will be spaced equally between min(x) and max(x). [default: 16]"),
            
            
            make_option(c("--distfun"), type = "character",default = "euclidean",help="the distance measure to be used. This must be one of \"euclidean\", \"maximum\", \"manhattan\", \"canberra\", \"binary\" or \"minkowski\". Any unambiguous substring can be given.[default:euclidean]"),
            
            make_option(c("--hclustfun"), type = "character",default = 'complete',help="the agglomeration method to be used. This should be (an unambiguous abbreviation of) one of \"ward.D\", \"ward.D2\", \"single\", \"complete\", \"average\" (= UPGMA), \"mcquitty\" (= WPGMA), \"median\" (= WPGMC) or \"centroid\" (= UPGMC). [default:complete]")#,

        )
    
    parser <- OptionParser(usage="%prog [options]", option_list=option_list,description=help.info,epilogue=help.end)
    arguments <- parse_args(parser, positional_arguments = TRUE)
    opt <- arguments$options
    arg <- arguments$args
    return(opt)
}
greenblackred = function(n){
	return(colorpanel(n, "green", "black", "red"))
}
redblackgreen = function(n){
	return(colorpanel(n, "red", "black", "green"))
}
normalcol = function(n){
	return(colorpanel(n, "#1864D7", "white", "#CE350F"))
}

# check args
checkarg = function(arg){
    # outtype = c("png","pdf","svg","tif","bmp","jpeg","ps","tiff")
    datatype = c("txt","csv")
    colortype = c("bluered","redblue","redgreen","greenred","heat.colors","rainbow","cm.colors","terrain.colors","greenblackred","redblackgreen","normalcol")#"colorpanel",
    scaletype = c("row","col","none")
    distmethodlist = c("euclidean", "maximum", "manhattan", "canberra", "binary" ,"minkowski")
    clustermethodlist = c("ward", "single", "complete","average", "mcquitty", "median" , "centroid")
    directionlist = c("row","none","both","col")
    # input file draw heatmap
    if(is.null(arg$input)) stop("please give an input file !")
    arg$inputtype = checkfile(arg$input,datatype)
    
    # if(is.null(arg$output)) arg$output = "Heatmap.png"
    # arg$outputtype = checkfile(arg$output,outtype)
    
    # get the zscore type 
    #if(!is.null(arg$zscore)){
    #    arg$zscoretype = checkfile(arg$zscore,datatype)
    #}
    
    # get color type
    arg$col = checklist(arg$col,"greenred",colortype)
    # get color type
    # arg$height = checkvalue(arg$height,4,1,40)
    # get width type
    # arg$width = checkvalue(arg$width,4,1,40)
    # get scale
    arg$scale = checklist(arg$scale,"row",scaletype)
    # sample cluster
    #arg$dendrogram = checklist(arg$dendrogram,"both",directionlist)
    # set dist method
    arg$distfun = checklist(arg$distfun,"euclidean",distmethodlist)
    # set cluster method
    arg$hclustfun = checklist(arg$hclustfun,"complete",clustermethodlist)
	
	# arg$size = 12
	# cex.v = 2*arg$width/3 + 1/3;
	# arg$size = arg$size*cex.v/3;

    return(arg)
}



checkvalue = function(argkey,value,minvalue=NULL,maxvalue=NULL){
    if(is.null(argkey)) argkey = value
    if(!is.null(argkey)){
        if(is.numeric(minvalue) )
            if(argkey < minvalue) stop(paste("please give right value ,the value is smaller than",
                                             minvalue,collapse=","))
        if(is.numeric(maxvalue)) 
            if (argkey > maxvalue) stop(paste("please give right value ,the value is bigger than",
                                              maxvalue,collapse=","))
    }
    return(argkey)
}

checklist = function(argkey,value,valuelist){
    if(is.null(argkey)) argkey = value
    if(!is.null(argkey)){
        if(!(argkey %in% valuelist)) 
            stop(paste("please give right value ,the value can be",paste(
                       valuelist,collapse=",")))
    }
    return(argkey)
}


checkfile = function(filename,typelist){
    if(!is.null(filename)){
        type = rev(strsplit(filename,"\\.")[[1]])[1]
        if(!(type %in% typelist)) 
            stop(paste("please give right file ,the file type can be",paste(
                       typelist,collapse=",")))
    }
    return(type)
}
############################################################
# the txt or csv data
readHeatmapdata <- function(arg){
    filetype = arg$inputtype
    filename = arg$input
    if(is.null(filename)) stop("the input is wrong ,please give a csv file or txt file !")
    data = NULL
    if(filetype == "txt"){
        data = read.table(filename,header=T,row.names=NULL,fill=T,sep="\t",quote="")
        data.head = read.table(filename,header=F,sep="\t",fill=T,row.names = NULL,stringsAsFactors=F,na.strings = "",nrows=1,quote="")
        colnames(data) = data.head[1,]
    }else if(filetype == "csv"){
        data = read.table(filename,header=T,row.names=NULL,fill=T,sep=",",quote="\"")
        data.head = read.table(filename,header=F,sep=",",quote="\"",fill=T,row.names = NULL,stringsAsFactors=F,na.strings = "",nrows=1)
        colnames(data) = data.head[1,]
    }else
    {
        stop("the file type is wrong ,please give a csv file or txt file !")
    }
    # data = as.matrix(data)
    return(data)
}
# min.breaks = max.breaks = tmpbreaks = breaks = 75


Heatmap.main <-function(data,arg){
	myfun = function(){
		mar <- c(3, 2*arg$keywidth, 2, 5*arg$keywidth)
		par(mar = mar, cex = 1, mgp = c(2, 1, 0))
		min.breaks = arg$min.breaks
		max.breaks = arg$max.breaks
		min.raw <- min.breaks
		max.raw <- max.breaks
		z <- seq(min.raw, max.raw, length.out=75)
		col <- get(arg$col, mode = "function")
		image(z = matrix(z, nrow = 1), y=z,col = col(75), xaxt = "n", yaxt = "n",main=NA,ylab=NA,xlab=NA,axes=F)
		bigs = as.integer(min(min.breaks,abs(max.breaks)))
	  idx = c(-1*bigs,0,bigs)
		axis(4,at=idx,labels=idx,las=1,cex=2,tick=F)
	}
    label=NA
	#snames = colnames(data)
	snames = as.character(data[,1])
	#print(head(data))
	#print(head(snames))
	data = as.matrix(data[,-1])
	row.names(data) = snames
	row.len = nrow(data)
	col.len = ncol(data)
	sampleheight = 16
	symbolwidth = 5
	lhei.v = lwid.v = 4
	cex.col = 2
	cex.row = 0.8
    if(arg$showsymbol) {
		label = snames
		sname.max = max(nchar(snames))
		label.max = max(nchar(label))
		if(sname.max > 10) sampleheight = ceiling((sname.max+1)/2+10)
		if(label.max > 10) symbolwidth = ceiling((label.max+1)/2)
		if(row.len > 10){
			# arg$height = arg$height + ((row.len - 10) * 0.3)
			lhei.v = 3.8 + ((row.len -10) * 0.11)
			cex.row = 0.5 + 0.6/log10(row.len)
		}
	}else{
		symbolwidth = 2.1
	}
	if(col.len > 15){
		cex.col = cex.col * 24 / col.len
	}

    clustermethod = function(x)hclust(x,method=arg$hclustfun)
    distmethod = function(x)dist(x,method = arg$distfun)
    
    colmethod =arg$col
	# print(arg$lmat)
	# print(arg$lhei)
	# print(arg$lwid)
    # print(sampleheight)
    hv = heatmap.2(data,trace="none",density.info="none",
                   
                   scale=arg$scale,
                   hclustfun=clustermethod,
                   col=colmethod,
                   dendrogram = arg$dendrogram,
                   breaks=arg$breaks,
                   margins = c(sampleheight,symbolwidth),
                   cexRow = cex.row,
                   cexCol = cex.col,
                   labRow=label,
                   key = FALSE,
                   distfun = distmethod,
                   # lhei = c(1.5,lhei.v),
                   # lwid = c(1.5,lwid.v),
				   # key.title=NA,key.ylab=NA,key.ytickfun=NULL,
				   symkey=F, 
				   # key.par = list(cex=0.4),
				   extrafun=myfun,
				   lmat=arg$lmat,lwid=arg$lwid,lhei=arg$lhei
                   # keysize = 1.5
    )
    
    # output of zscore
    if(!is.null(arg$zscore)){
        outdata = t(hv$carpet)
        outdata = cbind("Symbol"=colnames(hv$carpet),outdata)
        outdata = outdata[nrow(outdata):1,]
        if(arg$zscoretype=="txt"){
            write.table(outdata,file=arg$zscore,row.names=F,col.names=T,sep="\t",quote=FALSE)
        }else if(arg$zscoretype == "csv"){
            write.table(outdata,file=arg$zscore,row.names=F,col.names=T,sep=",",quote=FALSE)
        }else{
            stop("the zscore file you given is wrong ,you should give a csv file or txt file !")
        }
    }
    if(!is.null(arg$symbollist)){
        outdata =data.frame("Symbol"=colnames(hv$carpet))
        outdata = outdata[nrow(outdata):1,]
        if(arg$zscoretype=="txt"){
            write.table(outdata,file=arg$symbollist,row.names=F,col.names=F,sep="\t",quote=FALSE)
        }else if(arg$zscoretype == "csv"){
            write.table(outdata,file=arg$symbollist,row.names=F,col.names=F,sep=",",quote=FALSE)
        }else{
            stop("the zscore file you given is wrong ,you should give a csv file or txt file !")
        }
    }
    return(hv)
}

main = function(arg){
    libs = require("gplots",quietly = T,warn.conflicts = F)
	arg$outpath = gsub("\\\\+","\\/",arg$outpath,perl=T)
	if(!file.exists(arg$outpath)) dir.create(arg$outpath)
	arg$zscore = paste(arg$outpath,"cluster_data.txt",sep="/")
	arg$symbollist = paste(arg$outpath,"cluster_data_list.txt",sep="/")
    data = readHeatmapdata(arg)
	hdata = heatmap.2(as.matrix(data[,-1]), col=greenred(75), scale=arg$scale)
	dev.off()
	tmpbreaks = breaks = 75
	arg$min.breaks = hdata$breaks[1]
	arg$max.breaks = hdata$breaks[length(hdata$breaks)]
	row.len = nrow(data)
	arg$showsymbol = TRUE
	arg$res = 150
	arg$width = 12
	arg$height = 9
	arg$size = 11
	arg$scale = "row"
	arg$keywidth = 2
	arg$zscoretype = "txt"
	arg$dendrogram = "both"
	# print(arg$res)
	# print(arg$size)
	arg$lmat = rbind(c(5,3,0),c(2,1,0),c(2,1,4))
	arg$lhei = c(1.5,1.9 + ((row.len -10) * 0.055),1.9 + ((row.len -10) * 0.055))
	arg$lwid = c(1.5,4,0.1)
	par(family="Helvetica")
	arg$output = paste(arg$outpath,"cluster_heatmap.tiff",sep="/")
    if(arg$showsymbol & row.len > 10) arg$height = 9 + 9 * ((row.len - 10) * 0.14)/7
    	# library(Cairo)
	bitmap(file = arg$output,units="in",res=arg$res,width=arg$width,height = arg$height,pointsize=arg$size)
	# CairoTIFF(filename = arg$output,units="in",res=arg$res,width=arg$width,height = arg$height,pointsize=arg$size)
    Heatmap.main(data,arg)
	dev.off()
	
	arg$lmat = rbind(c(4,3,0),c(2,1,0),c(2,1,5),c(2,1,0))
	arg$lhei = c(1.5,2,2,0.9)
	arg$lwid = c(0.1,4,0.8)
	par("lheight"=0.2) 
	par(family="Helvetica")
	
	arg$keywidth = 1
	arg$showsymbol = FALSE
	arg$zscore = NULL
	arg$symbollist = NULL
	arg$showsymbol = FALSE
	arg$dendrogram = "column"
	arg$output = paste(arg$outpath,"cluster_heatmap_smallsize.png",sep="/")
    arg$height = 9
	png(filename = arg$output,units="in",res=arg$res,width=arg$width,height = arg$height,pointsize=arg$size)
	# print(arg$scale)
    Heatmap.main(data,arg)
	dev.off()
	unlink("Rplots.pdf")
}
############################################################
############################################################
############################################################
############################################################
# parse the args
opt = parseargs()
# print(opt)
opt$scale="row"
# test part
# opt$input = "Heatmap.csv"
#main process
# opt$output = "Heatmap.jpeg"
arg = checkarg(opt)
main(arg)

############################################################
############################################################
############################################################
############################################################
