def plateau():
    P=[]

     
    ligne=[] #[5,6,7,8,9,8,7,6,5]
    
    for i in range(5,10):
        ligne.append(i)
   
    for j in range(8,4,-1):
        ligne.append(j)


    
    for k in range(len(ligne)):
        P.append([0]*ligne[k])
    
    return P



for ligne in(plateau()):
    print(ligne)



def billes():
    
    P1=plateau()
    
    #ajoute 1 sur les 3 premieres lignes: joueur 1
    for i in range(0,2):
        for j in range(len(P1[i])):
            P1[i][j]=1


    debut_3_j1=len(P1[2])//2
    for x in range(debut_3_j1-1, debut_3_j1+2):
        P1[2][x]=1


    #ajoute 2 sur les 3 dernieres lignes: joueur 2
    for m in range(7,9):
        for k in range(len(P1[m])):
            P1[m][k]=2


    debut_3_j2=len(P1[6])//2
    for y in range(debut_3_j2-1,debut_3_j2+2):
        P1[6][y]=2


    return P1



for ligne in(billes()):
    print(ligne)
    
    
    
    