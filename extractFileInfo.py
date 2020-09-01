def get(string, *args, delimiter='_'):
    """
    Input a string that is separated by delimeter. Function will return the
    data near the keyword. User may give a list of keywords as [key1, key2, .., keyn]
    and results will be returned in requested order.

    Example usage: get(testfile_45DA_68fun.txt, 'DA') = 45
    """
    for keyword in args:
        zero = ''.join([ii for ii in string.split(delimiter) if keyword in ii])

        if not zero:
            zero = ''.join([
                ii for ii in string.split(delimiter)
                if keyword.lower() in ii.lower()
            ])
        one = ''.join([ch for ch in zero if ch.isdigit() or ch == '.'])

        try:
            one = float(one)

            if int(one) == one:
                one = int(one)
        except ValueError:
            pass

        if one == '':
            one = 'none'

        yield one
