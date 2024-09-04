from time import time_ns
from copy import deepcopy
from tkinter import *
from tkinter import font

tableau_analyse = """
                            
                            ---      Analyse Des Résultats     -----
                            
              +---------------+---------------+-
              |      A*       | hill climbing |                              
+-------------+---------------+---------------+-
| Nb Visités |{nbVisitesA:03d}|{nbVisitesHC:03d}|               
+-------------+---------------+---------------+-
| Nb générés  |{nbEtatsA:03d} |{nbEtatsHC:03d}|               
+-------------+---------------+---------------+-
|   Temps     |               |               |                              
| d'Exécution |{tempsA:08d}   |{tempsHC:08d}  |                              
|   en Nano   |               |               |                              
|   Secondes  |               |               |                              
+-------------+---------------+---------------+ 
"""
#fih touskie comparaison mtaa les deux algo 


idx = 0

etat_depart = [
    [1, 2, 3],
    [8, 6, 0],
    [7, 5, 4]
]

etat_final = [
    [1, 2, 3],
    [8, 0, 4],
    [7, 6, 5]
]

def arrowDown(m):
    canvas = Canvas(m, width=10, height = 50)
    canvas.pack()
    canvas.create_line(5, 0, 5, 50, arrow = LAST, fill = "red")

def estEtatFinal(t, goal):
    return True if (t == goal) else False

def numero(t, x, y):
    return t[x][y]

def position_case_vide(t):
    for x in range(3):
        for y in range(3):
            if (numero(t, x, y) == 0):
                return (x, y)

def permuter(t, c1, c2):
    tp = deepcopy(t)
    x1, y1, x2, y2 = c1 + c2
    tp[x1][y1], tp[x2][y2] = tp[x2][y2], tp[x1][y1]
    return tp

def transitions(etat):
    etats = []

    xv, yv = position_case_vide(etat)
    haut, bas, gauche, droite = xv - 1, xv + 1, yv - 1, yv + 1

    if (haut >= 0):
        etats.append(permuter(etat, (haut, yv), (xv, yv)))
    if (bas <= 2):
        etats.append(permuter(etat, (bas, yv), (xv, yv)))
    if (droite <= 2):
        etats.append(permuter(etat, (xv, droite), (xv, yv)))
    if (gauche >= 0):
        etats.append(permuter(etat, (xv, gauche), (xv, yv)))

    return etats

def afficher_taquin(t):
    if (mode == "terminal"):
        print("+---+---+---+") 
        for x in range(3):
            print(f"| {t[x][0]} | {t[x][1]} | {t[x][2]} |")
            print("+---+---+---+") 
    else:
        pass

def afficher_chemin(chemin, success):
    for etat in chemin:
        afficher_taquin(etat[0])
        print(" " * 6 + "|")
        print(" " * 6 + "\u25bc")
    if (success):
        print(" " * 4 + "Succès")
    else:
        print(" " * 4 + "Échec")

def afficherEtatGraphique(m, etat):
    state = Frame(m)
    state.pack()
    arrowDown(state)
    afficher_taquin_graphique(state, etat)



def recherche(s0, goal):
    closelist = set()
    current_state = s0
    success = False
    steps = [(current_state, 0)]  # Tuple (état, niveau)

    niveau = 0

    while not success:
        neighbors = transitions(current_state)
        best_neighbor = None
        best_heuristic = float("inf")

        for neighbor in neighbors:
            if tuple(map(tuple, neighbor)) in closelist:
                continue  # Skip already visited states

            if estEtatFinal(neighbor, goal):
                success = True
                best_neighbor = neighbor
                steps.append((best_neighbor, niveau + 1))
                break

            heuristic = sum(
                1 for x in range(3) for y in range(3) 
                if neighbor[x][y] != goal[x][y] and neighbor[x][y] != 0
            )

            if heuristic < best_heuristic:
                best_heuristic = heuristic
                best_neighbor = neighbor

        if best_neighbor is None:
            break

        current_state = best_neighbor
        closelist.add(tuple(map(tuple, current_state)))
        steps.append((current_state, niveau + 1))
        niveau += 1

    return current_state, success, steps




