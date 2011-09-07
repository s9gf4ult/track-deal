#!/bin/bash
### dist-helper.sh --- 


print_usage () {
    cat <<EOF
dist-helper.sh dist {tag-name}
To make tar.bz2 archive of given tag, repository tag must be in commited state

or
dist-helper.sh windist {tag-name}
To make zip archive for windows users
EOF
}

die () {
    echo $1
    exit 1
}

checkout_tag () {
    git checkout $1 || die "Can not checkout tag $1"
}

make_distdirectory () {
    git tag > /dev/null || die "can not do git tag"
    trackname="track-deal-$1"
    mkdir $trackname
    for subdir in `git ls-files --full-name | grep -e '\/' | xargs -l dirname | sort | uniq`;do
        mkdir "$trackname/$subdir" > /dev/null
    done

    for fname in `git ls-files --full-name`;do
        cp "$fname" "$trackname/$fname" > /dev/null
    done
    echo "$trackname"
}

dist_pack () {
    tar -cjvf $1.tar.bz2 $1 || die "Tar executed with errors"
}

windist_pack () {
    7za a -mx=9 $1.zip $1 || die "7za executed with errors or there is no 7zip installed"
}

make_dist () {
    checkout_tag $2
    distdirname=`make_distdirectory $2`
    if [[ "dist" = $1 ]];then
        dist_pack $distdirname
    elif [[ "windist" = $1 ]];then
        windist_pack $distdirname
    fi
    rm -rf $distdirname
}
    

if [[ 2 -ne $# ]];then
    print_usage
    exit 1
fi

if [[ "dist" != $1 ]] && [[ "windist" != $1 ]];then
    print_usage
    exit 1
fi

dist=$1
tagname=$2

if git tag | grep "$tagname" > /dev/null;then
    make_dist  $dist $tagname
else
    die "There is no such tag $tagname"
fi
    