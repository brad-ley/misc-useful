import glob
import os


def replace(*args):

    machine = os.name

    if machine == 'posix':
        delim = '/'
    else:
        delim = '\\'

    if len(args) != 0:
        targ_string = args[0]
    else:
        targ_string = 'print '

    targdir = input('Paste target directory or filename: ')

    if targdir.endswith('.py'):
        goodpath = delim.join(os.path.abspath(targdir).split(delim)[:-1])
        file_list = [targdir.split(delim)[-1]]

    else:
        goodpath = os.path.abspath(targdir)
        file_list = os.listdir(goodpath)

    for item in file_list:
        if item == os.path.basename(__file__):
            file_list.remove(item)

    for item in file_list:
        if item.endswith('.py'):
            # print(item)
            count = 0
            filetoedit = goodpath + delim + item
            file = open(filetoedit, 'r')
            doc = ''

            for line in file:
                line = line.rstrip('\n')

                if targ_string in line.lstrip(' ').lstrip(
                        '\t')[:len(targ_string)]:
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
                    # strings are immutable... duh
                    line = line.replace(targ_string, 'print(')
                    line = line.rstrip(' ')
                    line = line + ') ' + comment

                    print('newline should be: ' + line)

                    count += 1

                doc = doc + line + '\n'

            file.close()

            newfile = open(goodpath + delim + item, 'w')
            newfile.write(doc)
            newfile.close()

            print('Completed for: ' + item +
                  '. Replaced %d occurrences.' % count)

    print('Completed for directory %s.' % goodpath)


if __name__ == "__main__":
    replace()
else:
    print('Functions:\nreplace() -- replaces "print ..." with "print(...)";'
          ' can use no args or arg'
          ' with string to be replaced\nInput target directory after running')
