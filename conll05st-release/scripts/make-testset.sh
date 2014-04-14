#! /bin/tcsh

# sections for training  
set SECTIONS = "wsj brown"

# name of the output file 
set FILE = "test-set" 

foreach s ( $SECTIONS )

    echo Processing section $s

    zcat test.$s/words/test.$s.words.gz > /tmp/$$.words
    zcat test.$s/props/test.$s.props.gz > /tmp/$$.props

    ## Choose syntax
    # zcat test.$s/synt.col2/test.$s.synt.col2.gz > /tmp/$$.synt
    # zcat test.$s/synt.col2h/test.$s.synt.col2h.gz > /tmp/$$.synt
    # zcat test.$s/synt.upc/test.$s.synt.upc.gz > /tmp/$$.synt
    zcat test.$s/synt.cha/test.$s.synt.cha.gz > /tmp/$$.synt

    zcat test.$s/null/test.$s.null.gz > /tmp/$$.senses
    zcat test.$s/ne/test.$s.ne.gz > /tmp/$$.ne

    paste -d ' ' /tmp/$$.words /tmp/$$.synt /tmp/$$.ne /tmp/$$.senses /tmp/$$.props | gzip> /tmp/$$.section.$s.gz
end

echo Generating gzipped file $FILE.gz
zcat /tmp/$$.section* | gzip -c > $FILE.gz

echo Cleaning files
rm -f /tmp/$$*

