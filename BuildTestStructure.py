'''

This program manually builds the structure that I want the recursive drill fucntion to build.
I only wrote it to try to get my head around what I need to create with the drill function.

The recursive structure is: 

structure = [dirName,[list of directories],[[file1,filesize],[file2,filesize]]

List of directories is a list of structures the same as this (due to the recursion).

Example:

DrillTest
    dir1
        No dirs
        file9, 28 bytes
    dir2
        No dirs
        file4, 0 bytes
        file5, 0 bytes
        file6, 0 bytes
    dir3
        dir5
            file7,    27 bytes
            file7~,    0 bytes
            file8,     0 bytes
        dir6
        dir7
        No files
    dir4
        No dirs
        No files
    file9   28 bytes

We traverse this structure as follows:
    
drill DrillTest
    drill dir1
        create list for directories - []
        create list for files and append file9 - [ [file9,28] ]
        return [ [],[ [file9,28] ] ]
    drill dir2
        create list for directories - []
        create list for files and append list [ [file4,0],[file5,0],[file6,0] ]
        return [[],[ [file4,0],[file5,0],[file6,0]]
        
##
Now the structure looks like this:
    
    [[dir1,[],[file9,28]], [dir2,[],[[file4,0],[file5,0],[file6,0]]

    drill dir3
        create list for directories - []
        drill dir5
            create list for directories - []
                append 

'''
# This is the test structure I put into my home directory. The base directory
# is DrillTest.
#structure = [['dir1',[],[]],['dir2',[],[]],['dir3',['dir5',[],[]],['dir6',[],[]],['dir7',[],[]],['dir4',[],[]]],['file9']]