def recherche_A_etoile(s0, goal):
    # le cout de chaque transition est de 1 donc on n'aura pas a calculer les couts pour trier les transitions
    freeNodes = [(s0, 0, 0)] # on enregistre les couples (etat, niveau, f) avec f est le résultat de la fonction heuristique
    closedNodes = []
    success = False

    while (freeNodes):
        etat_courant, niveau, _ = min(freeNodes, key = lambda node: node[2])
        closedNodes.append((etat_courant, niveau))
        freeNodes.remove((etat_courant, niveau, _))

        if (estEtatFinal(etat_courant, goal)):
            success = True
            break

        generatedStates = transitions(etat_courant)
        tocheckStates = deepcopy(generatedStates)

        for etat in tocheckStates:
            if (any(node[0] == etat for node in freeNodes) or any(etat == node[0] for node in closedNodes)):
                generatedStates.remove(etat)

        # h = len(closedNodes) est le nombre de jetons déplacés
        # g = la somme des 1 dont la case est différente de la cause du taquin final est le nombre de jetons mal placés
        for etat in generatedStates:
            f = (sum(1 for x in range(3) for y in range(3) if etat[x][y] != goal[x][y] and etat[x][y] != 0) + len(closedNodes))
            freeNodes.append((etat, niveau + 1, f))
        
    return closedNodes, len(closedNodes + freeNodes), len(closedNodes), success

def clearScreen(m):
    for child in m.winfo_children():
        if (child == exitButton):
            continue
        child.destroy()

def rechercheGraphique(m, rech, back = False):
    global idx

    if (back and (idx <= 1)):
        return

    chemins = {
        "hill_climbing": cheminhill,
        "A*": cheminA
    }

    if (back):
        idx -= 1
    elif (idx < (len(chemins[rech]) - 1)):
        idx += 1
    else:
        return

    etat, niveau = chemins[rech][idx]

    if (rech not in ["hill_climbing"]):
        if (back):
            nv_preced = chemins[rech][idx + 1][1]
            if (niveau < nv_preced):
                for i in range(2):
                    m.winfo_children()[-1].destroy()
            elif (niveau > nv_preced):
                path = [etat]
                for i in range(idx - 1, 0, -1):
                    if (chemins[rech][i][1] < niveau):
                        path.insert(0, chemins[rech][i][0])
                        niveau = chemins[rech][i][1]

                m.winfo_children()[-1].destroy()
                
                for etat in path:
                    afficherEtatGraphique(m, etat)

                return
            else:
                m.winfo_children()[-1].destroy()
        elif (1 < idx):
                nv_preced = chemins[rech][idx - 1][1]
                if (niveau <= nv_preced):
                    for i in range(nv_preced - niveau + 1):
                        m.winfo_children()[-1].destroy()
        else:
            m.winfo_children()[-1].destroy()
    else:
        m.winfo_children()[-1].destroy()

    afficherEtatGraphique(m, etat)

def afficher_taquin_graphique(m, t):
    f = Frame(m)
    f.pack(pady = 4, padx = 4)

    for x in range(3):
            for y in range(3):
                label = Label(f, text = (t[x][y] if (t[x][y] != 0) else ''), width = 5, height = 2, borderwidth = 2, relief = "solid", bg = ("#C19A6B" if (t[x][y] != 0) else "#EADDCA"), fg = "#333333", highlightbackground = "#cccccc")
                label.grid(row = x, column = y)

