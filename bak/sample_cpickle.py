import cPickle as pkl
import rsTools
reload(rsTools)
from rsTools import AttrDict

#AttrDict is a way to access dictionary like class
d=AttrDict()
d.name='dname'
c=d

# d={'name':'dname'}
# c=d.copy()
#
# size={'x':12,'y':24}
# c['obj']={'size':size}
# c['name']='cname'

#serialize the dictionary to txt file
filename='cPickleTest.sav'
with open(filename,'wb') as fp:
    pkl.dump(c,fp)


#serialize the dic from a txt file
with open(filename,'rb') as fp:
    d1=pkl.load(fp)

print(d1.name)
