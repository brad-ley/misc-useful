def statusBar(percent):
    ps = '|' + '='*(percent//2) + '-'*(50 - (percent//2)) + '|'
    if percent == 100:
        print(f"{ps} {percent}% complete")
    else:
        print(f"{ps} {percent}% complete", end='\r')

if __name__=="__main__":
    import time
    for ii in range(101):
        time.sleep(1)
        statusBar(ii)
