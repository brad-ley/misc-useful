def statusBar(percent):
    ps = '|' + '='*(int(percent)//2) + '-'*(50 - (int(percent)//2)) + '|'
    if int(percent) == 100:
        print(f"{ps} {percent:.1f}% complete")
    else:
        print(f"{ps} {percent:.1f}% complete", end='\r')

if __name__=="__main__":
    import time
    for ii in range(101):
        time.sleep(1)
        statusBar(ii)