def handlerGraphique(m, rech):
    global idx

    idx = 0
    clearScreen(m)

    menuButton = Button(m, text="Menu", command=lambda: menu_graphique(m), fg="white", bg="red", width=10)
    menuButton.pack(anchor="se", side="bottom", padx=10, pady=10, ipadx=5, ipady=5)

    if (rech == "analyse"):
        tableau = Label(m, text=tableau_analyse.format(nbVisitesDFS=nbVisitesDFS, nbVisitesDFSL=nbVisitesDFSL,
                                                       nbVisitesBFS=nbVisitesBFS, nbVisitesA=nbVisitesA,
                                                       nbEtatsDFS=nbEtatsDFS, nbEtatsDFSL=nbEtatsDFSL,
                                                       nbEtatsBFS=nbEtatsBFS, nbEtatsA=nbEtatsA, tempsDFS=tempsDFS,
                                                       tempsDFSL=tempsDFSL, tempsBFS=tempsBFS, tempsA=tempsA),
                        fg="#5C4033")
        tableau.place(relx=0.5, rely=0.5, anchor="center")
        return

    t = Label(m, text="Etat Initial")
    t.pack()
    afficher_taquin_graphique(m, etat_depart)

    frameB = Frame(m)
    frameB.place(relx=0.5, rely=0.95, anchor="center")

    nextB = Button(frameB, text="Précédent", width=13, fg="white", bg="red", padx=10,
                   command=lambda: rechercheGraphique(m, rech, True))
    nextB.grid(row=1, column=0)
    prevB = Button(frameB, text="Suivant", width=13, fg="white", bg="red", padx=10,
                   command=lambda: rechercheGraphique(m, rech))
    prevB.grid(row=1, column=1)

    afficherEtatGraphique(m, etat_depart)


def menu():
    print("1) Mode Terminal")
    print("2) Mode Graphique")
    print("99) Quit")

def menu_graphique(m):
    clearScreen(m)
    
    menuFrame = Frame(m)
    menuFrame.place(relx = 0.5, rely = 0.5, anchor = "center")

    t = Label(menuFrame, text = "Etat Initial")
    t.pack()

    afficher_taquin_graphique(menuFrame, etat_depart)

    arrowDown(menuFrame)
    
    t = Label(menuFrame, text = "Etat Final")
    t.pack(pady = 10)

    afficher_taquin_graphique(menuFrame, etat_final)

    rechhillclimbing = Button(menuFrame, text = "Recherche en hill climbing ", fg = "white", bg = "#C19A6B", width = 40, command = lambda: handlerGraphique(m, "hill_climbing"))
    rechhillclimbing.pack(pady = (40, 3))
    rechAStar = Button(menuFrame, text = "Recherche en A*", fg = "black",width = 40, bg = "#EADDCA", command = lambda: handlerGraphique(m, "A*"))
    rechAStar.pack(pady = 3)
    compare = Button(menuFrame, text = "Analyser les Diffèrents Algorithmes", width = 40, bg = "#C1916B", fg = "white", command = lambda: handlerGraphique(m, "analyse"))
    compare.pack(pady = 3)



if (__name__ == "__main__"):
    mode = "terminal"
    mode = "graphique"
    while (True):
        menu()
        try:
            mode = int(input("> "))
            if (mode == 1):
                mode = "terminal"
                break
            elif (mode == 2):
                mode = "graphique"
                break
            elif (mode == 99):
                print("Au revoir!")
                break
            else:
                print("Il faut saisir '1' ou '2' ou '99' comme input!")
        except:
            print("Il faut saisir un entier!")

    if (mode == 99):
        exit(0)
    # recherche en hill climbing 
    debut = time_ns()
    nbVisitesDFS, successDFS, cheminhill = recherche(etat_depart, etat_final)
    fin = time_ns()
    tempsDFS = fin - debut

    # recherche heuristique avec la solution A*
    debut = time_ns()
    cheminA, nbEtatsA, nbVisitesA, successA = recherche_A_etoile(etat_depart, etat_final)
    fin = time_ns()
    tempsA = fin - debut

    if (mode == "terminal"):
        afficher_chemin(cheminhill, successDFS)

        input("Appuyez sur ENTRER pour exécuter la recherche heuristique avec A*...")

        afficher_chemin(cheminA, successA)

    else:
        m = Tk(className = "Solutions AI - Jeu De Taquin")
        m.attributes("-fullscreen", True)
        defaultFont = font.nametofont("TkDefaultFont")
        defaultFont.configure(size = 12, family = "Terminal")

        exitButton = Button(m, text = "Quitter", command = m.destroy, fg = "white", bg = "red", width = 10)
        exitButton.pack(anchor = "se", side = "bottom", padx = 10, pady = 10, ipadx = 5, ipady = 5)

        menu_graphique(m)


        m.mainloop()
