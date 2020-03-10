import os
import glob

print('Methods:\nreplace() -- replaces "print ..." with "print(...)"; can use no args or arg'
      ' with string to be replaced\nInput target directory after running')


def replace(*args):
    if len(args) != 0:
        targ_string = args[0]
    else:
        targ_string = 'print '

    targdir = input('Paste target directory: ')
    goodpath = os.path.abspath(targdir)
    file_list = os.listdir(goodpath)
    # print(file_list)
    for item in file_list:
        if item == os.path.basename(__file__):
            file_list.remove(item)

    for item in file_list:
        if '.py' in item:
            # print(item)
            count = 0
            filetoedit = goodpath + '\\' + item
            file = open(filetoedit, 'r')
            doc = ''
            for line in file:
                line = line.rstrip('\n')

                if targ_string in line.lstrip(' ').lstrip('\t')[:len(targ_string)]:
                    commentpos = line.find('#')

                    if commentpos != -1:
                        comment = line[commentpos:]

                        if line[commentpos + 1] != '#':
                            comment = '#' + comment
                        # if line[commentpos - 1] != ' ':
                        #     comment = ' ' + comment

                        line = line[:commentpos]

                    else:
                        comment = ''

                    print(line)
                    line = line.replace(targ_string, 'print(')  # strings are immutable... duh
                    line = line.rstrip(' ')
                    line = line + ') ' + comment

                    print('newline should be: ' + line)

                    count += 1

                doc = doc + line + '\n'

            file.close()

            newfile = open(goodpath + '\\' + item, 'w')
            newfile.write(doc)
            newfile.close()

            print('Completed for: ' + item + '. Replaced %d occurrences.' % count)

    print('Completed for directory %s.' % goodpath)

