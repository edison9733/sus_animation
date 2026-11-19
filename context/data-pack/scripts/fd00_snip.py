# helper: print context windows around Gambella mentions near flood/drought words (reading aid only)
import sys,re,io
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
W=int(sys.argv[1]); pat=re.compile(sys.argv[2],re.I)
for f in sys.argv[3:]:
    L=open(f,encoding='utf-8',errors='replace').read().splitlines()
    keep=set()
    for i,l in enumerate(L):
        if pat.search(l):
            blk=' '.join(L[max(0,i-W):i+W+1])
            if re.search(r'flood|drought|inundat|overflow|submerg',blk,re.I):
                keep.update(range(max(0,i-W),min(len(L),i+W+1)))
    print('=====',f,len(L))
    prev=None
    for i in sorted(keep):
        if prev is not None and i!=prev+1: print('  ...')
        if L[i].strip(): print(i+1,L[i].strip()[:400])
        prev=i
